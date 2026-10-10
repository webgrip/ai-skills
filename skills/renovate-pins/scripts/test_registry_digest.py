import contextlib
import hashlib
import importlib.util
import io
import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

spec = importlib.util.spec_from_file_location("registry_digest", Path(__file__).resolve().parent / "registry_digest.py")
registry_digest = importlib.util.module_from_spec(spec)
sys.modules["registry_digest"] = registry_digest
spec.loader.exec_module(registry_digest)

INDEX_BODY = b'{"schemaVersion":2,"manifests":[]}'
INDEX_DIGEST = "sha256:" + hashlib.sha256(INDEX_BODY).hexdigest()
TOKEN = "anonymous-pull-token"


class FakeRegistry(BaseHTTPRequestHandler):
    tags = {
        "team/app": {"1.2.3": True, "no-digest-header": False},
    }
    basic_only = {"private/app"}

    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path.startswith("/token"):
            self.reply(200, json.dumps({"token": TOKEN}).encode(), {"Content-Type": "application/json"})
            return
        self.serve_manifest(include_body=True)

    def do_HEAD(self):
        self.serve_manifest(include_body=False)

    def serve_manifest(self, include_body):
        repository, _, reference = self.path[len("/v2/"):].partition("/manifests/")
        if repository in self.basic_only:
            self.reply(401, b"", {"WWW-Authenticate": 'Basic realm="registry"'})
            return
        if self.headers.get("Authorization") != f"Bearer {TOKEN}":
            realm = f"http://{self.headers['Host']}/token"
            self.reply(401, b"", {"WWW-Authenticate": f'Bearer realm="{realm}",service="fake"'})
            return
        tags = self.tags.get(repository, {})
        if reference not in tags:
            self.reply(404, b"", {})
            return
        headers = {"Content-Type": registry_digest.INDEX_MEDIA_TYPES[0]}
        if tags[reference]:
            headers["Docker-Content-Digest"] = INDEX_DIGEST
        self.reply(200, INDEX_BODY if include_body else b"", headers, len(INDEX_BODY))

    def reply(self, status, body, headers, length=None):
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(body) if length is None else length))
        self.end_headers()
        if body:
            self.wfile.write(body)


class RegistryDigestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeRegistry)
        cls.host = f"127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def check(self, reference):
        return registry_digest.check(f"{self.host}/{reference}", timeout=5)

    def test_published_tag_prints_index_digest(self):
        code, line = self.check("team/app:1.2.3")
        self.assertEqual(code, registry_digest.EXIT_FOUND)
        self.assertIn(INDEX_DIGEST, line)
        self.assertIn("multi-arch index", line)

    def test_missing_digest_header_is_computed_from_the_body(self):
        code, line = self.check("team/app:no-digest-header")
        self.assertEqual(code, registry_digest.EXIT_FOUND)
        self.assertIn(INDEX_DIGEST, line)

    def test_absent_tag(self):
        code, _ = self.check("team/app:9.9.9")
        self.assertEqual(code, registry_digest.EXIT_ABSENT)

    def test_pin_that_no_longer_matches_the_tag(self):
        stale = "sha256:" + "ab" * 32
        code, line = self.check(f"team/app:1.2.3@{stale}")
        self.assertEqual(code, registry_digest.EXIT_PIN_DIFFERS)
        self.assertIn("differs", line)

    def test_pin_that_matches_the_tag(self):
        code, _ = self.check(f"team/app:1.2.3@{INDEX_DIGEST}")
        self.assertEqual(code, registry_digest.EXIT_FOUND)

    def test_registry_without_anonymous_pull_is_an_error(self):
        with self.assertRaises(registry_digest.RegistryError):
            self.check("private/app:1.0.0")

    def test_main_returns_highest_exit_code(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = registry_digest.main([f"{self.host}/team/app:1.2.3", f"{self.host}/team/app:9.9.9"])
        self.assertEqual(code, registry_digest.EXIT_ABSENT)


class ParseImageReferenceTest(unittest.TestCase):
    def test_docker_hub_official_image(self):
        reference = registry_digest.parse_image_reference("nginx:1.27")
        self.assertEqual((reference.registry, reference.repository, reference.tag),
                         ("registry-1.docker.io", "library/nginx", "1.27"))

    def test_registry_with_port_and_no_tag(self):
        reference = registry_digest.parse_image_reference("localhost:5000/team/app")
        self.assertEqual((reference.registry, reference.repository, reference.manifest_reference),
                         ("localhost:5000", "team/app", "latest"))

    def test_digest_only(self):
        digest = "sha256:" + "cd" * 32
        reference = registry_digest.parse_image_reference(f"ghcr.io/owner/app@{digest}")
        self.assertEqual((reference.tag, reference.manifest_reference), (None, digest))

    def test_rejects_a_malformed_digest(self):
        with self.assertRaises(registry_digest.RegistryError):
            registry_digest.parse_image_reference("ghcr.io/owner/app@sha256:short")


if __name__ == "__main__":
    unittest.main()
