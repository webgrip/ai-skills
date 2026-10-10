#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

PROTOCOL_VERSION = "2025-06-18"
ACCEPT = "application/json, text/event-stream"
EXIT_OK = 0
EXIT_EXPECTATION_FAILED = 1
EXIT_UNUSABLE = 2
DETAIL_LIMIT = 300


class ProbeError(Exception):
    pass


class Denied(Exception):
    def __init__(self, step: str, status: int, detail: str):
        super().__init__(f"{step}: HTTP {status}")
        self.step = step
        self.status = status
        self.detail = detail


class RpcError(Exception):
    def __init__(self, method: str, error: Dict[str, object]):
        super().__init__(f"{method}: JSON-RPC error {error.get('code')}: {error.get('message')}")
        self.method = method
        self.error = error


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


OPENER = urllib.request.build_opener(NoRedirect())


def lower_keys(headers) -> Dict[str, str]:
    return {key.lower(): value for key, value in headers.items()}


def sse_messages(body: str) -> List[object]:
    messages = []
    for event in re.split(r"\r?\n\r?\n", body):
        data = "\n".join(line[5:].lstrip(" ") for line in event.splitlines() if line.startswith("data:"))
        if data:
            try:
                messages.append(json.loads(data))
            except json.JSONDecodeError:
                continue
    return messages


def find_response(body: str, content_type: str, request_id: int) -> Dict[str, object]:
    if "text/event-stream" in content_type or body.lstrip().startswith(("event:", "data:", "id:")):
        candidates = sse_messages(body)
    else:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as error:
            raise ProbeError(f"response is neither JSON nor an event stream: {body[:DETAIL_LIMIT]!r}") from error
        candidates = parsed if isinstance(parsed, list) else [parsed]
    for message in candidates:
        if isinstance(message, dict) and message.get("id") == request_id:
            return message
    raise ProbeError(f"no JSON-RPC response with id {request_id} in: {body[:DETAIL_LIMIT]!r}")


@dataclass
class Session:
    url: str
    auth_header: str
    auth_value: str
    timeout: float
    session_id: Optional[str] = None
    protocol_version: Optional[str] = None
    next_id: int = 1
    log: List[str] = field(default_factory=list)

    def headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": ACCEPT, self.auth_header: self.auth_value}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        if self.protocol_version:
            headers["MCP-Protocol-Version"] = self.protocol_version
        return headers

    def send(self, method: str, payload: Optional[Dict[str, object]], http_method: str = "POST") -> Tuple[int, Dict[str, str], str]:
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(self.url, data=data, headers=self.headers(), method=http_method)
        try:
            with OPENER.open(request, timeout=self.timeout) as response:
                return response.status, lower_keys(response.headers), response.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as error:
            return error.code, lower_keys(error.headers or {}), error.read().decode("utf-8", "replace")
        except (urllib.error.URLError, OSError) as error:
            raise ProbeError(f"{method}: cannot reach {self.url} ({getattr(error, 'reason', error)})") from error

    def checked(self, method: str, status: int, headers: Dict[str, str], body: str) -> None:
        if status in (401, 403):
            raise Denied(method, status, body[:DETAIL_LIMIT])
        if 300 <= status < 400:
            raise ProbeError(f"{method}: HTTP {status} redirect to {headers.get('location', '?')}; "
                             "not followed, so the credential stays with this host")
        if status == 406:
            raise ProbeError(f"{method}: HTTP 406; the server rejected Accept: {ACCEPT}")
        if status >= 400:
            raise ProbeError(f"{method}: HTTP {status}: {body[:DETAIL_LIMIT]}")

    def request(self, method: str, params: Optional[Dict[str, object]] = None) -> Dict[str, object]:
        request_id = self.next_id
        self.next_id += 1
        payload: Dict[str, object] = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params
        status, headers, body = self.send(method, payload)
        self.checked(method, status, headers, body)
        if headers.get("mcp-session-id"):
            self.session_id = headers["mcp-session-id"]
        message = find_response(body, headers.get("content-type", ""), request_id)
        if "error" in message:
            raise RpcError(method, message["error"])
        result = message.get("result")
        return result if isinstance(result, dict) else {}

    def notify(self, method: str) -> None:
        status, headers, body = self.send(method, {"jsonrpc": "2.0", "method": method})
        self.checked(method, status, headers, body)

    def close(self) -> None:
        if not self.session_id:
            return
        try:
            self.send("close", None, http_method="DELETE")
        except ProbeError:
            return


def initialize(session: Session) -> Dict[str, object]:
    result = session.request("initialize", {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": {"name": "mcp_probe", "version": "1"},
    })
    session.protocol_version = str(result.get("protocolVersion") or PROTOCOL_VERSION)
    session.notify("notifications/initialized")
    return result


def list_tools(session: Session) -> List[str]:
    names: List[str] = []
    cursor: Optional[str] = None
    while True:
        result = session.request("tools/list", {"cursor": cursor} if cursor else {})
        names += [str(tool.get("name")) for tool in result.get("tools", []) if isinstance(tool, dict)]
        cursor = result.get("nextCursor")
        if not cursor:
            return names


