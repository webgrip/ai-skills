#!/usr/bin/env python3
"""Scan prose for the regex-detectable tells of AI-generated writing.

Usage:
    scan.py [--lang en|nl|auto] [--json] [--fail-on always|cluster|context|never]
            [--fail-on-structure always|cluster|context|never] [--no-structure]
            [--domain wikipedia|fiction|all] [--patterns FILE] [FILE ...]
    scan.py --compare BEFORE AFTER

Reads the files (or stdin) and reports every match of the patterns in
patterns.json next to this script, plus density metrics the regexes cannot
express (em dashes per 500 words, sentence-length variance, paragraph-length
uniformity). Fenced code blocks and blockquotes are skipped: quoted text and
code are never the writer's own prose. Patterns about Markdown appearing on a
surface that does not render it are skipped when the input is Markdown.
Patterns that only make sense on Wikipedia or in fiction load with --domain.
Structure gates read the document's skeleton, which no regex can see: slot
headings on a short text, a bold label above a list, a three-item list of
parallel items, uniform paragraphs, a one-line closer, em-dash density, and a
flat sentence rhythm that only counts alongside another structure tell. They
never fail the scan unless --fail-on-structure says so. --compare measures a
rewrite against its original: character-level change rate, numbers injected
(a hard failure) or dropped (advisory), and whether the rhythm flattened. Exit status 1 when a finding at or
above --fail-on exists (default: always).
"""

import argparse
import json
import re
import difflib
import statistics
import sys
from collections import Counter, namedtuple
from pathlib import Path

SEVERITY_RANK = {"always": 3, "cluster": 2, "context": 1, "never": 0}
DUTCH_STOPWORDS = {"de", "het", "een", "en", "van", "niet", "dat", "die", "is", "op", "te", "zijn", "voor", "met", "als", "maar", "ook", "wij", "je", "we"}
ENGLISH_STOPWORDS = {"the", "and", "of", "to", "a", "in", "is", "that", "it", "for", "with", "as", "on", "this", "are", "be", "not", "but", "you", "we"}
EM_DASH = "—"
SPACED_EN_DASH = re.compile(r"\s–\s")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+")
WORD = re.compile(r"[A-Za-zÀ-ÿ'’]+")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+\S")
BULLET = re.compile(r"^\s*[-*+•]\s+\S")
NUMBERED = re.compile(r"^\s*\d{1,3}[.)]\s+\S")
LABEL = re.compile(r"^\s*\*\*[^*\n]{1,80}\*\*:?\s*$")
BOLD_SPAN = re.compile(r"\*\*[^*\r\n]+?\*\*")
LIST_SEPARATOR_DASH = re.compile(r"^\s*[-*+]\s+(?:\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))(?:\s*\([^)]*\)|\s*`[^`]*`)?\s*—", re.M)
VERSION_HEADING_DASH = re.compile(r"^#{1,6}\s*\[?v?\d+\.\d+[^\n]*—", re.M)
LONG_SENTENCE_CHARS = 100
AUXILIARIES = {
    "en": {"is", "are", "was", "were", "has", "have", "had", "will", "would", "should", "must", "do", "does", "did", "can", "could", "may", "might", "am", "been", "being"},
    "nl": {"is", "zijn", "was", "waren", "heeft", "hebben", "had", "hadden", "wordt", "worden", "werd", "werden", "kan", "kunnen", "kon", "konden", "moet", "moeten", "zal", "zullen", "zou", "zouden", "mag", "mogen", "wil", "willen", "doet", "doen", "gaat", "gaan", "blijft", "blijven", "ben", "bent", "staat", "staan", "krijgt", "krijgen"},
}
COLON_HEADING = re.compile(r"^\s{0,3}#{1,3}\s+.+:\s*[^\d\s].*$")
NUMBER_TOKEN = re.compile(r"\d[\d.,:/%-]*")
EM_DASH_DENSITY_GATE = 3.0
FLATTEN_RATIO = 0.6
LONG_SENTENCE_RATIO = 0.5
CHANGE_WARN = 0.30
CHANGE_ABORT = 0.50
WORDS_DROPPED_WARN = 0.40

Block = namedtuple("Block", "kind line text words sentences")


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


def split_sentences(prose):
    return [s for s in SENTENCE_END.split(prose.replace("\n", " ")) if WORD.search(s)]


