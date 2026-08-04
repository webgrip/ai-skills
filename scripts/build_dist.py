#!/usr/bin/env python3
"""Build dist/<skill>.skill files (zips for claude.ai / the Claude app).

Usage:
    python3 scripts/build_dist.py            # all plugins + dist/SHA256SUMS
    python3 scripts/build_dist.py domain-language

Each skills/<name>/ folder becomes dist/<name>.skill, a zip whose top-level
directory is the skill folder — the format the Claude app's "Save skill" flow
expects. Plugin machinery at the skill root (.claude-plugin/, README.md,
test.sh, .mcp.json) is excluded: claude.ai has no use for it and the zips stay
byte-comparable with pre-merge releases. dist/ is a build output (gitignored);
the release pipeline builds it fresh and attaches the zips to the Forgejo
release.

Zips are deterministic (fixed timestamps/permissions), so rebuilding at a git
tag reproduces the released artifacts byte-for-byte. SHA256SUMS covers every
zip currently in dist/ (sha256sum -c compatible).
"""

import hashlib
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
EPOCH = (1980, 1, 1, 0, 0, 0)  # zip format's minimum timestamp
# plugin machinery at the skill root — not part of the claude.ai skill package
PLUGIN_ONLY = {".claude-plugin", "README.md", "test.sh", ".mcp.json"}


def build(skill_dir: Path, quiet: bool = False):
    out = DIST / f"{skill_dir.name}.skill"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.rglob("*")):
            if f.relative_to(skill_dir).parts[0] in PLUGIN_ONLY:
                continue
            if f.is_file() and "__pycache__" not in f.parts:
                zi = zipfile.ZipInfo(str(f.relative_to(skill_dir.parent)), date_time=EPOCH)
                zi.compress_type = zipfile.ZIP_DEFLATED
                zi.external_attr = 0o644 << 16
                zf.writestr(zi, f.read_bytes())
    if not quiet:
        print(f"wrote {out.relative_to(ROOT)}")
    return out


def write_checksums():
    lines = [
        f"{hashlib.sha256(z.read_bytes()).hexdigest()}  {z.name}"
        for z in sorted(DIST.glob("*.skill"))
    ]
    (DIST / "SHA256SUMS").write_text("\n".join(lines) + "\n")
    print(f"wrote dist/SHA256SUMS ({len(lines)} zip(s))")


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    DIST.mkdir(exist_ok=True)
    found = False
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if only and skill_dir.name != only:
            continue
        if (skill_dir / "SKILL.md").exists():
            build(skill_dir)
            found = True
    if not found:
        sys.exit("no matching skills found")
    write_checksums()


if __name__ == "__main__":
    main()
