#!/usr/bin/env python3
"""Turn quality-retest results into the COMPARISON.md tables, one labelled block per run.

Usage: render_results.py "Before the stance fix=seed1.json" "After=seed2.json"
"""
import json
import sys
from pathlib import Path

COMPARISON = Path(__file__).resolve().parents[1] / "COMPARISON.md"
MARKER = "## What we did not take"
BLOCK_START = "<!-- quality-retest results -->"
BLOCK_END = "<!-- /quality-retest results -->"


def load(path):
    data = json.load(open(path))
    return data["result"] if "result" in data else data


def cell(rows, key, fmt=lambda v: v):
    return " / ".join(str(fmt(r[key])) for r in rows)


def table(title, runs, comparison):
    langs = ("en", "nl")
    lines = [f"**{title}**", "", "| Case | Skill | Facts kept | Invented | Naturalness | Flattened | Leakage |", "| --- | --- | ---: | ---: | ---: | --- | ---: |"]
    tally = {"won": 0, "lost": 0, "tie": 0}
    for lang in langs:
        cases = {}
        for run in runs:
            for row in run[comparison][lang]:
                cases.setdefault(row["case"], []).append(row)
        for case, rows in cases.items():
            verdicts = [r.get("skill", r.get("status")) for r in rows]
            for v in verdicts:
                tally[v] = tally.get(v, 0) + 1
            lines.append(
                f"| `{case}` | {' / '.join(verdicts)} | {cell(rows, 'facts')} | {cell(rows, 'invented', len)} | "
                f"{' / '.join(','.join(map(str, r['naturalness'])) for r in rows)} | {cell(rows, 'flattened')} | {cell(rows, 'leakage')} |"
            )
    lines += ["", f"Skill won {tally.get('won', 0)}, lost {tally.get('lost', 0)}, tied {tally.get('tie', 0)} across {len(runs)} seed(s).", ""]
    return "\n".join(lines)


def render_run(run, label):
    return "\n".join([
        f"**{label}** (seed {run['seed']}). Routing misses {len(run['routing_misses'])}; leakage findings "
        f"{sum(run['leakage'].values())}. Flattening constants: ratio {run['constants']['FLATTEN_RATIO']} to the "
        f"original's variation, floor {run['constants']['FLATTEN_FLOOR']}.",
        "",
        table("Rewrite against a free rewrite", [run], "rewrite"),
        table("Edit against a minimal edit", [run], "edit"),
    ])


def main():
    pairs = [arg.split("=", 1) for arg in sys.argv[1:]]
    blocks = [render_run(load(path), label) for label, path in pairs]
    block = "\n\n".join(blocks)
    text = COMPARISON.read_text()
    if BLOCK_START in text:
        before, rest = text.split(BLOCK_START, 1)
        _, after = rest.split(BLOCK_END, 1)
        text = before.rstrip() + "\n\n" + BLOCK_START + "\n" + block + "\n" + BLOCK_END + after
    else:
        head, tail = text.split(MARKER, 1)
        text = head.rstrip() + "\n\n" + BLOCK_START + "\n" + block + "\n" + BLOCK_END + "\n\n" + MARKER + tail
    COMPARISON.write_text(text)
    print(block)


if __name__ == "__main__":
    main()