def block_kind(lines):
    if len(lines) == 1 and HEADING.match(lines[0]):
        return "heading"
    if all(BULLET.match(l) for l in lines):
        return "bullet_run"
    if all(NUMBERED.match(l) for l in lines):
        return "numbered_run"
    if len(lines) == 1 and LABEL.match(lines[0]) and len(WORD.findall(lines[0])) <= 8:
        return "label"
    text = " ".join(lines)
    if len(WORD.findall(text)) >= 8 and re.search(r"[.!?]", text):
        return "prose"
    return "other"


def classify_blocks(text):
    blocks, current, start = [], [], None
    def flush():
        if current:
            joined = "\n".join(current)
            blocks.append(Block(block_kind(current), start, joined, len(WORD.findall(joined)), len(split_sentences(joined))))
    for number, line in prose_lines(text):
        if line.strip():
            if not current:
                start = number
            current.append(line)
        else:
            flush()
            current, start = [], None
    flush()
    return blocks


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


def metrics(text, blocks):
    prose = "\n".join(line for _, line in prose_lines(text))
    words = WORD.findall(prose)
    word_count = max(len(words), 1)
    sentences = split_sentences(prose)
    lengths = [len(WORD.findall(s)) for s in sentences]
    paragraphs = [p for p in re.split(r"\n\s*\n", prose) if WORD.search(p)]
    paragraph_lengths = [len(WORD.findall(p)) for p in paragraphs]
    prose_blocks = [b for b in blocks if b.kind == "prose"]
    separator_dashes = len(LIST_SEPARATOR_DASH.findall(prose)) + len(VERSION_HEADING_DASH.findall(prose))
    long_sentences = sum(1 for s in sentences if len(s.strip()) >= LONG_SENTENCE_CHARS)

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
        "prose_paragraphs": len(prose_blocks),
        "headings": sum(1 for b in blocks if b.kind == "heading"),
        "bullets": sum(b.text.count("\n") + 1 for b in blocks if b.kind in ("bullet_run", "numbered_run")),
        "bold_spans": sum(len(BOLD_SPAN.findall(b.text)) for b in prose_blocks),
        "sentence_length_mean": round(statistics.mean(lengths), 1) if lengths else None,
        "long_sentences_per_1000_words": round(long_sentences * 1000 / word_count, 1),
        "em_dashes_per_1000_words": round(max(prose.count(EM_DASH) - separator_dashes, 0) * 1000 / word_count, 2),
        "type_token_ratio": round(len({w.lower() for w in words}) / word_count, 2) if len(words) >= 200 else None,
    }


def bullet_items(block):
    return [re.sub(r"^\s*(?:[-*+•]|\d{1,3}[.)])\s+", "", line) for line in block.text.split("\n")]


def strip_label(item):
    return re.sub(r"^\*\*[^*]+\*\*:?\s*", "", item)


def verb_free(item, lang):
    return not any(w.lower() in AUXILIARIES[lang] for w in WORD.findall(item))


def structure_finding(entry_id, category, severity, block, evidence, hint):
    return {"id": entry_id, "category": category, "severity": severity, "kind": "structure",
            "line": block.line if block else 1, "column": 1, "match": hint, "hint": hint, "evidence": evidence}


def gate_uniform_paragraphs(doc):
    prose = [b for b in doc["blocks"] if b.kind == "prose"]
    if len(prose) < 4:
        return None
    counts = [b.sentences for b in prose]
    mean = statistics.mean(counts)
    if mean >= 3 and all(abs(c - mean) <= 1 for c in counts):
        return structure_finding("uniform-paragraph-length", "structure", "cluster", prose[0], {"paragraphs": len(prose), "sentences_each": counts}, f"{len(prose)} paragraphs of {round(mean)} sentences each")
    return None


def gate_same_openers(doc):
    repeats = []
    for block in (b for b in doc["blocks"] if b.kind == "prose"):
        openers = []
        for sentence in split_sentences(block.text):
            tokens = [w.lower() for w in WORD.findall(sentence)][:2]
            if len(tokens) == 2 and tokens in openers[-2:]:
                repeats.append(" ".join(tokens))
            openers.append(tokens)
    if len(doc["sentences"]) >= 8 and len(repeats) >= 2:
        return structure_finding("same-opener-runs", "syntax", "context", None, {"repeats": repeats}, f"sentence openers repeat: {', '.join(repeats[:3])}")
    return None


