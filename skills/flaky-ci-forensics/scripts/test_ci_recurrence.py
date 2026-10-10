import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURES = HERE.parent / "fixtures" / "forge"
spec = importlib.util.spec_from_file_location("ci_recurrence", HERE / "ci_recurrence.py")
ci_recurrence = importlib.util.module_from_spec(spec)
sys.modules["ci_recurrence"] = ci_recurrence
spec.loader.exec_module(ci_recurrence)


class FixtureTransport:
    def __init__(self, name, overrides=None):
        recorded = json.loads((FIXTURES / name).read_text())
        self.responses = dict(recorded["responses"])
        self.responses.update(overrides or {})
        self.requested = []
        self.headers_seen = []

    def __call__(self, url, headers):
        self.requested.append(url)
        self.headers_seen.append(dict(headers))
        if url not in self.responses:
            raise AssertionError(f"unrecorded request: {url}")
        entry = self.responses[url]
        body = json.dumps(entry["json"]) if "json" in entry else entry.get("text", "")
        return ci_recurrence.Response(entry["status"], entry.get("headers", {}), body.encode("utf-8"))


def run(arguments, transport, environment=None):
    out, err = io.StringIO(), io.StringIO()
    code = ci_recurrence.main(arguments, transport=transport, environment=environment or {}, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


GITLAB = ["gitlab", "--project", "example/app", "--api-url", "https://gitlab.example.com/api/v4",
          "--job", "phpunit", "--since", "2026-09-01"]
GITHUB = ["github", "--repo", "example/app", "--workflow", "ci.yml", "--api-url", "https://api.github.com",
          "--job", r"test \(.*\)", "--since", "2026-09-01"]
CURRENCY_TEST = "CurrencyConversionTest > converts every order line"
RETRY_ASSERTION = "AssertionError: expected 3 retries, got 4"


class GitLabRecurrenceTest(unittest.TestCase):
    def test_counts_the_assertion_across_merge_requests_and_trunk(self):
        transport = FixtureTransport("gitlab.json")
        code, out, _ = run(GITLAB + ["--grep", CURRENCY_TEST, "--json"], transport, {"GITLAB_TOKEN": "glpat-example"})
        report = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual([m["job"]["job_id"] for m in report["matches"]], [5108, 5106, 5105])
        self.assertEqual(report["listed"], 6)
        self.assertEqual(report["scanned"], 5)
        self.assertEqual(report["unavailable"], [5103])
        summary = report["summary"]
        self.assertEqual(summary["merge requests"], ["!19", "!23"])
        self.assertEqual(summary["branches"], {"main": 1})
        self.assertEqual(summary["pipelines"], 3)
        self.assertEqual((summary["first"], summary["last"]), ("2026-09-21", "2026-10-08"))
        self.assertEqual(len(summary["image_digests"]), 1)
        self.assertTrue(summary["image_digests"][0].startswith("registry.example.com/example/app/testing@sha256:a1a1"))

    def test_skips_other_job_names_and_stops_at_the_since_date(self):
        transport = FixtureTransport("gitlab.json")
        run(GITLAB + ["--grep", CURRENCY_TEST], transport, {"GITLAB_TOKEN": "glpat-example"})
        fetched_logs = [url.rsplit("/", 2)[-2] for url in transport.requested if url.endswith("/trace")]
        self.assertEqual(fetched_logs, ["5108", "5106", "5105", "5104", "5103"])
        self.assertTrue(all(h.get("PRIVATE-TOKEN") == "glpat-example" for h in transport.headers_seen))

    def test_text_output_strips_ansi_and_names_where_it_failed(self):
        code, out, _ = run(GITLAB + ["--grep", "2287 matches expected 1143"], FixtureTransport("gitlab.json"),
                           {"GITLAB_TOKEN": "glpat-example"})
        self.assertEqual(code, 0)
        self.assertNotIn("\x1b", out)
        self.assertIn("3 of 5 failed 'phpunit' jobs contain the text (6 failed jobs listed; logs unavailable: 1)", out)
        self.assertIn("2 merge requests (!19, !23), branch pipelines: main (1)", out)
        self.assertIn("    Failed asserting that 2287 matches expected 1143.", out)

    def test_text_that_never_appears_exits_one(self):
        code, out, _ = run(GITLAB + ["--grep", "SomeOtherTest > never fails"], FixtureTransport("gitlab.json"),
                           {"GITLAB_TOKEN": "glpat-example"})
        self.assertEqual(code, 1)
        self.assertIn("0 of 5 failed 'phpunit' jobs contain the text", out)

    def test_limit_caps_the_jobs_listed(self):
        code, out, _ = run(GITLAB + ["--grep", CURRENCY_TEST, "--limit", "2", "--json"], FixtureTransport("gitlab.json"),
                           {"GITLAB_TOKEN": "glpat-example"})
        report = json.loads(out)
        self.assertEqual((code, report["listed"], report["scanned"]), (0, 2, 1))

    def test_regex_mode(self):
        code, out, _ = run(GITLAB + ["--grep", r"Failed asserting that \d+ matches expected \d+", "--regex", "--json"],
                           FixtureTransport("gitlab.json"), {"GITLAB_TOKEN": "glpat-example"})
        self.assertEqual((code, len(json.loads(out)["matches"])), (0, 3))

    def test_missing_token_explains_and_never_prints_a_token(self):
        page = "https://gitlab.example.com/api/v4/projects/example%2Fapp/jobs?scope%5B%5D=failed&per_page=100"
        transport = FixtureTransport("gitlab.json", {page: {"status": 401, "text": "{\"message\":\"401 Unauthorized\"}"}})
        code, out, err = run(GITLAB + ["--grep", CURRENCY_TEST], transport, {"GITLAB_TOKEN": "glpat-secret-value"})
        self.assertEqual(code, 2)
        self.assertIn("GITLAB_TOKEN", err)
        self.assertNotIn("glpat-secret-value", err + out)

    def test_rate_limit_is_named(self):
        page = "https://gitlab.example.com/api/v4/projects/example%2Fapp/jobs?scope%5B%5D=failed&per_page=100"
        transport = FixtureTransport("gitlab.json", {page: {"status": 429, "text": "Retry later"}})
        code, _, err = run(GITLAB + ["--grep", CURRENCY_TEST], transport)
        self.assertEqual(code, 2)
        self.assertIn("rate limited", err)

    def test_log_dir_reuses_downloaded_logs(self):
        with tempfile.TemporaryDirectory() as directory:
            run(GITLAB + ["--grep", CURRENCY_TEST, "--log-dir", directory], FixtureTransport("gitlab.json"))
            self.assertTrue((Path(directory) / "gitlab-5108.log").exists())
            offline = FixtureTransport("gitlab.json")
            offline.responses = {url: entry for url, entry in offline.responses.items() if not url.endswith("/trace")}
            offline.responses["https://gitlab.example.com/api/v4/projects/example%2Fapp/jobs/5103/trace"] = {"status": 404, "text": ""}
            code, out, _ = run(GITLAB + ["--grep", CURRENCY_TEST, "--json", "--log-dir", directory], offline)
            self.assertEqual((code, len(json.loads(out)["matches"])), (0, 3))


class GitHubRecurrenceTest(unittest.TestCase):
    def test_counts_failed_attempts_hidden_by_a_green_rerun(self):
        transport = FixtureTransport("github.json")
        code, out, _ = run(GITHUB + ["--grep", RETRY_ASSERTION, "--json"], transport, {"GH_TOKEN": "ghp-example"})
        report = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual([m["job"]["job_id"] for m in report["matches"]], [9001, 8991])
        self.assertEqual(report["listed"], 3)
        self.assertEqual(report["scanned"], 4)
        self.assertEqual(report["unavailable"], [8981])
        summary = report["summary"]
        self.assertEqual(summary["pull requests"], ["#41"])
        self.assertEqual(summary["branches"], {"main": 1})
        self.assertEqual(summary["runs"], 2)
        self.assertEqual(summary["matches_without_digest"], 1)
        self.assertTrue(all(h.get("Authorization") == "Bearer ghp-example" for h in transport.headers_seen))

    def test_text_output_marks_a_failed_attempt_of_a_rerun(self):
        code, out, _ = run(GITHUB + ["--grep", RETRY_ASSERTION], FixtureTransport("github.json"), {"GITHUB_TOKEN": "ghp-example"})
        first, excerpt = out.splitlines()[:2]
        self.assertEqual(code, 0)
        self.assertIn("#41", first)
        self.assertIn("attempt 1/2", first)
        self.assertEqual(excerpt, "    E       AssertionError: expected 3 retries, got 4")
        self.assertIn("1 pull requests (#41), branch runs: main (1)", out)

    def test_nothing_matches_exits_one(self):
        code, out, _ = run(GITHUB + ["--grep", "ZeroDivisionError"], FixtureTransport("github.json"), {"GITHUB_TOKEN": "ghp-example"})
        self.assertEqual(code, 1)
        self.assertIn("0 of 4 failed", out)

    def test_forbidden_log_download_asks_for_a_token(self):
        transport = FixtureTransport("github.json", {
            "https://api.github.com/repos/example/app/actions/jobs/9001/logs": {"status": 403, "text": "{}"},
        })
        code, _, err = run(GITHUB + ["--grep", RETRY_ASSERTION], transport)
        self.assertEqual(code, 2)
        self.assertIn("GITHUB_TOKEN", err)


class TransportTest(unittest.TestCase):
    def test_credentials_are_not_forwarded_on_redirects(self):
        request = ci_recurrence.build_request("https://api.example.com/logs", {
            "Authorization": "Bearer secret", "PRIVATE-TOKEN": "secret", "Accept": "application/json"})
        self.assertNotIn("Authorization", request.headers)
        self.assertNotIn("Private-token", request.headers)
        self.assertTrue(request.has_header("Authorization"))
        self.assertTrue(request.has_header("Private-token"))
        self.assertIn("Accept", request.headers)


class CleaningTest(unittest.TestCase):
    def test_gitlab_markers_ansi_and_carriage_returns(self):
        raw = "\x1b[0Ksection_start:1:step\r\x1b[0Kfirst\r\nprogress 10%\rprogress 100%\r\n\x1b[31mred\x1b[0m\n"
        self.assertEqual(ci_recurrence.clean_lines(raw)[:3], ["first", "progress 100%", "red"])

    def test_github_timestamps(self):
        self.assertEqual(ci_recurrence.clean_lines("2026-10-02T08:15:01.1234567Z hello\n")[0], "hello")

    def test_mixed_precision_timestamps(self):
        self.assertEqual(ci_recurrence.parse_time("2026-10-08T09:12:44.512Z").microsecond, 512000)
        self.assertEqual(ci_recurrence.parse_time("2015-12-24T16:51:14.000+01:00").hour, 15)


if __name__ == "__main__":
    unittest.main()
