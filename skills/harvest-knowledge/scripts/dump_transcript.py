#!/usr/bin/env python3
"""Turn a Claude Code session transcript (JSONL) into a compact text dump.

Keeps user and assistant text, tool calls, truncated tool results, summaries,
and the subagent hand-back reports and queued user messages that live in
queue-operation entries, queued_command attachments and isMeta messages.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

REPORT_MARKERS = ("<agent-message", "<task-notification")
REPORT_MARKER_WINDOW = 80
REPORT_KEY_CHARS = 4000
GENERIC_INPUT_CHARS = 300
INPUT_FIELDS = ("command", "file_path", "path", "url", "query", "pattern", "prompt")
EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")


@dataclass
class Limits:
    tool_call: int
    tool_result: int
    edit: int


@dataclass
class Block:
    timestamp: str
    role: str
    text: str

    def render(self) -> str:
        label = f"{self.timestamp} {self.role}" if self.timestamp else self.role
        return f"[{label}] {self.text}"


@dataclass
class Dump:
    user_texts: set
    blocks: list = field(default_factory=list)
    report_keys: set = field(default_factory=set)
    queued_keys: set = field(default_factory=set)

    def add(self, timestamp: str, role: str, text: str) -> None:
        if text.strip():
            self.blocks.append(Block(timestamp, role, text.strip()))

    def add_report(self, timestamp: str, text: str) -> bool:
        key = report_key(text)
        if key is None:
            return False
        if key not in self.report_keys:
            self.report_keys.add(key)
            self.add(timestamp, "REPORT", text)
        return True

    def add_queued(self, timestamp: str, text: str) -> None:
        if self.add_report(timestamp, text):
            return
        key = normalize(text)
        if not key or key in self.user_texts or key in self.queued_keys:
            return
        self.queued_keys.add(key)
        self.add(timestamp, "QUEUED_USER", text)

    def count(self, role: str) -> int:
        return sum(1 for block in self.blocks if block.role == role)


def normalize(text: str) -> str:
    return " ".join(text.split())


def report_key(text: str) -> Optional[str]:
    positions = [text.find(marker) for marker in REPORT_MARKERS]
    found = [position for position in positions if position != -1]
    if not found or min(found) > REPORT_MARKER_WINDOW:
        return None
    return normalize(text[min(found):])[:REPORT_KEY_CHARS]


def text_of(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            part.get("text", "")
            for part in content
            if isinstance(part, dict) and part.get("type") == "text"
        )
    return ""


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return f"{text[:limit]} [... {len(text) - limit} more chars]"


def timestamp_of(record: dict) -> str:
    stamp = record.get("timestamp")
    if not stamp and isinstance(record.get("attachment"), dict):
        stamp = record["attachment"].get("timestamp")
    return str(stamp or "")[:16]


def message_content(record: dict) -> object:
    message = record.get("message")
    return message.get("content") if isinstance(message, dict) else None


def content_parts(content: object) -> list:
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if isinstance(content, list):
        return [part for part in content if isinstance(part, dict)]
    return []


def tool_call_summary(part: dict, limits: Limits) -> str:
    name = part.get("name", "?")
    tool_input = part.get("input") if isinstance(part.get("input"), dict) else {}
    if name in EDIT_TOOLS:
        body = str(tool_input.get("new_string") or tool_input.get("content") or tool_input.get("new_source") or "")
        summary = f"{tool_input.get('file_path') or tool_input.get('notebook_path')} :: {truncate(body, limits.edit)}"
    elif name == "Agent":
        summary = f"{tool_input.get('description', '')} :: {tool_input.get('prompt', '')}"
    else:
        summary = next(
            (str(tool_input[key]) for key in INPUT_FIELDS if tool_input.get(key)),
            json.dumps(tool_input, ensure_ascii=False)[:GENERIC_INPUT_CHARS],
        )
    return f"{name}: {truncate(summary, limits.tool_call)}"


def tool_result_text(part: dict) -> str:
    content = part.get("content")
    if isinstance(content, list):
        return " ".join(
            item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"
        )
    return str(content or "")


def read_records(path: Path) -> tuple:
    records = []
    unreadable = 0
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                unreadable += 1
                continue
            if isinstance(record, dict):
                records.append(record)
            else:
                unreadable += 1
    return records, unreadable


def typed_user_texts(records: Iterable) -> set:
    texts = set()
    for record in records:
        if record.get("type") != "user" or record.get("isMeta"):
            continue
        content = message_content(record)
        texts.add(normalize(text_of(content)))
        texts.update(normalize(part.get("text", "")) for part in content_parts(content) if part.get("type") == "text")
    texts.discard("")
    return texts


def add_user(record: dict, dump: Dump, limits: Limits) -> None:
    stamp = timestamp_of(record)
    content = message_content(record)
    if record.get("isCompactSummary"):
        dump.add(stamp, "SUMMARY", text_of(content))
        return
    for part in content_parts(content):
        if part.get("type") == "text":
            text = part.get("text", "")
            if not dump.add_report(stamp, text) and not record.get("isMeta"):
                dump.add(stamp, "USER", text)
        elif part.get("type") == "tool_result":
            dump.add(stamp, "TOOL_RESULT", truncate(tool_result_text(part), limits.tool_result))


def add_assistant(record: dict, dump: Dump, limits: Limits) -> None:
    stamp = timestamp_of(record)
    for part in content_parts(message_content(record)):
        if part.get("type") == "text":
            dump.add(stamp, "ASSISTANT", part.get("text", ""))
        elif part.get("type") == "tool_use":
            dump.add(stamp, "TOOL_CALL", tool_call_summary(part, limits))


def add_record(record: dict, dump: Dump, limits: Limits) -> None:
    kind = record.get("type")
    if kind == "user":
        add_user(record, dump, limits)
    elif kind == "assistant":
        add_assistant(record, dump, limits)
    elif kind == "summary":
        dump.add(timestamp_of(record), "SUMMARY", str(record.get("summary") or ""))
    elif kind == "queue-operation" and record.get("operation") == "enqueue":
        dump.add_queued(timestamp_of(record), text_of(record.get("content")))
    elif kind == "attachment":
        attachment = record.get("attachment") if isinstance(record.get("attachment"), dict) else {}
        if attachment.get("type") == "queued_command":
            dump.add_queued(timestamp_of(record), text_of(attachment.get("prompt")))


def build_dump(records: list, limits: Limits) -> Dump:
    dump = Dump(user_texts=typed_user_texts(records))
    for record in records:
        add_record(record, dump, limits)
    return dump


def split_at_user_turns(blocks: list, max_chars: int) -> list:
    parts = [[]]
    size = 0
    for block in blocks:
        if size >= max_chars and block.role == "USER" and parts[-1]:
            parts.append([])
            size = 0
        parts[-1].append(block)
        size += len(block.render()) + 2
    return parts


def render(blocks: list) -> str:
    return "\n\n".join(block.render() for block in blocks) + "\n"


def write_parts(output: Path, parts: list) -> list:
    if len(parts) == 1:
        output.write_text(render(parts[0]), encoding="utf-8")
        return [output]
    paths = [output.with_name(f"{output.stem}.part{index}{output.suffix}") for index in range(1, len(parts) + 1)]
    for path, blocks in zip(paths, parts):
        path.write_text(render(blocks), encoding="utf-8")
    return paths


def parse_arguments(argv: list) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path, help="session JSONL, e.g. ~/.claude/projects/<dir>/<session-id>.jsonl")
    parser.add_argument("-o", "--output", type=Path, help="write the dump here instead of stdout")
    parser.add_argument("--split-chars", type=int, help="split into numbered parts of about this size, only before a user turn")
    parser.add_argument("--result-chars", type=int, default=700, help="keep this much of each tool result")
    parser.add_argument("--tool-chars", type=int, default=900, help="keep this much of each tool call")
    parser.add_argument("--edit-chars", type=int, default=600, help="keep this much of each Edit/Write body")
    arguments = parser.parse_args(argv)
    if arguments.split_chars is not None and arguments.output is None:
        parser.error("--split-chars needs --output")
    if arguments.split_chars is not None and arguments.split_chars <= 0:
        parser.error("--split-chars must be positive")
    return arguments


def main(argv: list) -> int:
    arguments = parse_arguments(argv)
    if not arguments.transcript.is_file():
        print(f"dump_transcript: no such file: {arguments.transcript}", file=sys.stderr)
        return 2
    records, unreadable = read_records(arguments.transcript)
    if not records:
        print(f"dump_transcript: no transcript records in {arguments.transcript}", file=sys.stderr)
        return 1
    dump = build_dump(records, Limits(arguments.tool_chars, arguments.result_chars, arguments.edit_chars))
    if arguments.output is None:
        sys.stdout.write(render(dump.blocks))
    else:
        parts = split_at_user_turns(dump.blocks, arguments.split_chars) if arguments.split_chars else [dump.blocks]
        for path in write_parts(arguments.output, parts):
            print(path)
    print(
        f"dump_transcript: {len(dump.blocks)} blocks, {sum(len(block.text) for block in dump.blocks) // 1000}k chars, "
        f"{dump.count('REPORT')} reports, {dump.count('QUEUED_USER')} queued user messages, "
        f"{unreadable} unreadable lines skipped",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
