#!/usr/bin/env python3
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

CLAUDE_SERVICE = "claude-code"
OTHER_SERVICE = "probe-other-app"
CLAUDE_METRIC = "claude_code.cost.usage"
OTHER_METRIC = "probe.http.server.request.duration"
SYNTHETIC_IDENTIFIERS = {
    "user.email": "probe-user@example.invalid",
    "user.account_uuid": "00000000-0000-4000-8000-0000000000aa",
    "user.account_id": "user_probe0000000000aa",
}
MARKER_PATTERN = re.compile(r"probe-case-([a-z]+(?:-[a-z]+)*)")
EXIT_OK = 0
EXIT_MISMATCH = 1
EXIT_UNUSABLE = 2


@dataclass(frozen=True)
class Case:
    name: str
    signal: str
    service: str
    owner: Optional[str]
    owner_on: Optional[str]
    should_pass: bool

    @property
    def marker(self) -> str:
        return f"probe-case-{self.name}"


@dataclass(frozen=True)
class Finding:
    kind: str
    case: str
    detail: str

    @property
    def key(self) -> str:
        return f"{self.kind}:{self.case}"


def build_cases(org: str, keep_claude_logs: bool) -> List[Case]:
    return [
        Case("org-datapoint", "metrics", CLAUDE_SERVICE, org, "record", True),
        Case("org-resource", "metrics", CLAUDE_SERVICE, org, "resource", True),
        Case("org-subgroup", "metrics", CLAUDE_SERVICE, f"{org}/team/app", "record", True),
        Case("lookalike-suffix", "metrics", CLAUDE_SERVICE, f"{org}x", "record", False),
        Case("lookalike-prefix", "metrics", CLAUDE_SERVICE, f"x{org}", "record", False),
        Case("lookalike-nested", "metrics", CLAUDE_SERVICE, f"other-group/{org}", "record", False),
        Case("other-owner", "metrics", CLAUDE_SERVICE, "other-org", "record", False),
        Case("no-repo", "metrics", CLAUDE_SERVICE, None, None, False),
        Case("other-service-metric", "metrics", OTHER_SERVICE, None, None, True),
        Case("claude-log", "logs", CLAUDE_SERVICE, org, "record", keep_claude_logs),
        Case("claude-log-other-owner", "logs", CLAUDE_SERVICE, "other-org", "record", False),
        Case("other-service-log", "logs", OTHER_SERVICE, None, None, True),
    ]


def string_attribute(key: str, value: str) -> Dict[str, object]:
    return {"key": key, "value": {"stringValue": value}}


def resource_attributes(case: Case) -> List[Dict[str, object]]:
    attributes = [string_attribute("service.name", case.service)]
    if case.owner is not None and case.owner_on == "resource":
        attributes.append(string_attribute("vcs.owner.name", case.owner))
    return attributes


def record_attributes(case: Case) -> List[Dict[str, object]]:
    attributes = [string_attribute("probe.case", case.marker)]
    if case.service == CLAUDE_SERVICE:
        attributes += [string_attribute(key, value) for key, value in SYNTHETIC_IDENTIFIERS.items()]
    if case.owner is not None and case.owner_on == "record":
        attributes.append(string_attribute("vcs.owner.name", case.owner))
        attributes.append(string_attribute("vcs.repository.name", "probe-repo"))
    return attributes


def metric_entry(case: Case, value: float, now_nanos: int) -> Dict[str, object]:
    name = CLAUDE_METRIC if case.service == CLAUDE_SERVICE else OTHER_METRIC
    datapoint = {
        "asDouble": value,
        "startTimeUnixNano": str(now_nanos - 60_000_000_000),
        "timeUnixNano": str(now_nanos),
        "attributes": record_attributes(case),
    }
    return {
        "resource": {"attributes": resource_attributes(case)},
        "scopeMetrics": [{
            "scope": {"name": "probe.otlp_cases"},
            "metrics": [{
                "name": name,
                "unit": "USD" if case.service == CLAUDE_SERVICE else "s",
                "sum": {"aggregationTemporality": 2, "isMonotonic": True, "dataPoints": [datapoint]},
            }],
        }],
    }


def log_entry(case: Case, now_nanos: int) -> Dict[str, object]:
    record = {
        "timeUnixNano": str(now_nanos),
        "observedTimeUnixNano": str(now_nanos),
        "severityText": "INFO",
        "body": {"stringValue": case.marker},
        "attributes": record_attributes(case),
    }
    return {
        "resource": {"attributes": resource_attributes(case)},
        "scopeLogs": [{"scope": {"name": "probe.otlp_cases"}, "logRecords": [record]}],
    }


