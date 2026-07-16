#!/usr/bin/env python3
"""PostToolUse hook: append one JSONL line per Skill invocation.

Log lives at ~/.claude/skill-usage.jsonl — local file, never sent anywhere.
Fail-open by design: a telemetry hook must never break a session, so every
error path exits 0 silently.
"""
import datetime
import json
import os
import sys

try:
    event = json.load(sys.stdin)
    tool_input = event.get("tool_input") or {}
    line = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "skill": tool_input.get("skill") or tool_input.get("name") or "",
        "cwd": event.get("cwd", ""),
        "session": event.get("session_id", ""),
    }
    path = os.path.expanduser("~/.claude/skill-usage.jsonl")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a") as f:
        f.write(json.dumps(line) + "\n")
except Exception:
    pass
sys.exit(0)
