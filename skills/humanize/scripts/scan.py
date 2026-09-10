#!/usr/bin/env python3
"""Scan prose for the regex-detectable tells of AI-generated writing.

Usage:
    scan.py [--lang en|nl|auto] [--json] [--fail-on always|cluster|context|never]
            [--domain wikipedia|fiction|all] [--patterns FILE] [FILE ...]

Reads the files (or stdin) and reports every match of the patterns in
patterns.json next to this script, plus density metrics the regexes cannot
express (em dashes per 500 words, sentence-length variance, paragraph-length
uniformity). Fenced code blocks and blockquotes are skipped: quoted text and
code are never the writer's own prose. Patterns about Markdown appearing on a
surface that does not render it are skipped when the input is Markdown.
Patterns that only make sense on Wikipedia or in fiction load with --domain. Exit status 1 when a finding at or
above --fail-on exists (default: always).
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

SEVERITY_RANK = {"always": 3, "cluster": 2, "context": 1, "never": 0}
DUTCH_STOPWORDS = {"de", "het", "een", "en", "van", "niet", "dat", "die", "is", "op", "te", "zijn", "voor", "met", "als", "maar", "ook", "wij", "je", "we"}
ENGLISH_STOPWORDS = {"the", "and", "of", "to", "a", "in", "is", "that", "it", "for", "with", "as", "on", "this", "are", "be", "not", "but", "you", "we"}
EM_DASH = "—"
SPACED_EN_DASH = re.compile(r"\s–\s")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
WORD = re.compile(r"[A-Za-zÀ-ÿ'’]+")


def detect_language(text):
    words = [w.lower() for w in WORD.findall(text)]
    dutch = sum(w in DUTCH_STOPWORDS for w in words)
    english = sum(w in ENGLISH_STOPWORDS for w in words)
    return "nl" if dutch > english else "en"


def is_markdown(name, text):
    if name.lower().endswith((".md", ".markdown", ".mdx")):
        return True
    return bool(re.search(r"^(?:#{1,6} |[-*] |\d+\. |```)", text, re.M))


def load_patterns(path, lang, markdown, domains=()):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    compiled = []
    for entry in data["patterns"]:
        if lang not in entry["lang"] and "*" not in entry["lang"]:
            continue
        if markdown and entry.get("skip_on_markdown"):
            continue
        if entry.get("domain") and entry["domain"] not in domains:
            continue
        for expression in entry["regex"]:
            compiled.append((entry, re.compile(expression, re.IGNORECASE)))
    return compiled


def prose_lines(text):
    inside_fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            inside_fence = not inside_fence
            continue
        if inside_fence or line.lstrip().startswith(">"):
            continue
        yield number, line


def find_matches(text, compiled):
    findings = []
    for number, line in prose_lines(text):
        for entry, expression in compiled:
            for match in expression.finditer(line):
                findings.append({
                    "id": entry["id"],
                    "category": entry["category"],
                    "severity": entry["severity"],
                    "line": number,
                    "column": match.start() + 1,
                    "match": match.group(0),
                    "hint": entry.get("hint", ""),
                })
    return findings


def metrics(text):
    prose = "\n".join(line for _, line in prose_lines(text))
    words = WORD.findall(prose)
    word_count = max(len(words), 1)
    sentences = [s for s in SENTENCE_END.split(prose.replace("\n", " ")) if WORD.search(s)]
    lengths = [len(WORD.findall(s)) for s in sentences]
    paragraphs = [p for p in re.split(r"\n\s*\n", prose) if WORD.search(p)]
    paragraph_lengths = [len(WORD.findall(p)) for p in paragraphs]

    def variation(values):
        if len(values) < 3 or statistics.mean(values) == 0:
            return None
        return round(statistics.pstdev(values) / statistics.mean(values), 2)

    return {
        "words": len(words),
        "em_dashes_per_500_words": round(prose.count(EM_DASH) * 500 / word_count, 2),
        "spaced_en_dashes_per_500_words": round(len(SPACED_EN_DASH.findall(prose)) * 500 / word_count, 2),
        "sentence_length_variation": variation(lengths),
        "paragraph_length_variation": variation(paragraph_lengths),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
    }


def report(name, findings, stats, lang):
    lines = [f"{name}  [{lang}]  {stats['words']} words, {stats['sentences']} sentences, {stats['paragraphs']} paragraphs"]
    lines.append(
        f"  em dashes/500w: {stats['em_dashes_per_500_words']}  "
        f"spaced en dashes/500w: {stats['spaced_en_dashes_per_500_words']}  "
        f"sentence-length variation: {stats['sentence_length_variation']}  "
        f"paragraph-length variation: {stats['paragraph_length_variation']}"
    )
    by_severity = {}
    for finding in findings:
        by_severity.setdefault(finding["severity"], []).append(finding)
    for severity in ("always", "cluster", "context"):
        group = by_severity.get(severity, [])
        if not group:
            continue
        lines.append(f"  {severity} ({len(group)}):")
        for finding in group:
            lines.append(f"    L{finding['line']}:{finding['column']}  {finding['id']}  \"{finding['match']}\"")
    if not findings:
        lines.append("  no pattern matches")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*")
    parser.add_argument("--lang", choices=["en", "nl", "auto"], default="auto")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on", choices=list(SEVERITY_RANK), default="always")
    parser.add_argument("--patterns", default=str(Path(__file__).with_name("patterns.json")))
    parser.add_argument("--domain", action="append", choices=["wikipedia", "fiction", "all"], default=[])
    args = parser.parse_args()

    inputs = [(f, Path(f).read_text(encoding="utf-8")) for f in args.files] or [("stdin", sys.stdin.read())]
    results = []
    worst = 0
    for name, text in inputs:
        lang = detect_language(text) if args.lang == "auto" else args.lang
        markdown = is_markdown(name, text)
        domains = ("wikipedia", "fiction") if "all" in args.domain else tuple(args.domain)
        findings = find_matches(text, load_patterns(args.patterns, lang, markdown, domains))
        stats = metrics(text)
        worst = max([worst] + [SEVERITY_RANK[f["severity"]] for f in findings])
        results.append({"file": name, "lang": lang, "markdown": markdown, "metrics": stats, "findings": findings})
        if not args.json:
            print(report(name, findings, stats, lang))
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    threshold = SEVERITY_RANK[args.fail_on]
    sys.exit(1 if threshold and worst >= threshold else 0)


if __name__ == "__main__":
    main()
