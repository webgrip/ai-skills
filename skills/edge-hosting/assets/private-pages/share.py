#!/usr/bin/env python3
import argparse
import json
import os
import re
import secrets
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from pathlib import Path

API = "https://api.cloudflare.com/client/v4"
APP_PREFIX = "share-"
NAME_PATTERN = re.compile(r"^[a-f0-9]{24}$")
GRACE_SECONDS = 7 * 24 * 3600
DURATION_UNITS = {"m": 60, "h": 3600, "d": 86400, "w": 604800}


class ApiError(RuntimeError):
    pass


@dataclass
class Settings:
    account_id: str
    host: str
    namespace_id: str
    owner: str | None
    session: str


class CloudflareApi:
    def __init__(self, token: str):
        self.token = token

    def call(self, method: str, path: str, body=None, raw: bytes | None = None, content_type: str | None = None):
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
        request = urllib.request.Request(f"{API}{path}", data=data, method=method)
        request.add_header("Authorization", f"Bearer {self.token}")
        request.add_header("Content-Type", content_type or "application/json")
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                payload = json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            raise ApiError(f"{method} {path} -> {exc.code}: {exc.read().decode(errors='replace')[:500]}") from exc
        if not payload.get("success", True):
            raise ApiError(f"{method} {path} failed: {payload.get('errors')}")
        return payload


def parse_duration(text: str) -> int:
    match = re.fullmatch(r"(\d+)([mhdw])", text)
    if not match:
        raise argparse.ArgumentTypeError(f"duration {text!r} must look like 90m, 12h, 30d or 2w")
    return int(match[1]) * DURATION_UNITS[match[2]]


