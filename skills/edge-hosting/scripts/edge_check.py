#!/usr/bin/env python3
import argparse
import datetime
import http.client
import json
import re
import secrets
import socket
import ssl
import sys
import time
import tomllib
import urllib.parse
from dataclasses import asdict, dataclass
from pathlib import Path

SEVERITIES = ("error", "warn", "note")
CONFIG_NAMES = ("wrangler.jsonc", "wrangler.json", "wrangler.toml")
TOP_LEVEL_ONLY_KEYS = {
    "name", "main", "compatibility_date", "compatibility_flags", "workers_dev",
    "preview_urls", "routes", "route", "account_id", "keep_vars",
}
CONFIG_TABLES = {"assets", "observability", "triggers", "build", "placement", "limits", "vars", "dev", "site"}
NON_INHERITED_BINDINGS = (
    "kv_namespaces", "d1_databases", "r2_buckets", "queues", "durable_objects", "hyperdrive",
    "services", "vectorize", "analytics_engine_datasets", "workflows", "secrets_store_secrets",
    "ratelimits", "send_email", "dispatch_namespaces", "pipelines", "vpc_services",
)
RESOURCE_IDENTITY_FIELDS = {
    "kv_namespaces": ("id",),
    "d1_databases": ("database_id", "database_name"),
    "r2_buckets": ("bucket_name",),
    "hyperdrive": ("id",),
    "vectorize": ("index_name",),
    "analytics_engine_datasets": ("dataset",),
}
SECRET_LIKE_VAR = re.compile(r"(TOKEN|SECRET|PASSWORD|PASSWD|PRIVATE|API_?KEY|CREDENTIAL)", re.I)
HSTS_PRELOADED_TLDS = {
    "dev", "app", "page", "new", "day", "foo", "zip", "mov", "bank", "insurance", "gle",
    "chrome", "android", "google", "youtube", "gmail", "how", "soy", "ing", "meme", "esq",
    "nexus", "phd", "prof", "boo", "channel", "dad", "rsvp", "fly", "ads", "eat",
}
ORIGIN_UNREACHABLE = {520, 521, 522, 523, 524, 525, 526, 527, 530}
STALE_COMPAT_DAYS = 548


@dataclass
class Finding:
    severity: str
    rule: str
    where: str
    message: str


def strip_jsonc(text: str) -> str:
    out = []
    i, n = 0, len(text)
    in_string = False
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
        elif text.startswith("//", i):
            end = text.find("\n", i)
            i = n if end == -1 else end
        elif text.startswith("/*", i):
            end = text.find("*/", i + 2)
            i = n if end == -1 else end + 2
        else:
            out.append(ch)
            i += 1
    return re.sub(r",(\s*[}\]])", r"\1", "".join(out))


def load_config(path: Path) -> dict:
    text = path.read_text()
    if path.suffix == ".toml":
        return tomllib.loads(text)
    return json.loads(strip_jsonc(text))


def find_config(directory: Path) -> Path | None:
    for name in CONFIG_NAMES:
        candidate = directory / name
        if candidate.exists():
            return candidate
    return None


def environments(config: dict) -> dict[str, dict]:
    merged = {"(top-level)": config}
    for env_name, env in (config.get("env") or {}).items():
        effective = {key: value for key, value in config.items() if key != "env" and key not in NON_INHERITED_BINDINGS and key != "vars"}
        effective.update(env)
        merged[f"env.{env_name}"] = effective
    return merged


def route_list(env: dict) -> list:
    routes = env.get("routes") or []
    if env.get("route"):
        routes = [*routes, env["route"]]
    return routes


def has_custom_domain(routes: list) -> bool:
    return any(isinstance(r, dict) and r.get("custom_domain") for r in routes)


def check_targets(where: str, env: dict) -> list[Finding]:
    findings = []
    routes = route_list(env)
    crons = (env.get("triggers") or {}).get("crons") or []
    workers_dev = env.get("workers_dev", not routes)
    if not routes and workers_dev is False and not crons:
        findings.append(Finding("error", "no-public-target", where,
            "workers_dev is false and no route or custom domain is set: the deploy goes green and serves nothing (every hostname 522s)."))
    if routes and env.get("workers_dev") is True:
        findings.append(Finding("warn", "workers-dev-alongside-routes", where,
            "workers_dev = true while routes exist: the Worker is also public on *.workers.dev, outside zone redirects, WAF and hostname-scoped Access."))
    if routes and "preview_urls" not in env:
        findings.append(Finding("note", "preview-urls-implicit", where,
            "preview_urls is unset, so the Worker's previous setting persists; set it explicitly: true only when public preview URLs are acceptable or Worker-level Access gates them, otherwise false."))
    return findings


