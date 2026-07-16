#!/usr/bin/env python3
"""PR guard for plugin changes (versions themselves are bumped at release time).

Usage:
    python3 scripts/check_plugin_commits.py <base-ref>    # e.g. the PR base sha

Two rules, both feeding the per-skill release trains (scripts/release_skills.py):

1. Every commit touching skills/** must use a release-triggering type
   (feat|fix|perf|refactor|revert, or breaking). Anything else (docs:, chore:,
   ...) would merge without cutting a release, so the plugin's version never
   bumps and Claude Code installs never see the change.
2. `version` in an existing plugin.json must not change in a PR — bumps are
   computed from the last release tag and would silently clobber a hand-edit.
   To force a major, use a breaking commit (e.g. `feat(<plugin>)!: ...`).
"""

import json
import sys
from pathlib import Path

from release_skills import BREAKING_RE, TYPE_RE, git

ROOT = Path(__file__).resolve().parent.parent
RELEASING_TYPES = {"feat", "fix", "perf", "refactor", "revert"}
errors = []


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = sys.argv[1]

    _, out = git("log", "--no-merges", "--format=%H", f"{base}..HEAD")
    for sha in out.split():
        _, subject = git("log", "-1", "--format=%s", sha)
        subject = subject.strip()
        _, body = git("log", "-1", "--format=%b", sha)
        _, files = git("diff-tree", "--no-commit-id", "--name-only", "-r", sha)
        if not any(f.startswith(("skills/", "plugins/")) for f in files.splitlines()):
            continue
        m = TYPE_RE.match(subject)
        breaking = (m and m.group("bang")) or BREAKING_RE.search(body)
        if not breaking and (not m or m.group("type") not in RELEASING_TYPES):
            errors.append(
                f"commit touches skills/ but type releases nothing, so the change "
                f"would never reach installs — use {'|'.join(sorted(RELEASING_TYPES))}: "
                f"{subject!r}"
            )

    _, diff = git("diff", "--name-only", f"{base}...HEAD")
    for path in diff.splitlines():
        parts = path.split("/")
        if len(parts) == 4 and parts[0] in ("skills", "plugins") and path.endswith(".claude-plugin/plugin.json"):
            code, base_pj = git("show", f"{base}:{path}", ok_codes=(0, 128))
            if code != 0:
                continue  # new plugin: authoring the initial version is fine
            if not (ROOT / path).exists():
                continue  # plugin deleted in this PR
            base_version = json.loads(base_pj).get("version")
            head_version = json.loads((ROOT / path).read_text()).get("version")
            if base_version != head_version:
                errors.append(
                    f"{path}: version changed {base_version!r} → {head_version!r} — versions "
                    f"are computed at release time from commit types; revert the manual bump"
                )

    if errors:
        print("plugin commit check FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("plugin commit check OK")


if __name__ == "__main__":
    main()
