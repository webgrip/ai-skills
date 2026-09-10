#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SCAN="python3 scripts/scan.py"

python3 - <<'PY'
import json, re, sys
patterns = json.load(open("scripts/patterns.json"))["patterns"]
catalogs = {lang: open(f"patterns-{lang}.md").read() + open(f"patterns-{lang}-domains.md").read() for lang in ("en", "nl")}
missing = [p["id"] for p in patterns for lang in p["lang"] if f"`{p['id']}`" not in catalogs[lang]]
if missing:
    sys.exit(f"scanner ids without a catalog entry: {missing}")
for p in patterns:
    for expression in p["regex"]:
        re.compile(expression, re.IGNORECASE)
ids = [p["id"] + "/" + ",".join(p["lang"]) for p in patterns]
if len(ids) != len(set(ids)):
    sys.exit("duplicate scanner ids")
print(f"patterns.json: {len(patterns)} entries consistent with the catalogs")
PY

for lang in en nl; do
  detected=$($SCAN --json --fail-on never "fixtures/$lang-clean.md" | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['lang'])")
  [ "$detected" = "$lang" ] || { echo "language detection: expected $lang, got $detected" >&2; exit 1; }

  $SCAN --lang "$lang" "fixtures/$lang-clean.md" > /dev/null || { echo "$lang-clean.md raised an always-severity finding" >&2; $SCAN --lang "$lang" "fixtures/$lang-clean.md"; exit 1; }
  clean_hits=$($SCAN --json --lang "$lang" --fail-on never "fixtures/$lang-clean.md" | python3 -c "import json,sys; print(len(json.load(sys.stdin)[0]['findings']))")
  [ "$clean_hits" -le 3 ] || { echo "$lang-clean.md: $clean_hits findings on human prose, expected at most 3" >&2; $SCAN --lang "$lang" --fail-on never "fixtures/$lang-clean.md"; exit 1; }

  if $SCAN --lang "$lang" "fixtures/$lang-slop.md" > /dev/null; then
    echo "$lang-slop.md passed the scanner; it must fail on an always-severity finding" >&2; exit 1
  fi
  $SCAN --json --lang "$lang" --fail-on never "fixtures/$lang-slop.md" > "/tmp/humanize-$lang-slop.json"
  python3 - "$lang" <<'PY'
import json, sys
lang = sys.argv[1]
found = {f["id"] for f in json.load(open(f"/tmp/humanize-{lang}-slop.json"))[0]["findings"]}
expected = [l.strip() for l in open(f"fixtures/{lang}-slop.expect") if l.strip()]
missed = [e for e in expected if e not in found]
if missed:
    sys.exit(f"{lang}-slop.md: expected ids not found: {missed}; found {sorted(found)}")
print(f"{lang}: clean fixture quiet, slop fixture hit all {len(expected)} expected ids")
PY
done
python3 - <<'PY'
import collections
import json
import os
import re
import subprocess
import sys
import tempfile

EXAMPLES_THAT_MUST_CARRY_ANOTHER_SURFACE = {
    ("list-label-periods", "inline-header-lists"),
    ("empty-parent-headings", "heading-level-skipping"),
    ("bypass-trick-characters", "ai-vocabulary-lexicon"),
}

findings = collections.Counter()
total = 0
for lang, catalog in (("en", "patterns-en.md"), ("nl", "patterns-nl.md"), ("en", "patterns-en-domains.md"), ("nl", "patterns-nl-domains.md")):
    label = "Na: " if lang == "nl" else "After: "
    owner, examples = None, []
    for line in open(catalog):
        heading = re.match(r"^### .*`([a-z0-9-]+)`\s*$", line)
        if heading:
            owner = heading.group(1)
        elif line.startswith(label):
            examples.append((owner, line[len(label):].strip()))
    total += len(examples)
    if not examples:
        sys.exit(f"{catalog}: no rewritten examples found")

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n\n".join(text for _, text in examples))
        path = f.name
    out = subprocess.run(["python3", "scripts/scan.py", "--json", "--lang", lang, "--fail-on", "never", path],
                         capture_output=True, text=True)
    os.unlink(path)
    if out.returncode:
        sys.exit(out.stderr)
    result = json.loads(out.stdout)[0]

    body = "\n\n".join(text for _, text in examples).split("\n")
    line_owner = {}
    cursor = 1
    for entry_id, text in examples:
        for _ in text.split("\n"):
            line_owner[cursor] = entry_id
            cursor += 1
        cursor += 1

    for finding in result["findings"]:
        if finding["severity"] != "always":
            continue
        owner_id = line_owner.get(finding["line"])
        if finding["id"] == owner_id:
            continue
        if (owner_id, finding["id"]) in EXAMPLES_THAT_MUST_CARRY_ANOTHER_SURFACE:
            continue
        findings[f"{lang}/{finding['id']}"] += 1
        print(f"  {catalog}:{finding['line']} {finding['id']} in an example owned by "
              f"{owner_id}: {finding['match']!r}")
    if result["metrics"]["em_dashes_per_500_words"] > 0:
        sys.exit(f"{catalog}: the rewritten examples contain em dashes")

if findings:
    sys.exit(f"rewritten examples still carry tells they do not themselves demonstrate: {dict(findings)}")
print(f"catalog self-scan: {total} rewritten examples, no stray always-severity tells, no em dashes")
PY

python3 - <<'PY'
import glob
import json
import sys

rule = "five or more vocabulary hits"
carriers = [f for f in glob.glob("*.md") if rule in open(f).read()]
if carriers != ["SKILL.md"]:
    sys.exit(f"the mode rule must live in SKILL.md only; found in {carriers}")
method = open("method.md").read()
for stale in ("Default when the user shares", "or when asked"):
    if stale in method:
        sys.exit(f"method.md restates the mode rule: {stale!r}")
cases = json.load(open("evals/evals.json"))["evals"]
missing = [c["id"] for c in cases if "expect_trigger" not in c]
if missing:
    sys.exit(f"evals without an explicit expect_trigger: {missing}")
print(f"mode rule stated once; {len(cases)} evals all carry expect_trigger")
PY

python3 - <<'PY'
import json
import sys
rows = json.load(open("scripts/patterns.json"))["patterns"]
scoped = [r["id"] for r in rows if r.get("domain")]
if not scoped:
    sys.exit("no domain-scoped scanner rows; the tagging did not reach patterns.json")
sys.path.insert(0, "scripts")
import scan
default = len(scan.load_patterns("scripts/patterns.json", "en", False))
everything = len(scan.load_patterns("scripts/patterns.json", "en", False, ("wikipedia", "fiction")))
if everything <= default:
    sys.exit("--domain all loads no more rows than the default")
leaked = [r["id"] for r in rows if r.get("domain") and any(r["id"] == e["id"] for e, _ in scan.load_patterns("scripts/patterns.json", r["lang"][0], False))]
if leaked:
    sys.exit(f"domain-scoped rows load by default: {sorted(set(leaked))}")
print(f"domain scoping: {len(set(scoped))} ids hidden by default, {everything - default} en rows restored by --domain all")
PY

echo "humanize: OK"
