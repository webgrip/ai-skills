import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SHARE = Path(__file__).resolve().parent.parent / "share.py"
spec = importlib.util.spec_from_file_location("share", SHARE)
share = importlib.util.module_from_spec(spec)
sys.modules["share"] = share
spec.loader.exec_module(share)

NOW = 1_790_000_000
SETTINGS = share.Settings("acct", "share.example.org", "ns", "me@example.org", "720h")


class FakeApi:
    def __init__(self, fail_on=None):
        self.calls = []
        self.apps = {}
        self.policies = {}
        self.kv = {}
        self.fail_on = fail_on

    def call(self, method, path, body=None, raw=None, content_type=None):
        self.calls.append((method, path.split("?")[0]))
        if self.fail_on and self.fail_on == (method, path.split("?")[0].rsplit("/", 1)[-1]):
            raise share.ApiError(f"injected failure on {method} {path}")
        if method == "POST" and path.endswith("/access/policies"):
            policy = {"id": f"pol-{len(self.policies)}", **body}
            self.policies[policy["id"]] = policy
            return {"result": policy}
        if method == "POST" and path.endswith("/access/apps"):
            app = {"id": f"app-{len(self.apps)}", "aud": f"aud-{len(self.apps)}", **body,
                   "policies": [{"id": p["id"], "name": self.policies[p["id"]]["name"]} for p in body["policies"]]}
            self.apps[app["id"]] = app
            return {"result": app}
        if method == "GET" and "/access/apps" in path:
            return {"result": list(self.apps.values()), "result_info": {"total_pages": 1}}
        if method == "DELETE" and "/access/apps/" in path:
            return {"result": self.apps.pop(path.rsplit("/", 1)[-1], None)}
        if method == "DELETE" and "/access/policies/" in path:
            return {"result": self.policies.pop(path.rsplit("/", 1)[-1], None)}
        if method == "PUT" and "/values/" in path:
            key = path.split("?")[0].rsplit("/", 1)[-1]
            text = raw.decode()
            metadata = json.loads(text.split("application/json\r\n\r\n", 1)[1].split("\r\n", 1)[0])
            self.kv[key] = {"metadata": metadata, "expiration": int(path.split("expiration=")[1]), "raw": text}
            return {"result": {}}
        if method == "GET" and "/metadata/" in path:
            entry = self.kv.get(path.rsplit("/", 1)[-1])
            return {"result": entry["metadata"]} if entry else None
        if method == "DELETE" and "/values/" in path:
            self.kv.pop(path.rsplit("/", 1)[-1], None)
            return {"result": {}}
        raise AssertionError(f"unexpected call {method} {path}")


def page(tmp: Path) -> Path:
    path = tmp / "briefing.html"
    path.write_text("<h1>briefing</h1>")
    return path


class PublishTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_gate_goes_up_before_content(self):
        api = FakeApi()
        url = share.publish(api, SETTINGS, page(self.tmp), ["alex@example.org"], [], 30 * 86400, None, NOW)
        order = [c for c in api.calls if c[0] in ("POST", "PUT")]
        self.assertEqual([c[0] for c in order], ["POST", "POST", "PUT"])
        self.assertTrue(order[1][1].endswith("/access/apps"))
        name = url.rsplit("/", 1)[-1]
        self.assertRegex(name, r"^[a-f0-9]{24}$")
        self.assertEqual(url, f"https://share.example.org/p/{name}")

    def test_page_metadata_carries_expiry_and_the_apps_audience(self):
        api = FakeApi()
        name = share.publish(api, SETTINGS, page(self.tmp), ["alex@example.org"], [], 3600, None, NOW).rsplit("/", 1)[-1]
        entry = api.kv[name]
        self.assertEqual(entry["metadata"], {"expires": NOW + 3600, "aud": "aud-0"})
        self.assertEqual(entry["expiration"], NOW + 3600 + share.GRACE_SECONDS)
        self.assertIn("<h1>briefing</h1>", entry["raw"])

    def test_policy_admits_recipients_domains_and_the_owner_once(self):
        api = FakeApi()
        share.publish(api, SETTINGS, page(self.tmp), ["alex@example.org", "me@example.org"], ["client.example"], 3600, None, NOW)
        include = next(iter(api.policies.values()))["include"]
        self.assertEqual(include, [
            {"email": {"email": "alex@example.org"}},
            {"email": {"email": "me@example.org"}},
            {"email_domain": {"domain": "client.example"}},
        ])

    def test_app_is_scoped_to_the_exact_page_path(self):
        api = FakeApi()
        name = share.publish(api, SETTINGS, page(self.tmp), ["alex@example.org"], [], 3600, None, NOW).rsplit("/", 1)[-1]
        app = next(iter(api.apps.values()))
        self.assertEqual(app["domain"], f"share.example.org/p/{name}")
        self.assertEqual(app["destinations"], [{"type": "public", "uri": f"share.example.org/p/{name}"}])
        self.assertEqual(app["policies"][0]["id"], "pol-0")

    def test_new_page_without_recipients_is_refused_before_any_write(self):
        api = FakeApi()
        with self.assertRaises(share.ApiError):
            share.publish(api, SETTINGS, page(self.tmp), [], [], 3600, None, NOW)
        self.assertEqual(api.calls, [])

    def test_failed_app_creation_removes_the_orphan_policy_and_uploads_nothing(self):
        api = FakeApi(fail_on=("POST", "apps"))
        with self.assertRaises(share.ApiError):
            share.publish(api, SETTINGS, page(self.tmp), ["alex@example.org"], [], 3600, None, NOW)
        self.assertEqual(api.policies, {})
        self.assertEqual(api.kv, {})

    def test_republish_keeps_the_link_and_gate_and_replaces_content(self):
        api = FakeApi()
        url = share.publish(api, SETTINGS, page(self.tmp), ["alex@example.org"], [], 3600, None, NOW)
        name = url.rsplit("/", 1)[-1]
        again = share.publish(api, SETTINGS, page(self.tmp), [], [], 7200, name, NOW + 10)
        self.assertEqual(again, url)
        self.assertEqual(len(api.apps), 1)
        self.assertEqual(api.kv[name]["metadata"]["expires"], NOW + 10 + 7200)

    def test_republish_of_unknown_page_is_refused(self):
        with self.assertRaises(share.ApiError):
            share.publish(FakeApi(), SETTINGS, page(self.tmp), [], [], 3600, "0" * 24, NOW)


class RevokeAndSweepTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_revoke_deletes_content_before_the_gate(self):
        api = FakeApi()
        name = share.publish(api, SETTINGS, page(self.tmp), ["alex@example.org"], [], 3600, None, NOW).rsplit("/", 1)[-1]
        api.calls.clear()
        share.revoke(api, SETTINGS, name)
        deletes = [c[1] for c in api.calls if c[0] == "DELETE"]
        self.assertIn("/values/", deletes[0])
        self.assertEqual((api.apps, api.policies, api.kv), ({}, {}, {}))

    def test_half_revoked_page_is_finished_by_sweep(self):
        api = FakeApi()
        name = share.publish(api, SETTINGS, page(self.tmp), ["alex@example.org"], [], 3600, None, NOW).rsplit("/", 1)[-1]
        api.fail_on = ("DELETE", api.apps["app-0"]["id"])
        with self.assertRaises(share.ApiError):
            share.revoke(api, SETTINGS, name)
        self.assertEqual(api.kv, {})
        api.fail_on = None
        self.assertEqual(share.sweep(api, SETTINGS, NOW), [name])
        self.assertEqual(api.apps, {})

    def test_sweep_revokes_expired_and_keeps_live_pages(self):
        api = FakeApi()
        live = share.publish(api, SETTINGS, page(self.tmp), ["a@example.org"], [], 30 * 86400, None, NOW).rsplit("/", 1)[-1]
        dead = share.publish(api, SETTINGS, page(self.tmp), ["b@example.org"], [], 60, None, NOW).rsplit("/", 1)[-1]
        self.assertEqual(share.sweep(api, SETTINGS, NOW + 3600), [dead])
        self.assertIn(live, api.kv)
        self.assertEqual([a["name"] for a in api.apps.values()], [f"share-{live}"])


class DurationTest(unittest.TestCase):
    def test_units(self):
        self.assertEqual(share.parse_duration("30d"), 30 * 86400)
        self.assertEqual(share.parse_duration("12h"), 12 * 3600)
        with self.assertRaises(Exception):
            share.parse_duration("30 days")


if __name__ == "__main__":
    unittest.main()