def build_payloads(cases: Sequence[Case], now_nanos: int) -> Dict[str, Dict[str, object]]:
    metrics = [metric_entry(case, 100.0 + index, now_nanos)
               for index, case in enumerate(cases) if case.signal == "metrics"]
    logs = [log_entry(case, now_nanos) for case in cases if case.signal == "logs"]
    return {"metrics": {"resourceMetrics": metrics}, "logs": {"resourceLogs": logs}}


def post_json(url: str, payload: Dict[str, object], timeout: float) -> int:
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.status


def describe(case: Case) -> str:
    owner = f'{case.owner_on} owner "{case.owner}"' if case.owner else "no repository attributes"
    return f"{case.signal} from {case.service}, {owner}"


def evaluate(cases: Sequence[Case], output: str, expect_stripped: bool) -> List[Finding]:
    seen = set(MARKER_PATTERN.findall(output))
    findings = []
    for case in cases:
        if case.name in seen and not case.should_pass:
            findings.append(Finding("leak", case.name, f"{describe(case)} got through; it must be dropped"))
        if case.name not in seen and case.should_pass:
            findings.append(Finding("overblock", case.name, f"{describe(case)} is missing; it must pass"))
    if expect_stripped:
        for key, value in SYNTHETIC_IDENTIFIERS.items():
            if value in output:
                findings.append(Finding("identifier", key, f"{key} value {value} reached the exporter"))
    return findings


def command_plan(args: argparse.Namespace) -> int:
    cases = build_cases(args.org, args.keep_claude_logs)
    print(json.dumps(build_payloads(cases, time.time_ns()), indent=2))
    return EXIT_OK


def command_send(args: argparse.Namespace) -> int:
    cases = build_cases(args.org, args.keep_claude_logs)
    payloads = build_payloads(cases, time.time_ns())
    base = args.endpoint.rstrip("/")
    for signal in ("metrics", "logs"):
        url = f"{base}/v1/{signal}"
        try:
            status = post_json(url, payloads[signal], args.timeout)
        except urllib.error.HTTPError as error:
            print(f"{url}: HTTP {error.code} {error.read().decode('utf-8', 'replace')[:200]}", file=sys.stderr)
            return EXIT_UNUSABLE
        except (urllib.error.URLError, OSError) as error:
            print(f"{url}: cannot reach the collector ({getattr(error, 'reason', error)})", file=sys.stderr)
            return EXIT_UNUSABLE
        print(f"POST {url} -> {status}")
    for case in cases:
        verdict = "pass" if case.should_pass else "drop"
        print(f"  {verdict:4}  {case.marker:36} {describe(case)}")
    return EXIT_OK


def read_output(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    with open(path, encoding="utf-8", errors="replace") as handle:
        return handle.read()


def command_check(args: argparse.Namespace) -> int:
    cases = build_cases(args.org, args.keep_claude_logs)
    try:
        output = read_output(args.output)
    except OSError as error:
        print(f"cannot read {args.output}: {error}", file=sys.stderr)
        return EXIT_UNUSABLE
    if not MARKER_PATTERN.search(output):
        print("no probe-case markers in the output: set the debug exporter to verbosity \"detailed\", "
              "check the pipeline wiring, and send the cases again", file=sys.stderr)
        return EXIT_UNUSABLE
    findings = evaluate(cases, output, args.expect_stripped)
    if args.json:
        print(json.dumps({"findings": [finding.__dict__ for finding in findings]}, indent=2))
    else:
        for finding in findings:
            print(f"{finding.kind.upper():10} {finding.case:24} {finding.detail}")
        print(f"{len(cases)} cases, {len(findings)} findings")
    return EXIT_MISMATCH if findings else EXIT_OK


def parse_arguments(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synthetic OTLP cases that prove a collector filter keeps only one organisation's "
                    "agent telemetry. Run send against a local collector with a debug exporter, then "
                    "check its output.")
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("plan", "print the OTLP/JSON payloads without sending"),
                            ("send", "POST the cases to a collector's OTLP/HTTP receiver"),
                            ("check", "compare the debug exporter's output with the expected verdicts")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--org", required=True, help="the repository owner whose telemetry must pass")
        command.add_argument("--keep-claude-logs", action="store_true",
                             help="expect the organisation's Claude Code events to pass (default: all dropped)")
    commands.choices["send"].add_argument("--endpoint", default="http://127.0.0.1:4318",
                                          help="OTLP/HTTP base URL of a local collector")
    commands.choices["send"].add_argument("--timeout", type=float, default=10.0)
    commands.choices["check"].add_argument("output", help="captured debug exporter output, or - for stdin")
    commands.choices["check"].add_argument("--expect-stripped", action="store_true",
                                           help="also fail when a personal identifier reaches the exporter")
    commands.choices["check"].add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_arguments(argv)
    handlers = {"plan": command_plan, "send": command_send, "check": command_check}
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
