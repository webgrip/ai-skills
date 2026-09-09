#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
SCAN="python3 scripts/scan.py"

python3 - <<'PY'
import json, re, sys
patterns = json.load(open("scripts/patterns.json"))["patterns"]
catalogs = {"en": open("patterns-en.md").read(), "nl": open("patterns-nl.md").read()}
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
import json, re, subprocess, sys, tempfile, os, collections
findings = collections.Counter()
total = 0
for lang, catalog in (("en", "patterns-en.md"), ("nl", "patterns-nl.md")):
    label = "Na: " if lang == "nl" else "After: "
    afters = [l[len(label):].strip() for l in open(catalog) if l.startswith(label)]
    total += len(afters)
    if not afters:
        sys.exit(f"{catalog}: no rewritten examples found")
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        f.write("\n\n".join(afters))
        path = f.name
    out = subprocess.run(["python3", "scripts/scan.py", "--json", "--lang", lang, "--fail-on", "never", path],
                         capture_output=True, text=True)
    os.unlink(path)
    if out.returncode:
        sys.exit(out.stderr)
    result = json.loads(out.stdout)[0]
    hits = [f for f in result["findings"] if f["severity"] == "always"]
    for f in hits:
        findings[f"{lang}/{f['id']}"] += 1
    if result["metrics"]["em_dashes_per_500_words"] > 0:
        sys.exit(f"{catalog}: the rewritten examples contain em dashes")
    if len(hits) > len(afters) * 0.02:
        sys.exit(f"{catalog}: {len(hits)} always-severity tells across {len(afters)} rewritten examples: {findings}")
print(f"catalog self-scan: {total} rewritten examples, {sum(findings.values())} always-severity hits, no em dashes")
PY

echo "humanize: OK"