def check_compat_date(where: str, env: dict, today: datetime.date) -> list[Finding]:
    raw = env.get("compatibility_date")
    if not raw:
        return [Finding("warn", "compat-date-missing", where, "No compatibility_date: pin one so runtime behaviour changes only when you move it.")]
    try:
        date = datetime.date.fromisoformat(str(raw))
    except ValueError:
        return [Finding("error", "compat-date-invalid", where, f"compatibility_date {raw!r} is not YYYY-MM-DD.")]
    if date > today:
        return [Finding("error", "compat-date-future", where, f"compatibility_date {raw} is in the future; deploys fail once it exceeds the runtime wrangler bundles.")]
    if (today - date).days > STALE_COMPAT_DAYS:
        return [Finding("note", "compat-date-stale", where, f"compatibility_date {raw} is over 18 months old; read the compatibility-flags changelog before bumping.")]
    return []


def check_assets(where: str, env: dict) -> list[Finding]:
    assets = env.get("assets")
    if not isinstance(assets, dict):
        return []
    findings = []
    if assets.get("run_worker_first") is True:
        findings.append(Finding("warn", "run-worker-first-all", where,
            "run_worker_first = true meters every asset request as a Worker invocation (429 past the free daily limit); list only the paths that need code, e.g. [\"/api/*\"]."))
    if not env.get("main") and "not_found_handling" not in assets:
        findings.append(Finding("note", "assets-404-unset", where,
            "Assets-only Worker without not_found_handling: unknown paths return a bare 404; use \"404-page\" for a site or \"single-page-application\" for an SPA."))
    if env.get("main") and assets.get("binding") is None and assets.get("run_worker_first") not in (None, False):
        findings.append(Finding("note", "assets-binding-missing", where,
            "run_worker_first routes requests to the Worker but assets has no binding, so the Worker cannot fall through to env.ASSETS.fetch()."))
    return findings


def check_vars(where: str, env: dict) -> list[Finding]:
    findings = []
    for key in (env.get("vars") or {}):
        if SECRET_LIKE_VAR.search(key):
            findings.append(Finding("warn", "secret-in-vars", where,
                f"vars.{key} looks like a secret; vars are plaintext in the repo and the dashboard. Use a Worker secret (wrangler secret put) instead."))
    return findings


def check_misplaced_toml_keys(config: dict) -> list[Finding]:
    findings = []
    scopes = [("", config)] + [(f"env.{n}.", e) for n, e in (config.get("env") or {}).items()]
    for prefix, scope in scopes:
        for table in CONFIG_TABLES:
            body = scope.get(table)
            if not isinstance(body, dict):
                continue
            for key in sorted(TOP_LEVEL_ONLY_KEYS & body.keys()):
                findings.append(Finding("error", "misplaced-top-level-key", f"{prefix}{table}.{key}",
                    f"'{key}' sits under [{prefix}{table}] and is ignored there; in TOML, top-level keys must come before the first [table] header."))
    return findings


def binding_identities(env: dict, kind: str) -> dict[str, str]:
    identities = {}
    for binding in env.get(kind) or []:
        if not isinstance(binding, dict):
            continue
        for field in RESOURCE_IDENTITY_FIELDS.get(kind, ()):
            if binding.get(field):
                identities[str(binding[field])] = binding.get("binding", "?")
                break
    return identities


def check_environment_bindings(config: dict) -> list[Finding]:
    findings = []
    envs = config.get("env") or {}
    for env_name, env in envs.items():
        for kind in NON_INHERITED_BINDINGS:
            top_names = {b.get("binding") or b.get("name") for b in config.get(kind) or [] if isinstance(b, dict)}
            env_names = {b.get("binding") or b.get("name") for b in env.get(kind) or [] if isinstance(b, dict)}
            for missing in sorted(n for n in top_names - env_names if n):
                findings.append(Finding("warn", "binding-not-inherited", f"env.{env_name}.{kind}",
                    f"Binding {missing} exists at top level but not in env.{env_name}; bindings are never inherited, so that environment deploys without it."))
            if kind in RESOURCE_IDENTITY_FIELDS:
                shared = binding_identities(config, kind).keys() & binding_identities(env, kind).keys()
                for resource in sorted(shared):
                    findings.append(Finding("error", "shared-binding-across-envs", f"env.{env_name}.{kind}",
                        f"{kind} resource {resource} is bound in both production and env.{env_name}: that environment reads and writes production data."))
    names = [config.get("name")] + [e.get("name") for e in envs.values()]
    named = [n for n in names if n]
    if len(named) != len(set(named)):
        findings.append(Finding("error", "env-name-collision", "env",
            "Two environments resolve to the same Worker name, so deploying one overwrites the other."))
    return findings


