#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

OUTCOMES = ("pass", "fail", "timeout", "missing")
FAILURES_SHOWN = 5
KILL_GRACE_SECONDS = 5


@dataclass
class RunResult:
    index: int
    outcome: str
    exit_code: Optional[int]
    seconds: float
    log: Path


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"expected a whole number, got {value!r}") from error
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def positive_seconds(value: str) -> float:
    try:
        number = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"expected seconds, got {value!r}") from error
    if number <= 0:
        raise argparse.ArgumentTypeError("must be more than 0")
    return number


def load_average() -> str:
    try:
        return "{:.1f}".format(os.getloadavg()[0])
    except (AttributeError, OSError):
        return "n/a"


def kill_group(process: subprocess.Popen) -> None:
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        return


class LiveProcesses:
    def __init__(self):
        self.lock = threading.Lock()
        self.processes = set()

    def add(self, process: subprocess.Popen) -> None:
        with self.lock:
            self.processes.add(process)

    def discard(self, process: subprocess.Popen) -> None:
        with self.lock:
            self.processes.discard(process)

    def kill_all(self) -> None:
        with self.lock:
            for process in list(self.processes):
                kill_group(process)


def run_once(index: int, command: List[str], timeout: float, required: Optional[re.Pattern], log_dir: Path,
             live: LiveProcesses) -> RunResult:
    log = log_dir / f"run-{index:04d}.log"
    environment = dict(os.environ, REPEAT_RUN_INDEX=str(index))
    started = time.monotonic()
    with log.open("wb") as output:
        try:
            process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                       env=environment, start_new_session=True)
        except OSError as error:
            output.write(f"cannot start {command[0]}: {error}\n".encode())
            return RunResult(index, "fail", None, 0.0, log)
        live.add(process)
        try:
            exit_code: Optional[int] = process.wait(timeout=timeout)
            outcome = "pass" if exit_code == 0 else "fail"
        except subprocess.TimeoutExpired:
            kill_group(process)
            process.wait(timeout=KILL_GRACE_SECONDS)
            exit_code, outcome = None, "timeout"
        finally:
            live.discard(process)
    if outcome == "pass" and required and not required.search(log.read_text(errors="replace")):
        outcome = "missing"
    return RunResult(index, outcome, exit_code, time.monotonic() - started, log)


def last_line(path: Path) -> str:
    lines = [line.strip() for line in path.read_text(errors="replace").splitlines() if line.strip()]
    return lines[-1][:200] if lines else "(no output)"


def parse_arguments(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one command many times with a per-run timeout and report pass, fail, timeout and "
        "missing-output counts. Each run gets REPEAT_RUN_INDEX in its environment.",
        usage="%(prog)s [-n RUNS] [-j PARALLEL] [--timeout SECONDS] [--require REGEX] [--log-dir DIR] -- command ...",
    )
    parser.add_argument("-n", "--runs", type=positive_int, default=20)
    parser.add_argument("-j", "--parallel", type=positive_int, default=1,
                        help="concurrent runs; only for commands that isolate their state per REPEAT_RUN_INDEX")
    parser.add_argument("--timeout", type=positive_seconds, default=600.0, help="seconds per run (default 600)")
    parser.add_argument("--require", help="regular expression a passing run's output must contain, such as a test count")
    parser.add_argument("--log-dir", type=Path, help="where to keep logs of runs that did not pass")
    parser.add_argument("--keep-all", action="store_true", help="keep logs of passing runs too")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    arguments = parser.parse_args(argv)
    if arguments.command[:1] == ["--"]:
        arguments.command = arguments.command[1:]
    if not arguments.command:
        parser.error("give the command after --")
    return arguments


def main(argv: Optional[List[str]] = None, out=sys.stdout, err=sys.stderr) -> int:
    arguments = parse_arguments(sys.argv[1:] if argv is None else argv)
    try:
        required = re.compile(arguments.require) if arguments.require else None
    except re.error as error:
        print(f"repeat_run: --require is not a valid regular expression: {error}", file=err)
        return 2
    log_dir = arguments.log_dir or Path(tempfile.mkdtemp(prefix="repeat-run-"))
    log_dir.mkdir(parents=True, exist_ok=True)
    load_before = load_average()
    live = LiveProcesses()
    pool = ThreadPoolExecutor(max_workers=arguments.parallel)
    try:
        results = list(pool.map(
            lambda index: run_once(index, arguments.command, arguments.timeout, required, log_dir, live),
            range(1, arguments.runs + 1),
        ))
    except KeyboardInterrupt:
        pool.shutdown(wait=False, cancel_futures=True)
        live.kill_all()
        print(f"repeat_run: interrupted; logs so far in {log_dir}", file=err)
        return 130
    pool.shutdown()
    counts = {outcome: sum(1 for result in results if result.outcome == outcome) for outcome in OUTCOMES}
    for result in results:
        if result.outcome == "pass" and not arguments.keep_all:
            result.log.unlink()
    slowest = max(result.seconds for result in results)
    print(
        f"runs {len(results)}  pass {counts['pass']}  fail {counts['fail']}  timeout {counts['timeout']}"
        f"  missing {counts['missing']}  slowest {slowest:.1f}s  load {load_before} -> {load_average()}"
        f"  parallel {arguments.parallel}",
        file=out,
    )
    not_passed = [result for result in results if result.outcome != "pass"]
    for result in not_passed[:FAILURES_SHOWN]:
        print(f"  run {result.index}: {result.outcome}  {result.log}  {last_line(result.log)}", file=out)
    if len(not_passed) > FAILURES_SHOWN:
        print(f"  ... {len(not_passed) - FAILURES_SHOWN} more in {log_dir}", file=out)
    if not not_passed and not arguments.keep_all and arguments.log_dir is None:
        log_dir.rmdir()
    return 0 if not not_passed else 1


if __name__ == "__main__":
    sys.exit(main())
