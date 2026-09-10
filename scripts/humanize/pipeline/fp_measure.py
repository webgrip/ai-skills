#!/usr/bin/env python3
"""Measure the scanner's false-positive rate on human-written prose.

Every document in control/manifest.json was written by a person, so every flag the scanner raises
on it is a false positive by construction. Regex hit rates are per 10,000 cleaned words of the whole text; the fraction of
paragraphs flagged uses paragraphs of 50 to 400 words as the unit, and structure gates use windows
of 300 to 700 words, sized like a rewrite output.
Rates are reported per language and per register with a Wilson 95% interval, and --fail turns the
thresholds into an exit status so a regex cannot ship untested.

Usage:
    fp_measure.py [--committed | --all] [--fail] [--json]
                  [--threshold-regex 2.0] [--threshold-register 4.0]
"""

import argparse
import collections
import html
import importlib.util
import json
import math
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

HUMANIZE = Path(__file__).resolve().parents[1]
CONTROL = HUMANIZE / "control"
SKILL = HUMANIZE.parents[1] / "skills" / "humanize"
PARAGRAPH_WORDS = (50, 400)
WINDOW_WORDS = (300, 700)
MIN_LANGUAGE_WORDS = 10_000
MIN_REGISTER_WORDS = 5_000
STRUCTURE_CEILING = {"encyclopedic": 0.05, "technical": 0.05, "official": 0.05, "informal-discussion": 0.10, "literary": 0.10}