def gate_bold_overuse(doc):
    prose = [b for b in doc["blocks"] if b.kind == "prose"]
    spans = sum(len(BOLD_SPAN.findall(b.text)) for b in prose)
    if spans > 3 and spans > doc["words"] / 250:
        return structure_finding("bold-overuse", "punctuation-format", "cluster", prose[0] if prose else None, {"bold_spans": spans, "words": doc["words"]}, f"{spans} bold spans in {doc['words']} words of prose")
    return None


def gate_colon_headings(doc):
    headings = [b for b in doc["blocks"] if b.kind == "heading"]
    colon = [b for b in headings if COLON_HEADING.match(b.text)]
    if len(colon) >= 2 and len(colon) * 2 >= len(headings):
        return structure_finding("colon-subtitle-headings", "structure", "cluster", colon[0], {"colon_headings": len(colon), "headings": len(headings)}, f"{len(colon)} of {len(headings)} headings take the X: Y shape")
    return None


def gate_slot_headings(doc):
    if not doc["markdown"]:
        return None
    headings = [b for b in doc["blocks"] if b.kind == "heading"]
    slot_regexes = [rx for entry, rx in doc["compiled"] if entry["id"] == "formulaic-section-headers"]
    slots = [b for b in headings if any(rx.search(b.text) for rx in slot_regexes)]
    words = doc["words"]
    fires = (len(slots) >= 2 and words < 600) or (len(slots) >= 1 and words < 250) or (len(headings) >= 3 and words / len(headings) < 120)
    if fires:
        return structure_finding("formulaic-section-headers", "structure", "cluster", (slots or headings)[0], {"slot_headings": len(slots), "headings": len(headings), "words": words}, f"{len(slots)} slot headings over {words} words")
    return None


def gate_label_above_list(doc):
    blocks = doc["blocks"]
    for i, block in enumerate(blocks[:-1]):
        nxt = blocks[i + 1]
        if block.kind == "label" and nxt.kind in ("bullet_run", "numbered_run") and nxt.text.count("\n") >= 1:
            return structure_finding("inline-header-lists", "structure", "cluster", block, {"label": block.text.strip()}, f"bold label above a list: {block.text.strip()[:40]}")
    return None


def triple_shape(items, lang):
    stripped = [strip_label(i) for i in items]
    counts = [len(WORD.findall(i)) for i in stripped]
    if any(c > 8 for c in counts):
        return None
    if max(counts) - min(counts) <= 1:
        return "equal length"
    if all(BOLD_SPAN.match(i.strip()) for i in items):
        return "bold labels"
    if all(verb_free(i, lang) for i in stripped):
        return "verb-free"
    return None


def gate_triples(doc):
    triples = []
    for block in (b for b in doc["blocks"] if b.kind == "bullet_run"):
        items = bullet_items(block)
        if len(items) == 3:
            shape = triple_shape(items, doc["lang"])
            if shape:
                triples.append((block, shape))
    if len(triples) >= 2 or (len(triples) == 1 and doc["words"] < 300):
        block, shape = triples[0]
        return structure_finding("rule-of-three", "syntax", "cluster", block, {"triples": len(triples), "shape": shape}, f"{len(triples)} three-item list(s) of {shape} items")
    return None


def gate_bare_noun_bullets(doc):
    for block in (b for b in doc["blocks"] if b.kind == "bullet_run"):
        items = bullet_items(block)
        if len(items) < 5:
            continue
        bare = [i for i in items if 0 < len(WORD.findall(i)) <= 6 and verb_free(i, doc["lang"])]
        if len(bare) >= 5 and len(bare) / len(items) >= 0.75:
            return structure_finding("bare-noun-phrase-bullets", "structure", "cluster", block, {"items": len(items), "bare": len(bare)}, f"{len(bare)} of {len(items)} bullets are bare noun phrases")
    return None


def gate_aphoristic_closer(doc):
    prose = [b for b in doc["blocks"] if b.kind == "prose"]
    if len(prose) < 4 or doc["words"] < 150:
        return None
    last, before = prose[-1], prose[-2]
    text = last.text.strip()
    tokens = WORD.findall(text)
    capitals_after_first = [t for t in tokens[1:] if t[0].isupper()]
    if last.sentences == 1 and len(tokens) <= 20 and not re.search(r"\d|[\"“”']", text) and not capitals_after_first and before.sentences >= 2:
        return structure_finding("aphoristic-ender", "rhetoric", "context", last, {"closer": text}, f"one-line closing paragraph: {text[:50]}")
    return None


