#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

DEFAULT_ROOT = Path.home() / ".claude" / "projects"
HANDBACK_FRAME = re.compile(r'<agent-message from="([^"]+)">\s*\[Subagent hand-back\].*?The report follows:\n', re.S)
SUMMARY_KEYS = ("command", "file_path", "path", "pattern", "url", "query", "description", "to")


@dataclass
class Call:
    timestamp: str
    project: str
    session: str
    agent: Optional[str]
    cwd: Optional[str]
    branch: Optional[str]
    tool: str
    summary: str


@dataclass
class Handback:
    timestamp: str
    project: str
    session: str
    sender: str
    report: str


def parse_time(text: str) -> datetime:
    value = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
    return value if value.tzinfo else value.astimezone()


def file_time(path: Path) -> datetime:
    stat = path.stat()
    seconds = getattr(stat, "st_birthtime", None) or stat.st_mtime
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def transcript_files(root: Path, project_filter: Optional[str]) -> Iterator[Tuple[Path, str, str, Optional[str]]]:
    for project_dir in sorted(path for path in root.glob("*") if path.is_dir()):
        if project_filter and project_filter not in project_dir.name:
            continue
        for session_file in sorted(project_dir.glob("*.jsonl")):
            yield session_file, project_dir.name, session_file.stem, None
        for agent_file in sorted(project_dir.glob("*/subagents/agent-*.jsonl")):
            yield agent_file, project_dir.name, agent_file.parent.parent.name, agent_file.stem[len("agent-"):]


def records(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if isinstance(record, dict):
                yield record


def in_window(record: dict, since: Optional[datetime], until: Optional[datetime]) -> bool:
    stamp = record.get("timestamp")
    if not stamp:
        return since is None and until is None
    try:
        moment = parse_time(stamp)
    except ValueError:
        return False
    return (since is None or moment >= since) and (until is None or moment <= until)


def summarize(tool_input: object) -> str:
    if isinstance(tool_input, dict):
        for key in SUMMARY_KEYS:
            value = tool_input.get(key)
            if isinstance(value, str) and value:
                return value
    return json.dumps(tool_input, ensure_ascii=False)


def content_items(record: dict) -> list:
    content = (record.get("message") or {}).get("content")
    return content if isinstance(content, list) else []


def find_calls(root: Path, project_filter: Optional[str], since: Optional[datetime], until: Optional[datetime], tool: Optional[str], pattern: Optional[re.Pattern]) -> List[Call]:
    calls = []
    for path, project, session, agent in transcript_files(root, project_filter):
        for record in records(path):
            if not in_window(record, since, until):
                continue
            for item in content_items(record):
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                if tool and item.get("name") != tool:
                    continue
                serialized = json.dumps(item.get("input"), ensure_ascii=False)
                if pattern and not pattern.search(serialized):
                    continue
                calls.append(Call(
                    timestamp=record.get("timestamp", ""),
                    project=project,
                    session=session,
                    agent=agent or record.get("agentId"),
                    cwd=record.get("cwd"),
                    branch=record.get("gitBranch"),
                    tool=item.get("name", "?"),
                    summary=summarize(item.get("input")),
                ))
    return sorted(calls, key=lambda call: call.timestamp)


def handback_text(record: dict) -> Optional[str]:
    if record.get("type") == "queue-operation" and isinstance(record.get("content"), str):
        return record["content"]
    if record.get("type") == "user" and record.get("isMeta"):
        content = (record.get("message") or {}).get("content")
        if isinstance(content, str):
            return content
        return "\n".join(item.get("text", "") for item in content or [] if isinstance(item, dict))
    return None


def find_handbacks(root: Path, project_filter: Optional[str], since: Optional[datetime], until: Optional[datetime], pattern: Optional[re.Pattern]) -> List[Handback]:
    seen, handbacks = set(), []
    for path, project, session, _ in transcript_files(root, project_filter):
        for record in records(path):
            text = handback_text(record)
            if not text or not in_window(record, since, until):
                continue
            frame = HANDBACK_FRAME.search(text)
            if not frame:
                continue
            body = text[frame.end():].split("</agent-message>", 1)[0]
            report = "\n".join(line[2:] if line.startswith("  ") else line for line in body.splitlines()).strip()
            key = (session, frame.group(1), report[:500])
            if key in seen or (pattern and not pattern.search(report)):
                continue
            seen.add(key)
            handbacks.append(Handback(record.get("timestamp", ""), project, session, frame.group(1), report))
    return sorted(handbacks, key=lambda handback: handback.timestamp)


def window(args: argparse.Namespace) -> Tuple[Optional[datetime], Optional[datetime]]:
    center = None
    if args.around:
        center = file_time(Path(args.around))
        print(f"window centre: {center.isoformat()} (birth time of {args.around}, or mtime where the filesystem has none)", file=sys.stderr)
    elif args.at:
        center = parse_time(args.at)
    if center is not None:
        margin = timedelta(minutes=args.minutes)
        return center - margin, center + margin
    return (parse_time(args.since) if args.since else None, parse_time(args.until) if args.until else None)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="List the tool calls (or subagent hand-back reports) recorded in Claude Code transcripts, across every project, session and subagent. Read-only.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="transcript root (default ~/.claude/projects)")
    parser.add_argument("--project", help="only project directories whose name contains this text")
    parser.add_argument("--since", help="ISO time; naive times are local")
    parser.add_argument("--until", help="ISO time; naive times are local")
    parser.add_argument("--at", help="ISO time to centre the window on")
    parser.add_argument("--around", help="file whose birth time centres the window")
    parser.add_argument("--minutes", type=float, default=10, help="half-width of the --at/--around window (default 10)")
    parser.add_argument("--tool", help="only this tool name, for example Bash, Edit, Write, Agent")
    parser.add_argument("--grep", help="regular expression the tool input (or hand-back report) must match")
    parser.add_argument("--handbacks", action="store_true", help="list subagent hand-back reports instead of tool calls")
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--width", type=int, default=200, help="truncate text output to this many characters per line")
    args = parser.parse_args(argv)

    root = Path(os.path.expanduser(args.root))
    if not root.is_dir():
        print(f"no transcript root at {root}", file=sys.stderr)
        return 2
    try:
        since, until = window(args)
        pattern = re.compile(args.grep) if args.grep else None
    except (ValueError, OSError, re.error) as error:
        print(f"bad argument: {error}", file=sys.stderr)
        return 2

    if args.handbacks:
        handbacks = find_handbacks(root, args.project, since, until, pattern)
        if args.json:
            print(json.dumps([asdict(handback) for handback in handbacks], indent=2, ensure_ascii=False))
        for handback in [] if args.json else handbacks:
            print(f"=== {handback.timestamp}  {handback.project}  {handback.session[:8]}  from={handback.sender}")
            print(handback.report)
        return 0

    calls = find_calls(root, args.project, since, until, args.tool, pattern)
    if args.json:
        print(json.dumps([asdict(call) for call in calls], indent=2, ensure_ascii=False))
        return 0
    for call in calls:
        who = call.session[:8] + (f"/{call.agent}" if call.agent else "")
        line = f"{call.timestamp[:19]}  {call.project}  {who}  {call.tool}: {' '.join(call.summary.split())}"
        print(line[:args.width])
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(1)
