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
from unittest import mock

SKILL = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("grafana_access_audit", SKILL / "scripts" / "grafana_access_audit.py")
audit = importlib.util.module_from_spec(spec)
sys.modules["grafana_access_audit"] = audit
spec.loader.exec_module(audit)

ADMIN = "admin:fixture-password"


def replaying_handler(routes):
    class ReplayingGrafana(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            org = self.headers.get("X-Grafana-Org-Id")
            route = routes.get(f"{self.path} @{org}") if org else routes.get(self.path)
            if route is None:
                self.reply(404, {"message": "Not found"})
            else:
                self.reply(route["status"], route["body"])

        def reply(self, status, body):
            payload = json.dumps(body).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    return ReplayingGrafana


@contextlib.contextmanager
def fake_grafana(routes):
    server = ThreadingHTTPServer(("127.0.0.1", 0), replaying_handler(routes))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def fixture_routes(name):
    return json.loads((SKILL / "fixtures" / f"{name}.json").read_text())["routes"]


def run(arguments, credentials=ADMIN):
    output = io.StringIO()
    environment = {audit.AUTH_ENVIRONMENT_VARIABLE: credentials} if credentials else {}
    with mock.patch.dict(os.environ, environment, clear=True), contextlib.redirect_stdout(output), \
            contextlib.redirect_stderr(io.StringIO()):
        code = audit.main(arguments)
    return code, output.getvalue()


class FixtureAuditTest(unittest.TestCase):
    def test_careless_instance_fires_every_rule(self):
        expected = {line.strip() for line in (SKILL / "fixtures" / "careless.expect").read_text().splitlines()
                    if line.strip()}
        with fake_grafana(fixture_routes("careless")) as url:
            code, output = run(["--url", url, "--kiosk-login", "^tv-", "--health", "--json"])
        found = {finding["rule"] for finding in json.loads(output)["findings"]}
        self.assertEqual(code, audit.EXIT_FINDINGS)
        self.assertEqual(found, expected)

    def test_careful_instance_is_clean(self):
        with fake_grafana(fixture_routes("careful")) as url:
            code, output = run(["--url", url, "--kiosk-login", "^tv-", "--json"])
        self.assertEqual(json.loads(output)["findings"], [])
        self.assertEqual(code, audit.EXIT_CLEAN)

    def test_inventory_names_credentials_every_member_can_use(self):
        with fake_grafana(fixture_routes("careful")) as url:
            _, output = run(["--url", url])
        self.assertIn("holds basicAuthPassword usable by all 2 members", output)

    def test_non_admin_credentials_stop_the_audit(self):
        routes = dict(fixture_routes("careful"))
        routes["/api/admin/settings"] = {"status": 403, "body": {"message": "Access denied"}}
        with fake_grafana(routes) as url:
            code, _ = run(["--url", url])
        self.assertEqual(code, audit.EXIT_ERROR)

    def test_missing_credentials(self):
        code, _ = run(["--url", "http://127.0.0.1:9"], credentials=None)
        self.assertEqual(code, audit.EXIT_ERROR)

    def test_unreachable_grafana(self):
        code, _ = run(["--url", "http://127.0.0.1:9", "--timeout", "2"])
        self.assertEqual(code, audit.EXIT_ERROR)


class OrgMappingTest(unittest.TestCase):
    def test_space_and_comma_separated_entries_with_default_role(self):
        self.assertEqual(audit.org_mapping_entries("staff:1:Editor, scope-b:2 *:3:Viewer"),
                         [("staff", "1", "Editor"), ("scope-b", "2", "Viewer"), ("*", "3", "Viewer")])

    def test_escaped_colon_stays_in_the_group_name(self):
        self.assertEqual(audit.org_mapping_entries(r"team\:ops:2:Viewer"), [(r"team\:ops", "2", "Viewer")])

    def test_numeric_mapping_with_empty_fallback_raises_nothing(self):
        settings = {"auth.generic_oauth": {"org_mapping": "a:1:Editor b:2:Viewer",
                                           "role_attribute_path": "contains(groups, 'admins') && 'GrafanaAdmin' || ''"}}
        self.assertEqual(audit.settings_findings(settings), [])


if __name__ == "__main__":
    unittest.main()
