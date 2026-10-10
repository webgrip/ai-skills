#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_ERROR = 2

AUTH_ENVIRONMENT_VARIABLE = "GRAFANA_ADMIN_AUTH"
PAGE_SIZE = 1000
ROLE_RANK = {"None": 0, "Viewer": 1, "Editor": 2, "Admin": 3}
ROLE_PATH_FALLBACK = re.compile(r"\|\|\s*'(Editor|Admin|GrafanaAdmin)'\s*$")
HEALTH_UNSUPPORTED_TYPES = {"alertmanager"}
INFINITY_TYPE = "yesoreyeram-infinity-datasource"
FAILING_SEVERITIES = {"error", "warn"}


class AuditError(Exception):
    pass


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    org: Optional[int]
    message: str


@dataclass
class DatasourceView:
    uid: str
    name: str
    type: str
    url: str
    secure_fields: List[str]
    health: Optional[str] = None


@dataclass
class OrgView:
    id: int
    name: str
    members: Dict[str, List[str]] = field(default_factory=dict)
    datasources: List[DatasourceView] = field(default_factory=list)
    snapshots: int = 0
    public_dashboards: int = 0
    audited: bool = True


class GrafanaClient:
    def __init__(self, base_url: str, credentials: str, timeout: float):
        self.base_url = base_url.rstrip("/")
        self.authorization = "Basic " + base64.b64encode(credentials.encode()).decode()
        self.timeout = timeout

    def get(self, path: str, org: Optional[int] = None) -> Tuple[int, Any]:
        headers = {"Authorization": self.authorization, "Accept": "application/json"}
        if org is not None:
            headers["X-Grafana-Org-Id"] = str(org)
        request = urllib.request.Request(self.base_url + path, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, json.loads(response.read() or b"null")
        except urllib.error.HTTPError as error:
            status, body = error.code, error.read()
            error.close()
            try:
                return status, json.loads(body or b"null")
            except ValueError:
                return status, None
        except (urllib.error.URLError, OSError) as error:
            raise AuditError(f"cannot reach {self.base_url}: {error}") from None
        except ValueError as error:
            raise AuditError(f"{path} did not return JSON: {error}") from None

    def require(self, path: str, org: Optional[int] = None) -> Any:
        status, body = self.get(path, org)
        if status in (401, 403):
            raise AuditError(f"{path} answered {status}: the credentials in {AUTH_ENVIRONMENT_VARIABLE} "
                             "must belong to a Grafana server admin")
        if status != 200:
            raise AuditError(f"{path} answered HTTP {status}")
        return body


def setting(settings: Dict[str, Dict[str, str]], section: str, key: str) -> str:
    return str((settings.get(section) or {}).get(key, "")).strip().lower()


def org_mapping_entries(mapping: str) -> List[Tuple[str, str, str]]:
    entries = []
    for raw in re.split(r"[\s,]+", mapping.strip().strip("[]")):
        token = raw.strip().strip('"')
        if not token:
            continue
        parts = re.split(r"(?<!\\):", token)
        if len(parts) >= 2:
            entries.append((parts[0], parts[1], parts[2] if len(parts) > 2 else "Viewer"))
    return entries


def settings_findings(settings: Dict[str, Dict[str, str]]) -> List[Finding]:
    findings = []
    if setting(settings, "snapshots", "enabled") == "true":
        findings.append(Finding("warn", "snapshots-enabled", None,
                                "dashboard snapshots are on: any Editor can copy panel data behind a URL that "
                                "needs no login; set [snapshots] enabled = false"))
    if setting(settings, "snapshots", "external_enabled") == "true":
        findings.append(Finding("warn", "external-snapshots-enabled", None,
                                "external snapshots are on: data can be uploaded to "
                                f"{(settings.get('snapshots') or {}).get('external_snapshot_url') or 'an outside server'}; "
                                "set [snapshots] external_enabled = false"))
    if setting(settings, "public_dashboards", "enabled") == "true":
        findings.append(Finding("warn", "public-dashboards-enabled", None,
                                "public dashboards are on: any Editor can publish a board without login; "
                                "set [public_dashboards] enabled = false"))
    if setting(settings, "plugins", "preinstall_auto_update") == "true":
        findings.append(Finding("note", "preinstall-auto-update", None,
                                "bundled and preinstalled plugins update themselves at startup; on a read-only root "
                                "filesystem Grafana 13 deletes them first and leaves them unregistered; set "
                                "[plugins] preinstall_auto_update = false and pin plugin versions"))
    oauth = settings.get("auth.generic_oauth") or {}
    mapping = str(oauth.get("org_mapping") or "")
    named = [org for _, org, _ in org_mapping_entries(mapping) if org != "*" and not org.isdigit()]
    if named:
        findings.append(Finding("warn", "org-mapping-by-name", None,
                                f"org_mapping names orgs ({', '.join(sorted(set(named)))}); names resolve once at "
                                "startup and unresolved entries are skipped silently; use numeric org ids"))
    role_path = str(oauth.get("role_attribute_path") or "")
    fallback = ROLE_PATH_FALLBACK.search(role_path)
    if mapping and fallback:
        findings.append(Finding("warn", "role-path-fallback", None,
                                f"role_attribute_path falls back to '{fallback.group(1)}' and that role is raised into "
                                "every org the mapping matches, kiosks included; end the expression in '' instead"))
    return findings


def list_items(body: Any, key: str) -> List[Any]:
    if isinstance(body, list):
        return body
    if isinstance(body, dict) and isinstance(body.get(key), list):
        return body[key]
    return []


def audit_org(client: GrafanaClient, org: Dict[str, Any], admin_orgs: Set[int], plugin_ids: Set[str],
              check_health: bool, findings: List[Finding]) -> OrgView:
    view = OrgView(int(org["id"]), str(org.get("name", "")))
    for member in client.require(f"/api/orgs/{view.id}/users?perpage={PAGE_SIZE}") or []:
        view.members.setdefault(str(member.get("role", "None")), []).append(str(member.get("login", "")))
    status, datasources = client.get("/api/datasources", view.id) if view.id in admin_orgs else (403, None)
    if status in (401, 403):
        view.audited = False
        findings.append(Finding("warn", "org-not-audited", view.id,
                                f"the admin is not a member of org {view.id} ({view.name}), so its datasources, "
                                "snapshots and public dashboards were not read; add the admin to the org"))
        return view
    for datasource in datasources or []:
        uid = str(datasource.get("uid", ""))
        _, detail = client.get(f"/api/datasources/uid/{urllib.parse.quote(uid)}", view.id)
        secure = sorted(k for k, v in ((detail or {}).get("secureJsonFields") or {}).items() if v)
        entry = DatasourceView(uid, str(datasource.get("name", "")), str(datasource.get("type", "")),
                               str(datasource.get("url", "")), secure)
        json_data = (detail or {}).get("jsonData") or {}
        if entry.type == INFINITY_TYPE and json_data.get("auth_method") == "apiKey" and "apiKeyValue" not in secure:
            findings.append(Finding("error", "infinity-api-key-field", view.id,
                                    f"datasource {entry.name} uses API-key auth but stores no secureJsonData.apiKeyValue "
                                    f"({', '.join(secure) or 'no secure fields'}); Infinity reads the key only from "
                                    "apiKeyValue, so every query fails"))
        if entry.type not in plugin_ids:
            findings.append(Finding("error", "datasource-plugin-missing", view.id,
                                    f"datasource {entry.name} needs plugin {entry.type}, which is not loaded; every "
                                    "panel on it answers 'Plugin not registered'"))
        if check_health and entry.type not in HEALTH_UNSUPPORTED_TYPES:
            health_status, health = client.get(f"/api/datasources/uid/{urllib.parse.quote(uid)}/health", view.id)
            entry.health = str((health or {}).get("status") or f"HTTP {health_status}")
            if entry.health != "OK":
                findings.append(Finding("error", "datasource-unhealthy", view.id,
                                        f"datasource {entry.name} health is {entry.health}: "
                                        f"{(health or {}).get('message', '')}".strip()))
        view.datasources.append(entry)
    _, snapshots = client.get(f"/api/dashboard/snapshots?limit={PAGE_SIZE}", view.id)
    view.snapshots = len(list_items(snapshots, "snapshots"))
    if view.snapshots:
        findings.append(Finding("error", "snapshot-exists", view.id,
                                f"org {view.id} ({view.name}) has {view.snapshots} snapshot(s) readable without "
                                "login; review and delete them before switching snapshots off"))
    _, public = client.get(f"/api/dashboards/public-dashboards?perpage={PAGE_SIZE}", view.id)
    view.public_dashboards = len(list_items(public, "publicDashboards"))
    if view.public_dashboards:
        findings.append(Finding("error", "public-dashboard-exists", view.id,
                                f"org {view.id} ({view.name}) has {view.public_dashboards} public dashboard(s) "
                                "readable without login"))
    return view


def kiosk_findings(orgs: List[OrgView], kiosk_pattern: Optional[str], default_org: int) -> List[Finding]:
    if not kiosk_pattern:
        return []
    pattern = re.compile(kiosk_pattern)
    findings = []
    for org in orgs:
        for role, logins in org.members.items():
            for login in filter(pattern.search, logins):
                if org.id == default_org:
                    findings.append(Finding("error", "kiosk-outside-scope", org.id,
                                            f"kiosk {login} is a member of the default org {org.id}"))
                elif ROLE_RANK.get(role, 3) > ROLE_RANK["Viewer"]:
                    findings.append(Finding("error", "kiosk-outside-scope", org.id,
                                            f"kiosk {login} is {role} in org {org.id}; a screen needs Viewer"))
    return findings


def run_audit(client: GrafanaClient, kiosk_pattern: Optional[str], default_org: int,
              check_health: bool) -> Dict[str, Any]:
    health = client.require("/api/health")
    settings = client.require("/api/admin/settings") or {}
    plugin_ids = {str(p.get("id")) for p in client.require("/api/plugins?embedded=0") or []}
    admin_orgs = {int(o.get("orgId", 0)) for o in client.require("/api/user/orgs") or []}
    findings = settings_findings(settings)
    orgs = [audit_org(client, org, admin_orgs, plugin_ids, check_health, findings)
            for org in client.require(f"/api/orgs?perpage={PAGE_SIZE}") or []]
    findings.extend(kiosk_findings(orgs, kiosk_pattern, default_org))
    return {"version": (health or {}).get("version", "unknown"), "orgs": orgs, "findings": findings}


def render_text(result: Dict[str, Any]) -> str:
    lines = [f"Grafana {result['version']}"]
    for org in result["orgs"]:
        roles = ", ".join(f"{role} {len(logins)}" for role, logins in sorted(org.members.items()))
        total = sum(len(logins) for logins in org.members.values())
        lines.append(f"org {org.id} {org.name}: {total} members ({roles})")
        if not org.audited:
            lines.append("  not audited: the admin is not a member")
            continue
        for datasource in org.datasources:
            held = f"; holds {', '.join(datasource.secure_fields)} usable by all {total} members" \
                if datasource.secure_fields else ""
            health = f"; health {datasource.health}" if datasource.health else ""
            lines.append(f"  datasource {datasource.name} [{datasource.type}] {datasource.url}{held}{health}")
        lines.append(f"  snapshots {org.snapshots}, public dashboards {org.public_dashboards}")
    for finding in result["findings"]:
        scope = f"org {finding.org}" if finding.org is not None else "instance"
        lines.append(f"{finding.severity}\t{finding.rule}\t{scope}\t{finding.message}")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only audit of who can see which data in a Grafana instance: members and roles per org, "
        "datasources and the credentials every member can use, snapshots, public dashboards, OAuth org mapping "
        f"traps and missing plugins. Credentials of a server admin come from {AUTH_ENVIRONMENT_VARIABLE}=user:password. "
        "Exit 0: no error or warn findings; 1: findings; 2: could not audit.")
    parser.add_argument("--url", required=True, help="Grafana base URL, for example http://127.0.0.1:3000")
    parser.add_argument("--kiosk-login", help="regular expression matching the logins of wall-screen accounts")
    parser.add_argument("--default-org", type=int, default=1, help="org id staff land in (default 1)")
    parser.add_argument("--health", action="store_true",
                        help="also run every datasource's health check, which makes Grafana contact each backend")
    parser.add_argument("--timeout", type=float, default=20.0, help="seconds per request (default 20)")
    parser.add_argument("--json", action="store_true", help="print the inventory and findings as JSON")
    args = parser.parse_args(argv)
    credentials = os.environ.get(AUTH_ENVIRONMENT_VARIABLE, "")
    if ":" not in credentials:
        print(f"set {AUTH_ENVIRONMENT_VARIABLE}=user:password for a Grafana server admin", file=sys.stderr)
        return EXIT_ERROR
    try:
        result = run_audit(GrafanaClient(args.url, credentials, args.timeout), args.kiosk_login,
                           args.default_org, args.health)
    except AuditError as error:
        print(f"audit failed: {error}", file=sys.stderr)
        return EXIT_ERROR
    if args.json:
        print(json.dumps({"version": result["version"], "orgs": [asdict(o) for o in result["orgs"]],
                          "findings": [asdict(f) for f in result["findings"]]}, indent=2))
    else:
        print(render_text(result))
    failing = [f for f in result["findings"] if f.severity in FAILING_SEVERITIES]
    return EXIT_FINDINGS if failing else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