def load_scanner():
    spec = importlib.util.spec_from_file_location("scan", SKILL / "scripts" / "scan.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_manifest(committed_only):
    rows = json.loads((CONTROL / "manifest.json").read_text())
    return [r for r in rows if (r["committed"] or not committed_only) and (CONTROL / r["file"]).exists()]


def clean_gutenberg(text):
    start = re.search(r"\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG[^\n]*\n", text)
    end = re.search(r"\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG", text)
    body = text[start.end() if start else 0:end.start() if end else len(text)]
    body = re.sub(r"\[\s*Transcriber'?s? Notes?:.*?\]", "", body, flags=re.S | re.I)
    kept = [l for l in body.split("\n") if not l.startswith("  ")]
    body = "\n".join(kept)
    body = re.sub(r"_([^_\n]+)_", r"\1", body)
    body = re.sub(r"(?<!\n)\n(?!\n)", " ", body)
    return re.sub(r"[ \t]+", " ", body)


def clean_wikitext(text):
    for _ in range(3):
        text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"\[\[(?:Bestand|File|Image|Afbeelding|Categorie|Category):[^\]]*\]\]", "", text)
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", text)
    text = re.sub(r"\[https?://\S+ ([^\]]*)\]", r"\1", text)
    text = re.sub(r"\[https?://\S+\]", "", text)
    text = re.sub(r"'{2,3}", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = "\n".join(l for l in text.split("\n") if not re.match(r"^\s*(\{\||\|\}|\||!)", l))
    text = re.sub(r"^\s*(={2,6})\s*(.+?)\s*=+\s*$", lambda m: "#" * len(m.group(1)) + " " + m.group(2), text, flags=re.M)
    text = re.sub(r"^\s*\*+\s*", "- ", text, flags=re.M)
    text = re.sub(r"^\s*#+\s+(?![#])", "1. ", text, flags=re.M)
    text = re.sub(r"[ \t]+([.,;:!?)])", r"\1", text)
    return html.unescape(text)


def clean_talk_wikitext(text):
    text = clean_wikitext(text)
    text = re.sub(r"\[\[(?:Gebruiker|User|Overleg gebruiker|User talk):[^\]]*\]\]", "", text)
    text = re.sub(r"\d{1,2} \w+\.? \d{4} \d{2}:\d{2} \((?:CES?T|UTC)\)", "", text)
    text = re.sub(r"^\s*:+", "", text, flags=re.M)
    text = re.sub(r"__[A-Z_]+__", "", text)
    text = re.sub(r"\(\s*\)", "", text)
    return text


class MainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out, self.skip, self.inside = [], 0, False

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.inside = True
        if tag in ("script", "style", "nav", "header", "footer", "aside"):
            self.skip += 1
        if self.inside and tag in ("p", "li", "h1", "h2", "h3", "br"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag == "main":
            self.inside = False
        if tag in ("script", "style", "nav", "header", "footer", "aside"):
            self.skip -= 1

    def handle_data(self, data):
        if self.inside and not self.skip:
            self.out.append(data)


def clean_html(text):
    parser = MainText()
    parser.feed(text)
    return re.sub(r"\n\s*\n+", "\n\n", html.unescape("".join(parser.out)))


def clean_markdown(text):
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    return re.sub(r"```.*?```", "", text, flags=re.S)


CLEANERS = {"gutenberg": clean_gutenberg, "wikitext": clean_wikitext, "talk-wikitext": clean_talk_wikitext, "html": clean_html, "markdown": clean_markdown, "text": lambda t: t}


def clean_text(row):
    raw = (CONTROL / row["file"]).read_text(encoding="utf-8", errors="ignore")
    return CLEANERS[row["format"]](raw)


def paragraph_units(text, scan):
    units = []
    for block in re.split(r"\n\s*\n", text):
        words = len(scan.WORD.findall(block))
        if PARAGRAPH_WORDS[0] <= words <= PARAGRAPH_WORDS[1]:
            units.append(block)
    return units


def window_units(text, scan):
    windows, current, count = [], [], 0
    for block in re.split(r"\n\s*\n", text):
        if not block.strip():
            continue
        current.append(block)
        count += len(scan.WORD.findall(block))
        if count >= WINDOW_WORDS[0]:
            windows.append("\n\n".join(current))
            current, count = [], 0
    return [w for w in windows if len(scan.WORD.findall(w)) <= WINDOW_WORDS[1]]


def wilson(hits, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = hits / n
    denominator = 1 + z * z / n
    centre = p + z * z / (2 * n)
    spread = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((centre - spread) / denominator, (centre + spread) / denominator)


def measure_regex(text, units, compiled, scan):
    per_id = collections.defaultdict(lambda: {"hits": 0, "flagged": 0, "examples": []})
    words = len(scan.WORD.findall(text))
    for finding in scan.find_matches(text, compiled):
        row = per_id[finding["id"]]
        row["hits"] += 1
        if len(row["examples"]) < 3:
            row["examples"].append(finding["match"][:60])
    for unit in units:
        for pid in {f["id"] for f in scan.find_matches(unit, compiled)}:
            per_id[pid]["flagged"] += 1
    return words, per_id


def measure_structure(windows, lang, scan, compiled):
    if not hasattr(scan, "structure_findings"):
        return {}, {}
    per_id, severity = collections.defaultdict(int), {}
    for window in windows:
        for finding in scan.structure_findings(window, lang, scan.classify_blocks(window), compiled):
            per_id[finding["id"]] += 1
            severity[finding["id"]] = finding["severity"]
    return dict(per_id), severity


def measure(rows, scan):
    report = {}
    for row in rows:
        lang, register = row["lang"], row["register"]
        text = clean_text(row)
        compiled = scan.load_patterns(SKILL / "scripts" / "patterns.json", lang, True)
        paragraphs = paragraph_units(text, scan)
        windows = window_units(text, scan)
        words, per_id = measure_regex(text, paragraphs, compiled, scan)
        structure, gate_severity = measure_structure(windows, lang, scan, compiled)
        key = (lang, register)
        bucket = report.setdefault(key, {"words": 0, "paragraphs": 0, "windows": 0, "regex": collections.defaultdict(lambda: {"hits": 0, "flagged": 0, "examples": []}), "structure": collections.defaultdict(int), "gate_severity": {}, "files": []})
        bucket["words"] += words
        bucket["paragraphs"] += len(paragraphs)
        bucket["windows"] += len(windows)
        bucket["files"].append(row["file"])
        for pid, stats in per_id.items():
            bucket["regex"][pid]["hits"] += stats["hits"]
            bucket["regex"][pid]["flagged"] += stats["flagged"]
            bucket["regex"][pid]["examples"] = (bucket["regex"][pid]["examples"] + stats["examples"])[:3]
        for sid, count in structure.items():
            bucket["structure"][sid] += count
        bucket["gate_severity"].update(gate_severity)
    return report


def per_language(report):
    totals = {}
    for (lang, _), bucket in report.items():
        t = totals.setdefault(lang, {"words": 0, "regex": collections.defaultdict(int)})
        t["words"] += bucket["words"]
        for pid, stats in bucket["regex"].items():
            t["regex"][pid] += stats["hits"]
    return totals


def judge(report, threshold_regex, threshold_register):
    failures = []
    for lang, totals in per_language(report).items():
        if totals["words"] < MIN_LANGUAGE_WORDS:
            continue
        for pid, hits in totals["regex"].items():
            rate = hits * 10_000 / totals["words"]
            if rate > threshold_regex:
                failures.append(f"{lang} {pid}: {rate:.2f} per 10k words over {totals['words']} words (limit {threshold_regex})")
    for (lang, register), bucket in report.items():
        if bucket["words"] >= MIN_REGISTER_WORDS:
            for pid, stats in bucket["regex"].items():
                rate = stats["hits"] * 10_000 / bucket["words"]
                if rate > threshold_register:
                    failures.append(f"{lang}/{register} {pid}: {rate:.2f} per 10k (register limit {threshold_register}); e.g. {stats['examples']}")
        ceiling = STRUCTURE_CEILING.get(register, 0.05)
        for sid, count in bucket["structure"].items():
            low, _ = wilson(count, bucket["windows"])
            if bucket["gate_severity"].get(sid) == "context":
                continue
            if bucket["windows"] >= 10 and low > ceiling:
                failures.append(f"{lang}/{register} structure {sid}: {count}/{bucket['windows']} windows, lower bound {low:.0%} over {ceiling:.0%}")
    return failures


def render(report):
    lines = []
    for (lang, register), bucket in sorted(report.items()):
        lines.append(f"{lang}/{register}: {bucket['words']} words in {bucket['paragraphs']} paragraphs, {bucket['windows']} windows, files {bucket['files']}")
        ranked = sorted(bucket["regex"].items(), key=lambda kv: -kv[1]["hits"])
        for pid, stats in ranked[:12]:
            rate = stats["hits"] * 10_000 / max(bucket["words"], 1)
            low, high = wilson(stats["flagged"], bucket["paragraphs"])
            lines.append(f"    {rate:5.2f}/10k  {stats['flagged']:3d}/{bucket['paragraphs']} paragraphs [{low:.1%}, {high:.1%}]  {pid}  e.g. {stats['examples'][:2]}")
        for sid, count in sorted(bucket["structure"].items(), key=lambda kv: -kv[1]):
            low, high = wilson(count, bucket["windows"])
            lines.append(f"    structure {count:3d}/{bucket['windows']} windows [{low:.1%}, {high:.1%}]  {sid}")
    for lang, totals in per_language(report).items():
        worst = sorted(totals["regex"].items(), key=lambda kv: -kv[1])[:5]
        lines.append(f"{lang} overall: {totals['words']} words; worst " + ", ".join(f"{pid} {hits * 10_000 / totals['words']:.2f}/10k" for pid, hits in worst))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--committed", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--fail", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--threshold-regex", type=float, default=2.0)
    parser.add_argument("--threshold-register", type=float, default=4.0)
    args = parser.parse_args()
    scan = load_scanner()
    rows = load_manifest(committed_only=not args.all)
    if not rows:
        sys.exit("no corpus files present; run control/fetch.sh")
    report = measure(rows, scan)
    failures = judge(report, args.threshold_regex, args.threshold_register)
    if args.json:
        print(json.dumps({f"{k[0]}/{k[1]}": {"words": v["words"], "paragraphs": v["paragraphs"], "windows": v["windows"], "regex": v["regex"], "structure": v["structure"]} for k, v in report.items()}, ensure_ascii=False, indent=1))
    else:
        print(render(report))
    if failures:
        print("\nover the false-positive limit:")
        for f in failures:
            print("  " + f)
    sys.exit(1 if failures and args.fail else 0)


if __name__ == "__main__":
    main()
