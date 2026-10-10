#!/usr/bin/env python3
"""PreToolUse hook (Claude Code twin of opencode/plugins/guard-secrets.js).

Blocks a plaintext-secret leak before an Edit/Write/MultiEdit runs:
  1. never create decrypted secret artifacts (a file name containing "decrypted")
  2. a *.sops.yaml / *.sops.yml write must contain SOPS ciphertext (ENC[)
  3. gitleaks scans the new content, and a finding blocks

Blocking = exit 2 with a reason on stderr (Claude Code's deny contract, the
analogue of the opencode plugin's throw). gitleaks runs with its own exit code
for findings (LEAKS_FOUND_EXIT_CODE). A missing gitleaks, a timeout, or any
other exit status is a scanner failure, not a finding: the hook warns on
stderr and allows the write. Malformed input also allows. The hook fails open
on its own errors because it is a same-machine guard, not a security boundary;
MR review is that. Content is taken from whichever field the tool provides
(Write: content; Edit: new_string; MultiEdit: each edit's new_string).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile

LEAKS_FOUND_EXIT_CODE = 10
SCAN_TIMEOUT_SECONDS = 30
COMPLIANT_PATH = (
    "Reference the value instead of writing it: follow the repo's own secrets convention "
    "where it documents one, else keep the value in the vault and read it with an "
    "ExternalSecret (SOPS only at the floor), wired by existingSecret/envFromSecret."
)


def deny(message: str) -> None:
    print(f"BLOCKED: {message}", file=sys.stderr)
    sys.exit(2)


def warn(message: str) -> None:
    print(f"guard-secrets: {message}", file=sys.stderr)


def read_tool_input() -> dict:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return {}
    tool_input = event.get("tool_input") if isinstance(event, dict) else None
    return tool_input if isinstance(tool_input, dict) else {}


def written_content(tool_input: dict) -> str:
    parts = [tool_input.get("content"), tool_input.get("new_string")]
    parts += [edit.get("new_string") for edit in tool_input.get("edits") or [] if isinstance(edit, dict)]
    return "\n".join(part for part in parts if isinstance(part, str) and part)


def refuse_decrypted_artifact(base: str) -> None:
    if "decrypted" in base:
        deny(
            f"refusing to write a decrypted secret artifact ({base}). Plaintext secrets never "
            "touch disk: the value stays in the vault, or at the floor in an encrypted *.sops.yaml."
        )


def refuse_plaintext_sops(base: str, content: str) -> None:
    if base.endswith((".sops.yaml", ".sops.yml")) and content and "ENC[" not in content:
        deny(f"{base} is a SOPS file but the content isn't encrypted. Edit plaintext elsewhere, then 'sops --encrypt'.")


def gitleaks_exit_code(gitleaks: str, content: str) -> int:
    with tempfile.TemporaryDirectory(prefix="guard-secrets-") as scan_dir:
        target = os.path.join(scan_dir, "content.txt")
        with open(target, "w", encoding="utf-8") as handle:
            handle.write(content)
        return subprocess.run(
            [
                gitleaks, "detect", "--no-banner", "--no-git", "--redact",
                "--exit-code", str(LEAKS_FOUND_EXIT_CODE), "-s", target,
            ],
            capture_output=True,
            timeout=SCAN_TIMEOUT_SECONDS,
        ).returncode


def scan_plaintext(base: str, content: str) -> None:
    gitleaks = shutil.which("gitleaks")
    if not gitleaks:
        warn("gitleaks not on PATH; plaintext scan skipped. Pin it in .mise.toml.")
        return
    try:
        exit_code = gitleaks_exit_code(gitleaks, content)
    except (OSError, subprocess.SubprocessError) as error:
        warn(f"gitleaks could not run ({error}); plaintext scan skipped.")
        return
    if exit_code == LEAKS_FOUND_EXIT_CODE:
        deny(f"gitleaks flagged a likely plaintext secret in {base}. {COMPLIANT_PATH}")
    if exit_code != 0:
        warn(
            f"gitleaks exited {exit_code} without a finding; plaintext scan skipped. "
            "Run 'gitleaks version' by hand to see why."
        )


def main() -> None:
    tool_input = read_tool_input()
    path = tool_input.get("file_path") or tool_input.get("path") or ""
    if not isinstance(path, str) or not path:
        return
    base = os.path.basename(path)
    content = written_content(tool_input)
    refuse_decrypted_artifact(base)
    refuse_plaintext_sops(base, content)
    if content:
        scan_plaintext(base, content)


if __name__ == "__main__":
    main()
