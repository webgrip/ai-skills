import contextlib
import importlib.util
import io
import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
FIXTURES = SCRIPTS.parent / "fixtures"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


mcp_probe = load("mcp_probe")
otlp_cases = load("otlp_cases")

READ_TOOLS = [["metrics_scope_a-query", "metrics_scope_a-labels"], ["logs_scope_a-query"]]
WRITE_TOOLS = [["grafana-search_dashboards", "grafana-update_dashboard"]]
SESSION_ID = "session-1"


class StubMcpGateway(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def reply(self, status, body="", content_type="application/json", extra=None):
        payload = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(payload)

    def reply_event(self, message, extra=None):
        self.reply(200, f"event: message\ndata: {json.dumps(message)}\n\n", "text/event-stream", extra)

    def do_DELETE(self):
        self.server.deleted.append(self.headers.get("Mcp-Session-Id"))
        self.reply(204)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
        self.server.requests.append((self.headers, body))
        accept = self.headers.get("Accept", "")
        if "application/json" not in accept or "text/event-stream" not in accept:
            return self.reply(406, '{"error":"Not Acceptable"}')
        key = self.headers.get("x-litellm-api-key", "")
        if key == "Bearer moved":
            return self.reply(307, extra={"Location": "https://elsewhere.invalid/mcp"})
        if key == "Bearer revoked":
            return self.reply(401, '{"error":"Authentication Error"}')
        if key == "Bearer no-grant":
            return self.reply(403, '{"error":"The key has no MCP servers granted"}')
        pages = {"Bearer granted": READ_TOOLS, "Bearer writer": WRITE_TOOLS, "Bearer empty": [[]]}.get(key)
        if pages is None:
            return self.reply(401, '{"error":"unknown key"}')
        method = body.get("method")
        if method == "initialize":
            return self.reply_event({"jsonrpc": "2.0", "id": body["id"], "result": {
                "protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                "serverInfo": {"name": "stub-gateway", "version": "1.0"}}}, {"Mcp-Session-Id": SESSION_ID})
        if self.headers.get("Mcp-Session-Id") != SESSION_ID:
            return self.reply(400, '{"error":"missing session"}')
        if method == "notifications/initialized":
            return self.reply(202)
        if method == "tools/list":
            cursor = int((body.get("params") or {}).get("cursor") or 0)
            result = {"tools": [{"name": name, "inputSchema": {"type": "object"}} for name in pages[cursor]]}
            if cursor + 1 < len(pages):
                result["nextCursor"] = str(cursor + 1)
            return self.reply_event({"jsonrpc": "2.0", "id": body["id"], "result": result})
        if method == "tools/call":
            failing = body["params"]["name"].endswith("labels")
            return self.reply(200, json.dumps({"jsonrpc": "2.0", "id": body["id"], "result": {
                "content": [{"type": "text", "text": "boom" if failing else "count: 3"}], "isError": failing}}))
        return self.reply(200, json.dumps({"jsonrpc": "2.0", "id": body.get("id"),
                                           "error": {"code": -32601, "message": "method not found"}}))


class StubOtlpReceiver(BaseHTTPRequestHandler):
    def log_message(self, *args):
        return

    def do_POST(self):
        payload = self.rfile.read(int(self.headers.get("Content-Length", "0")))
        self.server.requests.append((self.path, self.headers.get("Content-Type"), json.loads(payload)))
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"{}")


def start(handler):
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    server.requests = []
    server.deleted = []
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def stop(server):
    server.shutdown()
    server.server_close()


def run(module, argv, env=None):
    stdout, stderr = io.StringIO(), io.StringIO()
    previous = dict(os.environ)
    os.environ.update(env or {})
    try:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = module.main(argv)
    finally:
        os.environ.clear()
        os.environ.update(previous)
    return code, stdout.getvalue(), stderr.getvalue()


class McpProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = start(StubMcpGateway)
        cls.url = f"http://127.0.0.1:{cls.server.server_address[1]}/mcp"

    @classmethod
    def tearDownClass(cls):
        stop(cls.server)

    def probe(self, key, *extra):
        argv = ["--url", self.url, "--token-env", "PROBE_KEY", "--auth-header", "x-litellm-api-key", *extra]
        return run(mcp_probe, argv, {"PROBE_KEY": key})

    def test_granted_key_lists_every_page_of_tools_and_closes_the_session(self):
        code, out, _ = self.probe("granted", "--require", "logs_scope_a-query")
        self.assertEqual(code, 0, out)
        self.assertIn("tools: 3", out)
        self.assertIn(SESSION_ID, self.server.deleted)
        headers = [headers for headers, body in self.server.requests if body.get("method") == "tools/list"]
        self.assertTrue(all(h.get("MCP-Protocol-Version") == "2025-06-18" for h in headers))

    def test_key_without_grant_fails_a_tools_expectation(self):
        code, out, _ = self.probe("no-grant")
        self.assertEqual(code, 1)
        self.assertIn("HTTP 403", out)

    def test_key_without_grant_meets_a_denied_expectation(self):
        code, _, _ = self.probe("no-grant", "--expect", "denied")
        self.assertEqual(code, 0)

    def test_revoked_key_is_denied_with_401(self):
        code, out, _ = self.probe("revoked", "--expect", "denied")
        self.assertEqual(code, 0)
        self.assertIn("HTTP 401", out)

    def test_granted_key_fails_a_denied_expectation(self):
        code, _, _ = self.probe("granted", "--expect", "denied")
        self.assertEqual(code, 1)

    def test_empty_tool_list_is_silent_degradation(self):
        code, out, _ = self.probe("empty")
        self.assertEqual(code, 1)
        self.assertIn("without tools", out)

    def test_forbidden_write_tool_is_reported(self):
        code, out, _ = self.probe("writer", "--forbid", "update_|create_|delete_")
        self.assertEqual(code, 1)
        self.assertIn("grafana-update_dashboard", out)

    def test_missing_required_tool_fails(self):
        code, out, _ = self.probe("granted", "--require", "metrics_scope_b-query")
        self.assertEqual(code, 1)
        self.assertIn("metrics_scope_b-query", out)

    def test_successful_call(self):
        code, out, _ = self.probe("granted", "--call", "metrics_scope_a-query", "--arguments", '{"query": "up"}')
        self.assertEqual(code, 0, out)
        self.assertIn("count: 3", out)

    def test_tool_error_result_fails(self):
        code, _, _ = self.probe("granted", "--call", "metrics_scope_a-labels")
        self.assertEqual(code, 1)

    def test_redirect_is_not_followed(self):
        code, _, err = self.probe("moved")
        self.assertEqual(code, 2)
        self.assertIn("not followed", err)

    def test_token_never_printed(self):
        _, out, err = self.probe("granted", "--json")
        self.assertNotIn("granted", out + err)

    def test_unset_token_is_unusable(self):
        code, _, err = run(mcp_probe, ["--url", self.url, "--token-env", "PROBE_KEY_UNSET"])
        self.assertEqual(code, 2)
        self.assertIn("PROBE_KEY_UNSET", err)

    def test_unreachable_endpoint_is_unusable(self):
        code, _, err = run(mcp_probe, ["--url", "http://127.0.0.1:9/mcp", "--token-env", "PROBE_KEY",
                                       "--timeout", "2"], {"PROBE_KEY": "granted"})
        self.assertEqual(code, 2)
        self.assertIn("cannot reach", err)


class OtlpCasesTest(unittest.TestCase):
    def test_every_claude_case_carries_identifiers_and_a_unique_marker(self):
        cases = otlp_cases.build_cases("example-org", keep_claude_logs=False)
        payload = json.dumps(otlp_cases.build_payloads(cases, 1_000_000_000_000))
        self.assertEqual(len({case.marker for case in cases}), len(cases))
        for case in cases:
            self.assertIn(case.marker, payload)
        self.assertIn(otlp_cases.SYNTHETIC_IDENTIFIERS["user.email"], payload)

    def test_careful_collector_output_has_no_findings(self):
        code, out, _ = run(otlp_cases, ["check", str(FIXTURES / "collector-careful.log"),
                                        "--org", "example-org", "--expect-stripped"])
        self.assertEqual(code, 0, out)

    def test_careless_collector_output_fires_every_finding_kind(self):
        code, out, _ = run(otlp_cases, ["check", str(FIXTURES / "collector-careless.log"),
                                        "--org", "example-org", "--expect-stripped", "--json"])
        self.assertEqual(code, 1)
        found = sorted(f"{item['kind']}:{item['case']}" for item in json.loads(out)["findings"])
        expected = sorted(line.strip() for line in (FIXTURES / "collector-careless.expect").read_text().splitlines()
                          if line.strip())
        self.assertEqual(found, expected)
        self.assertEqual({key.split(":")[0] for key in found}, {"leak", "overblock", "identifier"})

    def test_keeping_claude_logs_turns_the_dropped_event_into_an_overblock(self):
        code, out, _ = run(otlp_cases, ["check", str(FIXTURES / "collector-careful.log"),
                                        "--org", "example-org", "--keep-claude-logs", "--json"])
        self.assertEqual(code, 1)
        self.assertEqual([item["case"] for item in json.loads(out)["findings"]], ["claude-log"])

    def test_output_without_markers_is_unusable(self):
        stdin = sys.stdin
        sys.stdin = io.StringIO("level=info msg=Metrics resource_metrics=4\n")
        try:
            code, _, err = run(otlp_cases, ["check", "-", "--org", "example-org"])
        finally:
            sys.stdin = stdin
        self.assertEqual(code, 2)
        self.assertIn("verbosity", err)

    def test_send_posts_metrics_and_logs_as_otlp_json(self):
        server = start(StubOtlpReceiver)
        try:
            code, out, _ = run(otlp_cases, ["send", "--org", "example-org",
                                            "--endpoint", f"http://127.0.0.1:{server.server_address[1]}"])
        finally:
            stop(server)
        self.assertEqual(code, 0, out)
        self.assertEqual([path for path, _, _ in server.requests], ["/v1/metrics", "/v1/logs"])
        self.assertTrue(all(content_type == "application/json" for _, content_type, _ in server.requests))
        self.assertEqual(len(server.requests[0][2]["resourceMetrics"]), 9)

    def test_send_to_nothing_is_unusable(self):
        code, _, err = run(otlp_cases, ["send", "--org", "example-org", "--endpoint", "http://127.0.0.1:9",
                                        "--timeout", "2"])
        self.assertEqual(code, 2)
        self.assertIn("cannot reach", err)


if __name__ == "__main__":
    unittest.main()
