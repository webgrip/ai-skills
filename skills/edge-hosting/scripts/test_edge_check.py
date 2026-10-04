import importlib.util
import sys
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("edge_check", Path(__file__).resolve().parent / "edge_check.py")
edge_check = importlib.util.module_from_spec(spec)
sys.modules["edge_check"] = edge_check
spec.loader.exec_module(edge_check)
Probe = edge_check.Probe

HEALTHY = {"server": "cloudflare", "strict-transport-security": "max-age=31536000", "x-content-type-options": "nosniff",
           "content-security-policy": "frame-ancestors 'none'"}


def fetcher(responses):
    def fetch(url, timeout):
        for prefix, (status, headers, error) in responses.items():
            if url.startswith(prefix):
                return Probe(url, status, headers, 0.1, error)
        return Probe(url, 404, {"server": "cloudflare"}, 0.1)
    return fetch


def rules(findings):
    return sorted({f.rule for f in findings})


class LiveTest(unittest.TestCase):
    def test_healthy_apex_with_permanent_www_redirect(self):
        fetch = fetcher({
            "https://example.org/edge-check-": (404, HEALTHY, None),
            "https://example.org/": (200, HEALTHY, None),
            "https://www.example.org/": (301, {"location": "https://example.org/", "server": "cloudflare"}, None),
        })
        self.assertEqual(rules(edge_check.check_live(["example.org"], 5, True, fetch)), [])

    def test_proxied_www_with_no_claimant_is_origin_unreachable(self):
        fetch = fetcher({
            "https://example.org/edge-check-": (404, HEALTHY, None),
            "https://example.org/": (200, HEALTHY, None),
            "https://www.example.org/": (522, {"server": "cloudflare"}, None),
        })
        self.assertEqual(rules(edge_check.check_live(["example.org"], 5, True, fetch)), ["origin-unreachable"])

    def test_timeout_is_no_response(self):
        fetch = fetcher({"https://example.org/": (None, {}, "timeout")})
        self.assertIn("no-response", rules(edge_check.check_live(["example.org"], 5, False, fetch)))

    def test_both_hosts_serving_is_duplicate_content(self):
        fetch = fetcher({
            "https://example.org/edge-check-": (404, HEALTHY, None),
            "https://example.org/": (200, HEALTHY, None),
            "https://www.example.org/": (200, HEALTHY, None),
        })
        self.assertIn("www-apex-both-serve", rules(edge_check.check_live(["example.org"], 5, True, fetch)))

    def test_temporary_canonical_redirect_is_noted(self):
        fetch = fetcher({
            "https://example.org/edge-check-": (404, HEALTHY, None),
            "https://example.org/": (200, HEALTHY, None),
            "https://www.example.org/": (302, {"location": "https://example.org/", "server": "cloudflare"}, None),
        })
        self.assertEqual(rules(edge_check.check_live(["example.org"], 5, True, fetch)), ["canonical-redirect-temporary"])

    def test_spa_fallback_on_random_path_is_soft_404(self):
        fetch = fetcher({"https://example.org/": (200, HEALTHY, None)})
        fetch_all_200 = lambda url, timeout: Probe(url, 200, HEALTHY, 0.1)
        self.assertIn("soft-404", rules(edge_check.check_live(["example.org"], 5, False, fetch_all_200)))

    def test_missing_hsts_is_excused_on_preloaded_tld(self):
        headers = {k: v for k, v in HEALTHY.items() if k != "strict-transport-security"}
        dev = fetcher({"https://example.dev/edge-check-": (404, headers, None), "https://example.dev/": (200, headers, None)})
        org = fetcher({"https://example.org/edge-check-": (404, headers, None), "https://example.org/": (200, headers, None)})
        self.assertEqual(rules(edge_check.check_live(["example.dev"], 5, False, dev)), [])
        self.assertEqual(rules(edge_check.check_live(["example.org"], 5, False, org)), ["hsts-missing"])


class JsoncTest(unittest.TestCase):
    def test_comments_and_trailing_commas_strip_but_strings_survive(self):
        text = '{\n  // c\n  "a": "x//y", /* b */ "u": "https://e/*z*/",\n  "l": [1,2,],\n}'
        self.assertEqual(edge_check.json.loads(edge_check.strip_jsonc(text)), {"a": "x//y", "u": "https://e/*z*/", "l": [1, 2]})


if __name__ == "__main__":
    unittest.main()