def check_config(path: Path, today: datetime.date) -> list[Finding]:
    config = load_config(path)
    findings = []
    if path.suffix == ".toml":
        findings += check_misplaced_toml_keys(config)
    for where, env in environments(config).items():
        findings += check_targets(where, env)
        findings += check_compat_date(where, env, today)
        findings += check_assets(where, env)
        findings += check_vars(where, env)
    findings += check_environment_bindings(config)
    return findings


@dataclass
class Probe:
    url: str
    status: int | None
    headers: dict
    seconds: float
    error: str | None = None


def fetch(url: str, timeout: float) -> Probe:
    parts = urllib.parse.urlsplit(url)
    connection_class = http.client.HTTPSConnection if parts.scheme == "https" else http.client.HTTPConnection
    kwargs = {"timeout": timeout}
    if parts.scheme == "https":
        kwargs["context"] = ssl.create_default_context()
    started = time.monotonic()
    try:
        connection = connection_class(parts.netloc, **kwargs)
        connection.request("GET", parts.path or "/", headers={"User-Agent": "edge-check/1", "Accept": "text/html"})
        response = connection.getresponse()
        headers = {k.lower(): v for k, v in response.getheaders()}
        response.read(65536)
        connection.close()
        return Probe(url, response.status, headers, time.monotonic() - started)
    except (socket.timeout, TimeoutError):
        return Probe(url, None, {}, time.monotonic() - started, "timeout")
    except (OSError, http.client.HTTPException, ssl.SSLError) as exc:
        return Probe(url, None, {}, time.monotonic() - started, f"{type(exc).__name__}: {exc}")


def follow(url: str, timeout: float, fetcher=fetch, limit: int = 6) -> list[Probe]:
    chain = []
    for _ in range(limit):
        probe = fetcher(url, timeout)
        chain.append(probe)
        location = probe.headers.get("location")
        if probe.status is None or not (300 <= probe.status < 400) or not location:
            break
        url = urllib.parse.urljoin(url, location)
    return chain


def classify_probe(host: str, probe: Probe) -> list[Finding]:
    if probe.error == "timeout":
        return [Finding("error", "no-response", host, f"{probe.url} did not answer within {probe.seconds:.0f}s (proxied record pointing at a dead origin, or a firewall drop).")]
    if probe.error:
        return [Finding("error", "unreachable", host, f"{probe.url}: {probe.error}")]
    if probe.status in ORIGIN_UNREACHABLE:
        return [Finding("error", "origin-unreachable", host,
            f"{probe.url} returned {probe.status}: the hostname is proxied but no Worker route, custom domain or redirect rule claims it, so Cloudflare forwards to the placeholder origin.")]
    return []


def check_final_response(host: str, probe: Probe) -> list[Finding]:
    findings = []
    headers = probe.headers
    if headers.get("server", "").lower() != "cloudflare":
        findings.append(Finding("note", "not-on-cloudflare", host, f"{probe.url} is not served through Cloudflare (server: {headers.get('server', '-')})."))
    tld = host.rsplit(".", 1)[-1].lower()
    if "strict-transport-security" not in headers and tld not in HSTS_PRELOADED_TLDS:
        findings.append(Finding("warn", "hsts-missing", host, "No Strict-Transport-Security header; enable HSTS on the zone (SSL/TLS, Edge Certificates) once every subdomain serves HTTPS."))
    if headers.get("x-content-type-options", "").lower() != "nosniff":
        findings.append(Finding("note", "nosniff-missing", host, "No X-Content-Type-Options: nosniff; add it in _headers."))
    csp = headers.get("content-security-policy", "")
    if "frame-ancestors" not in csp and "x-frame-options" not in headers:
        findings.append(Finding("note", "framing-unprotected", host, "Neither CSP frame-ancestors nor X-Frame-Options is set; add frame-ancestors 'none' in _headers."))
    return findings


def check_soft_404(host: str, timeout: float, fetcher=fetch) -> list[Finding]:
    probe = fetcher(f"https://{host}/edge-check-{secrets.token_hex(6)}", timeout)
    if probe.status == 200:
        return [Finding("warn", "soft-404", host,
            "A random path returned 200: not_found_handling is single-page-application on a multi-page site, or a catch-all route swallows misses (search engines index the duplicates).")]
    return []


