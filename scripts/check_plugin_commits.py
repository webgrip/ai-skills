#!/usr/bin/env python3
"""PR guard for plugin changes.

Usage:
    python3 scripts/check_plugin_commits.py <base-ref>    # e.g. the PR base sha

Every commit touching skills/** must use a release-triggering type
(feat|fix|perf|refactor|revert, or breaking). Anything else (docs:, chore:,
...) merges without cutting a release, so the skill gets no new
<skill>-vX.Y.Z tag, no Forgejo release and no .skill package. To force a
major, use a breaking commit (e.g. `feat(<plugin>)!: ...`). That no
plugin.json carries a version is checked by scripts/check_manifests.py.
"""

import sys

from release_skills import BREAKING_RE, TYPE_RE, git

RELEASING_TYPES = {"feat", "fix", "perf", "refactor", "revert"}
errors = []


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    base = sys.argv[1]

    out = git("log", "--no-merges", "--format=%H", f"{base}..HEAD")
    for sha in out.split():
        subject = git("log", "-1", "--format=%s", sha).strip()
        body = git("log", "-1", "--format=%b", sha)
        files = git("diff-tree", "--no-commit-id", "--name-only", "-r", sha)
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

    if errors:
        print("plugin commit check FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("plugin commit check OK")


if __name__ == "__main__":
    main()