def gate_em_dash_density(doc):
    if doc["words"] < 100:
        return None
    per_500 = doc["metrics"]["em_dashes_per_500_words"]
    if per_500 > EM_DASH_DENSITY_GATE:
        return structure_finding("em-dash-density", "punctuation-format", "cluster", None, {"em_dashes_per_500_words": per_500}, f"{per_500} em dashes per 500 words")
    return None


def gate_flat_rhythm(doc, others):
    lengths = [len(WORD.findall(s)) for s in doc["sentences"]]
    if len(lengths) < 8 or not others:
        return None
    mean = statistics.mean(lengths)
    cv = statistics.pstdev(lengths) / mean if mean else 1
    if cv < 0.25 and mean > 10:
        return structure_finding("sentence-rhythm-uniformity", "structure", "cluster", None, {"sentence_length_variation": round(cv, 2), "mean": round(mean, 1), "with": [o["id"] for o in others]}, f"sentence-length variation {cv:.2f} alongside other structure tells")
    return None


def gate_heading_levels(doc):
    headings = [b for b in doc["blocks"] if b.kind == "heading"]
    levels = [len(re.match(r"\s{0,3}(#{1,6})", b.text).group(1)) for b in headings]
    jumps = [(i, a, b) for i, (a, b) in enumerate(zip(levels, levels[1:])) if b - a > 1]
    if jumps:
        i, a, b = jumps[0]
        return structure_finding("heading-level-skipping", "punctuation-format", "cluster", headings[i + 1], {"levels": levels}, f"heading level jumps from {a} to {b}")
    return None


STRUCTURE_GATES = [gate_heading_levels, gate_uniform_paragraphs, gate_same_openers, gate_bold_overuse, gate_colon_headings, gate_slot_headings,
                   gate_label_above_list, gate_triples, gate_bare_noun_bullets, gate_aphoristic_closer, gate_em_dash_density]


def structure_findings(text, lang, blocks, compiled, markdown=True, stats=None):
    prose = "\n".join(line for _, line in prose_lines(text))
    doc = {"text": text, "lang": lang, "markdown": markdown, "blocks": blocks, "compiled": compiled,
           "sentences": split_sentences(prose), "words": len(WORD.findall(prose)), "metrics": stats or metrics(text, blocks)}
    found = [f for f in (gate(doc) for gate in STRUCTURE_GATES) if f]
    rhythm = gate_flat_rhythm(doc, found)
    return found + ([rhythm] if rhythm else [])


def strip_markup(text):
    kept = []
    for _, line in prose_lines(text):
        if re.match(r"^\s*(?:-{3,}|\*{3,}|={3,})\s*$", line):
            continue
        line = re.sub(r"^\s*(?:#{1,6}\s+|[-*+•]\s+|\d{1,3}[.)]\s+)", "", line)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"[*_`]+", "", line)
        kept.append(line)
    return re.sub(r"\s+", " ", " ".join(kept)).strip()


def compare_texts(before_text, after_text, before_blocks, after_blocks):
    before, after = strip_markup(before_text), strip_markup(after_text)
    change_rate = round(1 - difflib.SequenceMatcher(None, before, after, autojunk=False).ratio(), 3)
    before_numbers, after_numbers = Counter(NUMBER_TOKEN.findall(before)), Counter(NUMBER_TOKEN.findall(after))
    injected = sorted((after_numbers - before_numbers).elements())
    dropped = sorted((before_numbers - after_numbers).elements())
    words_before, words_after = len(WORD.findall(before)), len(WORD.findall(after))
    dropped_rate = round(max(words_before - words_after, 0) / max(words_before, 1), 3)
    m_before, m_after = metrics(before_text, before_blocks), metrics(after_text, after_blocks)
    v_before, v_after = m_before["sentence_length_variation"] or 0, m_after["sentence_length_variation"] or 0
    flattened = (v_before > 0 and v_after < FLATTEN_RATIO * v_before) or m_after["long_sentences_per_1000_words"] < LONG_SENTENCE_RATIO * m_before["long_sentences_per_1000_words"]
    reasons = []
    if change_rate > CHANGE_ABORT:
        reasons.append(f"change rate {change_rate} over {CHANGE_ABORT}")
    if injected:
        reasons.append(f"numbers injected: {injected}")
    verdict = "abort" if reasons else "ok"
    if verdict == "ok":
        if change_rate > CHANGE_WARN:
            reasons.append(f"change rate {change_rate} over {CHANGE_WARN}")
        if dropped_rate > WORDS_DROPPED_WARN:
            reasons.append(f"{dropped_rate:.0%} of words dropped")
        if flattened:
            reasons.append("rhythm flattened against the original")
        verdict = "warn" if reasons else "ok"
    return {"change_rate": change_rate, "words_before": words_before, "words_after": words_after, "words_dropped_rate": dropped_rate,
            "numbers_injected": injected, "numbers_dropped": dropped,
            "rhythm": {"variation_before": v_before, "variation_after": v_after, "long_sentences_before": m_before["long_sentences_per_1000_words"], "long_sentences_after": m_after["long_sentences_per_1000_words"], "flattened": flattened},
            "verdict": verdict, "reasons": reasons}


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