def is_apex_candidate(host: str) -> bool:
    return host.count(".") == 1


def check_canonical(apex: str, www: str, apex_chain: list[Probe], www_chain: list[Probe]) -> list[Finding]:
    findings = []
    apex_first, www_first = apex_chain[0], www_chain[0]
    if apex_first.status == 200 and www_first.status == 200:
        findings.append(Finding("warn", "www-apex-both-serve", f"{apex}+{www}",
            "Apex and www both serve 200: every page exists twice. Redirect one to the other with a single redirect rule."))
    for first, other in ((www_first, apex), (apex_first, www)):
        location = first.headers.get("location", "")
        if first.status in (302, 303, 307) and other in location:
            findings.append(Finding("note", "canonical-redirect-temporary", first.url,
                f"{first.url} redirects to {other} with {first.status}; use 301 (or 308) for the canonical host."))
    return findings


def check_live(hosts: list[str], timeout: float, probe_www: bool, fetcher=fetch) -> list[Finding]:
    findings = []
    chains = {}
    targets = list(dict.fromkeys(hosts + ([f"www.{h}" for h in hosts if probe_www and is_apex_candidate(h)])))
    for host in targets:
        chain = follow(f"https://{host}/", timeout, fetcher)
        chains[host] = chain
        broken = [f for p in chain for f in classify_probe(host, p)]
        findings += broken
        final = chain[-1]
        if not broken and final.status and 200 <= final.status < 300:
            findings += check_final_response(host, final)
    for host in hosts:
        www = f"www.{host}"
        if www in chains and not any(f.where in (host, www) and f.severity == "error" for f in findings):
            findings += check_canonical(host, www, chains[host], chains[www])
        if chains.get(host) and chains[host][-1].status == 200:
            findings += check_soft_404(host, timeout, fetcher)
    return findings


def render(findings: list[Finding], as_json: bool) -> str:
    if as_json:
        return json.dumps({"findings": [asdict(f) for f in findings]}, indent=2)
    if not findings:
        return "edge-check: no findings"
    order = {s: i for i, s in enumerate(SEVERITIES)}
    lines = [f"{f.severity.upper():5} {f.rule:30} {f.where}\n      {f.message}" for f in sorted(findings, key=lambda f: order[f.severity])]
    counts = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITIES}
    lines.append(f"edge-check: {counts['error']} error, {counts['warn']} warn, {counts['note']} note")
    return "\n".join(lines)


def exit_code(findings: list[Finding], fail_on: str) -> int:
    if fail_on == "never":
        return 0
    threshold = SEVERITIES.index(fail_on)
    return 1 if any(SEVERITIES.index(f.severity) <= threshold for f in findings) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="edge_check.py", description="Lint a wrangler config and probe live Cloudflare-hosted hostnames for the failures that deploy green but serve broken.")
    sub = parser.add_subparsers(dest="mode", required=True)
    config_parser = sub.add_parser("config", help="lint wrangler.jsonc/json/toml files or directories containing one")
    config_parser.add_argument("paths", nargs="*", default=["."])
    config_parser.add_argument("--today", help="override today's date (YYYY-MM-DD) for compatibility_date checks")
    live_parser = sub.add_parser("live", help="probe hostnames over HTTPS")
    live_parser.add_argument("hosts", nargs="+")
    live_parser.add_argument("--timeout", type=float, default=20.0)
    live_parser.add_argument("--no-www", action="store_true", help="do not also probe www.<apex>")
    for p in (config_parser, live_parser):
        p.add_argument("--json", action="store_true")
        p.add_argument("--fail-on", choices=(*SEVERITIES, "never"), default="error")
    args = parser.parse_args(argv)

    if args.mode == "config":
        today = datetime.date.fromisoformat(args.today) if args.today else datetime.date.today()
        findings = []
        for raw in args.paths:
            path = Path(raw)
            target = find_config(path) if path.is_dir() else path
            if target is None:
                findings.append(Finding("error", "config-not-found", str(path), f"No {' / '.join(CONFIG_NAMES)} found."))
                continue
            for finding in check_config(target, today):
                finding.where = f"{target}:{finding.where}"
                findings.append(finding)
    else:
        hosts = [h.removeprefix("https://").removeprefix("http://").strip("/") for h in args.hosts]
        findings = check_live(hosts, args.timeout, not args.no_www)

    print(render(findings, args.json))
    return exit_code(findings, args.fail_on)


if __name__ == "__main__":
    sys.exit(main())