def call_tool(session: Session, name: str, arguments: Dict[str, object]) -> Tuple[bool, str]:
    result = session.request("tools/call", {"name": name, "arguments": arguments})
    texts = [str(item.get("text", "")) for item in result.get("content", []) if isinstance(item, dict)]
    return not result.get("isError", False), " ".join(texts)[:DETAIL_LIMIT]


@dataclass
class Report:
    outcome: str = "unknown"
    detail: str = ""
    server: str = ""
    tools: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    forbidden: List[str] = field(default_factory=list)
    call: Optional[Dict[str, object]] = None
    problems: List[str] = field(default_factory=list)


def probe(session: Session, args: argparse.Namespace) -> Report:
    report = Report()
    try:
        server = initialize(session)
        info = server.get("serverInfo") if isinstance(server.get("serverInfo"), dict) else {}
        report.server = f"{info.get('name', '?')} {info.get('version', '')}".strip()
        report.tools = sorted(list_tools(session))
        report.outcome = "tools" if report.tools else "empty"
        if args.call:
            succeeded, text = call_tool(session, args.call, args.arguments)
            report.call = {"tool": args.call, "ok": succeeded, "text": text}
    except Denied as denied:
        report.outcome = "denied"
        report.detail = f"{denied.step}: HTTP {denied.status} {denied.detail}".strip()
    except RpcError as rpc_error:
        report.outcome = "denied" if rpc_error.method == "initialize" else "error"
        report.detail = str(rpc_error)
    finally:
        session.close()
    return judge(report, args)


def judge(report: Report, args: argparse.Namespace) -> Report:
    if args.expect == "denied":
        if report.outcome == "error":
            report.problems.append(report.detail)
        elif report.outcome == "tools":
            report.problems.append(f"expected no tools, but the key lists {len(report.tools)}")
        return report
    if report.outcome != "tools":
        report.problems.append(f"expected tools, got {report.outcome}"
                               + (f" ({report.detail})" if report.detail else "")
                               + "; a session with this key would run without tools")
    report.missing = sorted(set(args.require) - set(report.tools))
    if report.missing:
        report.problems.append(f"required tools not listed: {', '.join(report.missing)}")
    if args.forbid:
        pattern = re.compile(args.forbid)
        report.forbidden = [name for name in report.tools if pattern.search(name)]
        if report.forbidden:
            report.problems.append(f"tools matching --forbid are advertised: {', '.join(report.forbidden)}")
    if report.call is not None and not report.call["ok"]:
        report.problems.append(f"tools/call {report.call['tool']} returned an error: {report.call['text']}")
    if report.outcome == "error":
        report.problems.append(report.detail)
    return report


def render(report: Report) -> str:
    lines = [f"outcome: {report.outcome}" + (f" ({report.detail})" if report.detail else "")]
    if report.server:
        lines.append(f"server: {report.server}")
    lines.append(f"tools: {len(report.tools)}")
    lines += [f"  {name}" for name in report.tools]
    if report.call is not None:
        lines.append(f"call {report.call['tool']}: {'ok' if report.call['ok'] else 'error'} {report.call['text']}")
    lines += [f"FAIL {problem}" for problem in report.problems]
    lines.append("verdict: " + ("expectation failed" if report.problems else "as expected"))
    return "\n".join(lines)


def parse_arguments(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the MCP streamable-HTTP handshake (initialize, initialized, tools/list, an "
                    "optional tools/call) against a gateway or tool server and check what one key may do. "
                    "The token is read from an environment variable and never printed.")
    parser.add_argument("--url", required=True, help="the MCP endpoint, for example https://gateway.example/mcp")
    parser.add_argument("--token-env", required=True, help="name of the environment variable holding the key")
    parser.add_argument("--auth-header", default="Authorization",
                        help="header that carries the key (LiteLLM also reads x-litellm-api-key)")
    parser.add_argument("--scheme", default="Bearer", help="prefix before the key; empty string for none")
    parser.add_argument("--expect", choices=("tools", "denied"), default="tools",
                        help="tools: the key must list tools; denied: 401, 403 or an empty list")
    parser.add_argument("--require", action="append", default=[], metavar="TOOL",
                        help="a tool name that must be listed (repeatable)")
    parser.add_argument("--forbid", metavar="REGEX",
                        help="fail when any listed tool matches, for example 'update_|create_|delete_|write'")
    parser.add_argument("--call", metavar="TOOL", help="call this tool once after listing")
    parser.add_argument("--arguments", default="{}", help="JSON object of arguments for --call")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        args.arguments = json.loads(args.arguments)
    except json.JSONDecodeError as error:
        parser.error(f"--arguments is not JSON: {error}")
    if not isinstance(args.arguments, dict):
        parser.error("--arguments must be a JSON object")
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_arguments(argv)
    token = os.environ.get(args.token_env, "")
    if not token:
        print(f"environment variable {args.token_env} is empty or unset", file=sys.stderr)
        return EXIT_UNUSABLE
    auth_value = f"{args.scheme} {token}".strip() if args.scheme else token
    session = Session(args.url, args.auth_header, auth_value, args.timeout)
    try:
        report = probe(session, args)
    except ProbeError as error:
        print(str(error).replace(token, "***"), file=sys.stderr)
        return EXIT_UNUSABLE
    output = json.dumps(report.__dict__, indent=2) if args.json else render(report)
    print(output.replace(token, "***"))
    return EXIT_EXPECTATION_FAILED if report.problems else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