def structure_report(structure):
    if not structure:
        return "  structure: none"
    lines = [f"  structure ({len(structure)}):"]
    for finding in structure:
        lines.append(f"    L{finding['line']}  {finding['id']}  \"{finding['match']}\"")
    return "\n".join(lines)


def compare_report(compare):
    lines = [f"  compare: {compare['verdict']}  change rate {compare['change_rate']}  words {compare['words_before']} -> {compare['words_after']}"]
    if compare["numbers_injected"]:
        lines.append(f"    numbers injected: {compare['numbers_injected']}")
    if compare["numbers_dropped"]:
        lines.append(f"    numbers dropped: {compare['numbers_dropped']}")
    rhythm = compare["rhythm"]
    lines.append(f"    rhythm: variation {rhythm['variation_before']} -> {rhythm['variation_after']}, long sentences/1k {rhythm['long_sentences_before']} -> {rhythm['long_sentences_after']}{'  FLATTENED' if rhythm['flattened'] else ''}")
    for reason in compare["reasons"]:
        lines.append(f"    {reason}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*")
    parser.add_argument("--lang", choices=["en", "nl", "auto"], default="auto")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on", choices=list(SEVERITY_RANK), default="always")
    parser.add_argument("--patterns", default=str(Path(__file__).with_name("patterns.json")))
    parser.add_argument("--domain", action="append", choices=["wikipedia", "fiction", "all"], default=[])
    parser.add_argument("--fail-on-structure", choices=list(SEVERITY_RANK), default="never")
    parser.add_argument("--no-structure", action="store_true")
    parser.add_argument("--compare", nargs=2, metavar=("BEFORE", "AFTER"))
    args = parser.parse_args()

    if args.compare and args.files:
        parser.error("--compare takes exactly two files and no others")
    inputs = ([(args.compare[1], Path(args.compare[1]).read_text(encoding="utf-8"))] if args.compare
              else [(f, Path(f).read_text(encoding="utf-8")) for f in args.files] or [("stdin", sys.stdin.read())])
    results = []
    worst = 0
    worst_structure = 0
    abort = False
    for name, text in inputs:
        lang = detect_language(text) if args.lang == "auto" else args.lang
        markdown = is_markdown(name, text)
        domains = ("wikipedia", "fiction") if "all" in args.domain else tuple(args.domain)
        compiled = load_patterns(args.patterns, lang, markdown, domains)
        findings = [{**f, "kind": "pattern"} for f in find_matches(text, compiled)]
        blocks = classify_blocks(text)
        stats = metrics(text, blocks)
        structure = [] if args.no_structure else structure_findings(text, lang, blocks, compiled, markdown, stats)
        worst = max([worst] + [SEVERITY_RANK[f["severity"]] for f in findings])
        worst_structure = max([worst_structure] + [SEVERITY_RANK[f["severity"]] for f in structure])
        result = {"file": name, "lang": lang, "markdown": markdown, "metrics": stats, "findings": findings, "structure": structure}
        if args.compare:
            before_text = Path(args.compare[0]).read_text(encoding="utf-8")
            result["compare"] = {"before": args.compare[0], "after": args.compare[1], **compare_texts(before_text, text, classify_blocks(before_text), blocks)}
            abort = result["compare"]["verdict"] == "abort"
        results.append(result)
        if not args.json:
            print(report(name, findings, stats, lang))
            print(structure_report(structure))
            if args.compare:
                print(compare_report(result["compare"]))
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    threshold = SEVERITY_RANK[args.fail_on]
    structure_threshold = SEVERITY_RANK[args.fail_on_structure]
    failed = (threshold and worst >= threshold) or (structure_threshold and worst_structure >= structure_threshold) or abort
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