def multipart(fields: dict[str, tuple[str, bytes, str]]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    chunks = []
    for name, (filename, content, content_type) in fields.items():
        disposition = f'form-data; name="{name}"' + (f'; filename="{filename}"' if filename else "")
        chunks.append(f"--{boundary}\r\nContent-Disposition: {disposition}\r\nContent-Type: {content_type}\r\n\r\n".encode())
        chunks.append(content + b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def include_rules(recipients: list[str], domains: list[str], owner: str | None) -> list[dict]:
    emails = list(dict.fromkeys([*recipients, *([owner] if owner else [])]))
    return [{"email": {"email": e}} for e in emails] + [{"email_domain": {"domain": d}} for d in domains]


def all_share_apps(api, settings: Settings) -> list[dict]:
    apps, page = [], 1
    while True:
        payload = api.call("GET", f"/accounts/{settings.account_id}/access/apps?page={page}&per_page=100") or {}
        apps += [a for a in payload.get("result") or [] if a.get("name", "").startswith(APP_PREFIX)]
        info = payload.get("result_info") or {}
        if page >= int(info.get("total_pages") or 1):
            return apps
        page += 1


def find_app(api, settings: Settings, name: str) -> dict | None:
    return next((a for a in all_share_apps(api, settings) if a["name"] == f"{APP_PREFIX}{name}"), None)


def page_url(settings: Settings, name: str) -> str:
    return f"https://{settings.host}/p/{name}"


def create_gate(api, settings: Settings, name: str, rules: list[dict]) -> dict:
    account = settings.account_id
    policy = api.call("POST", f"/accounts/{account}/access/policies", {
        "name": f"{APP_PREFIX}{name}",
        "decision": "allow",
        "include": rules,
    })["result"]
    try:
        app = api.call("POST", f"/accounts/{account}/access/apps", {
            "name": f"{APP_PREFIX}{name}",
            "type": "self_hosted",
            "domain": f"{settings.host}/p/{name}",
            "destinations": [{"type": "public", "uri": f"{settings.host}/p/{name}"}],
            "session_duration": settings.session,
            "app_launcher_visible": False,
            "policies": [{"id": policy["id"], "precedence": 1}],
        })["result"]
    except ApiError:
        api.call("DELETE", f"/accounts/{account}/access/policies/{policy['id']}")
        raise
    return app


def delete_gate(api, settings: Settings, app: dict) -> None:
    account = settings.account_id
    api.call("DELETE", f"/accounts/{account}/access/apps/{app['id']}")
    for linked in app.get("policies") or []:
        if linked.get("name", "").startswith(APP_PREFIX):
            api.call("DELETE", f"/accounts/{account}/access/policies/{linked['id']}")


def upload(api, settings: Settings, name: str, html: bytes, expires: int, aud: str) -> None:
    body, content_type = multipart({
        "value": ("", html, "text/html"),
        "metadata": ("", json.dumps({"expires": expires, "aud": aud}).encode(), "application/json"),
    })
    path = f"/accounts/{settings.account_id}/storage/kv/namespaces/{settings.namespace_id}/values/{name}?expiration={expires + GRACE_SECONDS}"
    api.call("PUT", path, raw=body, content_type=content_type)


def read_metadata(api, settings: Settings, name: str) -> dict | None:
    payload = api.call("GET", f"/accounts/{settings.account_id}/storage/kv/namespaces/{settings.namespace_id}/metadata/{name}")
    return (payload or {}).get("result")


def publish(api, settings: Settings, file: Path, recipients: list[str], domains: list[str], expires_in: int, name: str | None, now: float) -> str:
    html = file.read_bytes()
    expires = int(now) + expires_in
    if name:
        app = find_app(api, settings, name)
        if app is None:
            raise ApiError(f"no Access application {APP_PREFIX}{name}; republish only works for a live page")
    else:
        if not recipients and not domains:
            raise ApiError("a new page needs --to or --domain: the Access gate goes up before the content")
        name = secrets.token_hex(12)
        app = create_gate(api, settings, name, include_rules(recipients, domains, settings.owner))
    upload(api, settings, name, html, expires, app["aud"])
    return page_url(settings, name)


def revoke(api, settings: Settings, name: str) -> list[str]:
    done = []
    api.call("DELETE", f"/accounts/{settings.account_id}/storage/kv/namespaces/{settings.namespace_id}/values/{name}")
    done.append("content deleted")
    app = find_app(api, settings, name)
    if app:
        delete_gate(api, settings, app)
        done.append("access application deleted")
    return done


def listing(api, settings: Settings, now: float) -> list[tuple[str, str, str]]:
    rows = []
    for app in all_share_apps(api, settings):
        name = app["name"].removeprefix(APP_PREFIX)
        metadata = read_metadata(api, settings, name)
        if not metadata:
            state = "content gone"
        elif metadata.get("expires", 0) < now:
            state = "expired"
        else:
            state = f"live, {int((metadata['expires'] - now) // 86400)}d left"
        rows.append((name, page_url(settings, name), state))
    return rows


def sweep(api, settings: Settings, now: float) -> list[str]:
    swept = []
    for name, _, state in listing(api, settings, now):
        if not state.startswith("live"):
            revoke(api, settings, name)
            swept.append(name)
    return swept


def settings_from_env(session: str) -> Settings:
    required = ("CLOUDFLARE_ACCOUNT_ID", "SHARE_HOST", "SHARE_KV_NAMESPACE_ID")
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        sys.exit(f"set {', '.join(missing)} (and CLOUDFLARE_API_TOKEN)")
    return Settings(os.environ["CLOUDFLARE_ACCOUNT_ID"], os.environ["SHARE_HOST"], os.environ["SHARE_KV_NAMESPACE_ID"], os.environ.get("SHARE_OWNER"), session)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="share.py", description="Publish a single HTML page behind a per-page Cloudflare Access gate that expires on its own.")
    sub = parser.add_subparsers(dest="command", required=True)
    pub = sub.add_parser("publish")
    pub.add_argument("file", type=Path)
    pub.add_argument("--to", default="", help="comma-separated recipient emails")
    pub.add_argument("--domain", default="", help="comma-separated email domains allowed in")
    pub.add_argument("--expires", type=parse_duration, default=parse_duration("30d"))
    pub.add_argument("--name", help="republish new content and expiry under an existing page name")
    pub.add_argument("--session", default="720h")
    rev = sub.add_parser("revoke")
    rev.add_argument("name")
    sub.add_parser("list")
    sub.add_parser("sweep", help="revoke every page whose content is expired or gone")
    args = parser.parse_args(argv)

    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        sys.exit("set CLOUDFLARE_API_TOKEN (Access: Apps and Policies Edit + Workers KV Storage Edit)")
    settings = settings_from_env(getattr(args, "session", "720h"))
    api = CloudflareApi(token)
    now = time.time()

    if args.command == "publish":
        if args.name and not NAME_PATTERN.fullmatch(args.name):
            sys.exit("--name must be the 24-hex page name")
        split = lambda value: [v.strip() for v in value.split(",") if v.strip()]
        print(publish(api, settings, args.file, split(args.to), split(args.domain), args.expires, args.name, now))
    elif args.command == "revoke":
        print("; ".join(revoke(api, settings, args.name)))
    elif args.command == "list":
        for row in listing(api, settings, now):
            print("  ".join(row))
    else:
        swept = sweep(api, settings, now)
        print(f"revoked {len(swept)}: {', '.join(swept) or '-'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
