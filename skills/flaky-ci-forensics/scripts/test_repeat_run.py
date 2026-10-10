import importlib.util
import io
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("repeat_run", HERE / "repeat_run.py")
repeat_run = importlib.util.module_from_spec(spec)
sys.modules["repeat_run"] = repeat_run
spec.loader.exec_module(repeat_run)

PYTHON = sys.executable


def run(arguments):
    out, err = io.StringIO(), io.StringIO()
    code = repeat_run.main(arguments, out=out, err=err)
    return code, out.getvalue(), err.getvalue()


class RepeatRunTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.log_dir = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def test_every_run_passing_with_the_required_count(self):
        code, out, _ = run(["-n", "4", "-j", "2", "--require", r"tests 39\b", "--log-dir", str(self.log_dir), "--",
                            PYTHON, "-c", "print('ℹ tests 39')"])
        self.assertEqual(code, 0)
        self.assertIn("runs 4  pass 4  fail 0  timeout 0  missing 0", out)
        self.assertEqual(list(self.log_dir.iterdir()), [])

    def test_failures_are_counted_and_their_logs_kept(self):
        script = "import os, sys; index = int(os.environ['REPEAT_RUN_INDEX']); print('assertion failed' if index % 2 else 'ok'); sys.exit(index % 2)"
        code, out, _ = run(["-n", "4", "--log-dir", str(self.log_dir), "--", PYTHON, "-c", script])
        self.assertEqual(code, 1)
        self.assertIn("pass 2  fail 2", out)
        self.assertEqual(sorted(path.name for path in self.log_dir.iterdir()), ["run-0001.log", "run-0003.log"])
        self.assertIn("run 1: fail", out)
        self.assertIn("assertion failed", out)

    def test_a_hung_run_is_killed_with_its_children(self):
        started = time.monotonic()
        code, out, _ = run(["-n", "1", "--timeout", "0.5", "--log-dir", str(self.log_dir), "--",
                            "sh", "-c", "sleep 30 & sleep 30; wait"])
        self.assertEqual(code, 1)
        self.assertIn("timeout 1", out)
        self.assertLess(time.monotonic() - started, 10)

    def test_a_green_run_that_reports_too_few_tests_is_missing(self):
        code, out, _ = run(["-n", "2", "--require", r"tests 39\b", "--log-dir", str(self.log_dir), "--",
                            PYTHON, "-c", "print('ℹ tests 29')"])
        self.assertEqual(code, 1)
        self.assertIn("pass 0  fail 0  timeout 0  missing 2", out)

    def test_a_command_that_cannot_start_fails(self):
        code, out, _ = run(["-n", "1", "--log-dir", str(self.log_dir), "--", str(self.log_dir / "no-such-binary")])
        self.assertEqual(code, 1)
        self.assertIn("cannot start", out)

    def test_invalid_required_pattern_is_an_error(self):
        code, _, err = run(["--require", "(", "--", PYTHON, "-c", "pass"])
        self.assertEqual(code, 2)
        self.assertIn("--require", err)


if __name__ == "__main__":
    unittest.main()
