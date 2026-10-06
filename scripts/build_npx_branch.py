#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from build_dist import PLUGIN_ONLY, ROOT

PREFIX = "webgrip-"
BRANCH = "npx"
OUT = ROOT / "dist" / BRANCH
BRANCH_README = f"""# webgrip ai-skills, prefixed for `npx skills`

Generated from `main` by `scripts/build_npx_branch.py`. Never edit this branch:
every release rebuilds it. Each skill is named `{PREFIX}<skill>` so it cannot
collide with another estate's same-named skill in `~/.agents/skills/`.

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git#{BRANCH} -g
npx skills update -g
```
"""


def git(*args, env=None):
    result = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True,
                            env={**os.environ, **(env or {})})
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def prefixed_skill_md(text: str, skill: str) -> str:
    lines = text.split("\n")
    if lines[0] != "---":
        sys.exit(f"{skill}: SKILL.md has no frontmatter")
    for index, line in enumerate(lines[1:], start=1):
        if line == "---":
            break
        if line.startswith("name:"):
            lines[index] = f"name: {PREFIX}{skill}"
            return "\n".join(lines)
    sys.exit(f"{skill}: SKILL.md frontmatter has no name")


def shipped_files(skill_dir: Path):
    for path in sorted(skill_dir.rglob("*")):
        relative = path.relative_to(skill_dir)
        if relative.parts[0] in PLUGIN_ONLY or "__pycache__" in relative.parts or not path.is_file():
            continue
        yield path, relative


def build() -> Path:
    shutil.rmtree(OUT, ignore_errors=True)
    skills = sorted(d for d in (ROOT / "skills").iterdir() if (d / "SKILL.md").is_file())
    for skill_dir in skills:
        target = OUT / "skills" / f"{PREFIX}{skill_dir.name}"
        for source, relative in shipped_files(skill_dir):
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative == Path("SKILL.md"):
                destination.write_text(prefixed_skill_md(source.read_text(), skill_dir.name))
            else:
                shutil.copy2(source, destination)
    (OUT / "README.md").write_text(BRANCH_README)
    shutil.copy2(ROOT / "LICENSE", OUT / "LICENSE")
    print(f"built {OUT.relative_to(ROOT)} ({len(skills)} skills, prefix {PREFIX})")
    return OUT


def remote_branch_head():
    listing = git("ls-remote", "origin", f"refs/heads/{BRANCH}")
    if not listing:
        return None
    head = listing.split()[0]
    git("fetch", "-q", "origin", f"refs/heads/{BRANCH}")
    return head


def tree_of(out: Path) -> str:
    with tempfile.TemporaryDirectory() as scratch:
        index = {"GIT_INDEX_FILE": str(Path(scratch) / "index")}
        git("--work-tree", str(out), "add", "-A", ".", env=index)
        return git("write-tree", env=index)


def publish():
    tree = tree_of(build())
    parent = remote_branch_head()
    if parent and git("rev-parse", f"{parent}^{{tree}}") == tree:
        print(f"{BRANCH} branch already matches {tree[:12]}; nothing to push")
        return
    source = git("rev-parse", "--short", "HEAD")
    parent_args = ["-p", parent] if parent else []
    commit = git("commit-tree", tree, *parent_args, "-m", f"chore(npx): build from {source} [skip ci]")
    git("push", "origin", f"{commit}:refs/heads/{BRANCH}")
    print(f"pushed {BRANCH} -> {commit[:12]} (from {source})")


if __name__ == "__main__":
    {"build": build, "publish": publish}[sys.argv[1] if len(sys.argv) > 1 else "build"]()
