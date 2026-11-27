#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/template"

python3 -I - <<'PY'
import json
import pathlib
import re
import subprocess
import sys

root = pathlib.Path(".")
schema = json.loads((root / "contract/service-status.schema.json").read_text())
allowed = set(schema["properties"])
for fixture in sorted((root / "contract/fixtures").glob("*.json")):
    data = json.loads(fixture.read_text())
    extra = set(data) - allowed
    missing = set(schema["required"]) - set(data)
    if extra or missing:
        sys.exit(f"{fixture}: extra {sorted(extra)}, missing {sorted(missing)}")
for fixture in sorted((root / "contract/invalid").glob("*.json")):
    json.loads(fixture.read_text())

comment = re.compile(r"^\s*(//|/\*|\*\s|<!--)")
hash_comment = re.compile(r"^\s*#(?!!)")
offenders = []
for path in sorted(root.rglob("*")):
    if not path.is_file() or "node_modules" in path.parts or "dist" in path.parts:
        continue
    if path.suffix in {".ts", ".tsx", ".css", ".html"}:
        pattern = comment
    elif path.suffix == ".py":
        pattern = hash_comment
    else:
        continue
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if pattern.match(line):
            offenders.append(f"{path}:{number}: {line.strip()}")
if offenders:
    sys.exit("comments are not allowed:\n" + "\n".join(offenders))

server = subprocess.Popen(
    [sys.executable, "-I", "server/python/stdlib_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
)
requests = [
    ("initialize", {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test.sh", "version": "1"}}),
    ("tools/list", {}),
    ("tools/call", {"name": "service_status_show", "arguments": {"serviceId": "checkout-api"}}),
    ("tools/call", {"name": "service_restart_prepare", "arguments": {"serviceId": "checkout-api"}}),
]
replies = []
for number, (method, params) in enumerate(requests, 1):
    server.stdin.write(json.dumps({"jsonrpc": "2.0", "id": number, "method": method, "params": params}) + "\n")
    server.stdin.flush()
    replies.append(json.loads(server.stdout.readline())["result"])
token = replies[3]["_meta"]["example.invalid/confirmToken"]
confirm = {"serviceId": "checkout-api", "confirmToken": token, "idempotencyKey": "key-00000001"}
outcomes = []
for number in (5, 6):
    server.stdin.write(json.dumps({"jsonrpc": "2.0", "id": number, "method": "tools/call", "params": {"name": "service_restart_confirm", "arguments": confirm}}) + "\n")
    server.stdin.flush()
    outcomes.append(json.loads(server.stdout.readline())["result"]["structuredContent"]["outcome"])
server.stdin.close()
server.wait(timeout=5)

tools = {tool["name"]: tool for tool in replies[1]["tools"]}
assert tools["service_status_show"]["_meta"]["ui"] == {"resourceUri": "ui://service-status/v1/card.html", "visibility": ["model", "app"]}
assert tools["service_restart_confirm"]["_meta"]["ui"]["visibility"] == ["app"]
assert tools["service_restart_confirm"]["annotations"]["destructiveHint"] is True
shown = replies[2]
assert set(shown["structuredContent"]) <= allowed
assert "this client shows text only" in shown["content"][0]["text"]
assert token not in json.dumps(replies[3]["structuredContent"])
assert outcomes == ["accepted", "duplicate"], outcomes
print("mcp-apps-ui: contract fixtures, no-comment rule and stdlib server checks pass")
PY
