#!/usr/bin/env python3
"""Flow metrics for any board, from a normalized work-item JSON file.

Offline and credential-free by design: you convert board data (any tracker) to
the small normalized shape below, this script does the arithmetic. Nothing here
talks to a network. The per-tool conversion recipes live in flow.md.

Input: one or more JSON files, each an array of items (or {"items": [...]}):

    {"id": "42", "title": "ci: bring pipeline under 8 minutes",
     "state": "doing",              // open | ready | doing | review | done | dropped
     "started": "2026-08-01T09:00:00Z",   // when work STARTED (entered doing) — ISO8601 or epoch ms; null/absent if never started
     "finished": null,                    // when it reached the team's real done; ISO8601 or epoch ms
     "created": "2026-07-01T09:00:00Z",   // optional; only used for the labeled lead-time proxy
     "priority": "P0"}                    // optional: P0|P1|P2|P3

Metrics follow the Kanban Guide (v2025.5): WIP is items started but not
finished, Work Item Age is start -> now, Cycle Time is start -> finish, and a
Service Level Expectation is an elapsed period WITH a probability attached.

Where `started` is missing the script falls back to created -> finished and
labels the result a LEAD TIME PROXY: `created` is when someone wrote the
ticket, not when anyone started it. It refuses to state an SLE below
--min-samples finished items, because a percentile over five tickets is theatre.

Usage:
    python3 flow_metrics.py --items board.json --wip-limit 3 --percentile 85
    python3 flow_metrics.py --items open.json done.json --json
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

MINUTES_PER_DAY = 60 * 24
STARTED_STATES = ("doing", "review")  # started but not finished; overridable
DONE_STATE = "done"


class DataError(Exception):
    """Input that cannot be interpreted as normalized work items."""


def load_items(paths: list[Path]) -> list[dict]:
    by_id: dict[str, dict] = {}
    for path in paths:
        try:
            data = json.loads(path.read_text())
        except FileNotFoundError:
            raise DataError(f"{path}: no such file")
        except json.JSONDecodeError as exc:
            raise DataError(f"{path}: invalid JSON — {exc}")
        items = data.get("items") if isinstance(data, dict) else data
        if not isinstance(items, list):
            raise DataError(f"{path}: expected an array or {{\"items\": [...]}}")
        for item in items:
            if not isinstance(item, dict) or "id" not in item:
                raise DataError(f"{path}: entry without an 'id' — not a normalized item list")
            by_id[str(item["id"])] = item  # later files win
    if not by_id:
        raise DataError("no items found in the supplied files")
    return list(by_id.values())


def as_ms(value: object) -> int | None:
    """Accept epoch ms (int/str) or ISO8601; return epoch ms or None."""
    if value in (None, "", "null"):
        return None
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.strip().isdigit()):
        ms = int(float(value))
        return ms if ms > 10**11 else ms * 1000 if ms > 10**8 else None
    if isinstance(value, str):
        try:
            moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if moment.tzinfo is None:
            moment = moment.replace(tzinfo=timezone.utc)
        return int(moment.timestamp() * 1000)
    return None


def fmt_duration(minutes: float | None) -> str:
    if minutes is None:
        return "—"
    days, rem = divmod(int(round(minutes)), MINUTES_PER_DAY)
    hours, mins = divmod(rem, 60)
    if days:
        return f"{days}d {hours}h"
    return f"{hours}h {mins}m" if hours else f"{mins}m"


def percentile(values: list[float], pct: float) -> float:
    """Nearest-rank percentile — the convention SLEs are quoted with."""
    ordered = sorted(values)
    rank = max(1, math.ceil(pct / 100 * len(ordered)))
    return ordered[min(rank, len(ordered)) - 1]


def analyse(items: list[dict], args) -> dict:
    now_ms = args.now if args.now is not None else int(datetime.now(timezone.utc).timestamp() * 1000)
    started_states = tuple(s.lower() for s in args.started_states)

    in_progress, completions = [], []
    age_proxy = cycle_proxy = False
    bad_timestamps = 0
    for item in items:
        state = str(item.get("state", "")).lower()
        for key in ("started", "finished", "created"):
            if item.get(key) not in (None, "", "null") and as_ms(item.get(key)) is None:
                bad_timestamps += 1
        started = as_ms(item.get("started"))
        finished = as_ms(item.get("finished"))
        created = as_ms(item.get("created"))
        title = str(item.get("title", "")).strip()

        if state in started_states and finished is None:
            age = None
            if started is not None:
                age = (now_ms - started) / 60000
                measured = True
            elif created is not None:
                age = (now_ms - created) / 60000
                measured, age_proxy = False, True
            else:
                measured = False
            in_progress.append({"id": str(item["id"]), "title": title,
                                "minutes": age, "measured": measured})
        elif state == args.done_state.lower() or finished is not None:
            cycle = None
            measured = False
            if finished is not None and started is not None:
                cycle, measured = (finished - started) / 60000, True
            elif finished is not None and created is not None:
                cycle, cycle_proxy = (finished - created) / 60000, True
            completions.append({"id": str(item["id"]), "title": title,
                                "finished_ms": finished, "minutes": cycle, "measured": measured})

    cycle_times = [c["minutes"] for c in completions if c["minutes"] is not None]
    unmeasurable = [c for c in completions if c["minutes"] is None]

    sle = None
    if len(cycle_times) >= args.min_samples:
        sle = {"percentile": args.percentile,
               "days": percentile(cycle_times, args.percentile) / MINUTES_PER_DAY,
               "samples": len(cycle_times),
               "includes_proxy": cycle_proxy}

    in_progress = sorted(in_progress, key=lambda i: i["minutes"] or -1, reverse=True)
    return {
        "wip": {"count": len(in_progress), "limit": args.wip_limit,
                "over_by": max(0, len(in_progress) - args.wip_limit)},
        "in_progress": in_progress,
        "throughput": throughput_by_week(completions),
        "cycle_time": {
            "samples": len(cycle_times),
            "median_days": (percentile(cycle_times, 50) / MINUTES_PER_DAY) if cycle_times else None,
            "p85_days": (percentile(cycle_times, 85) / MINUTES_PER_DAY) if cycle_times else None,
            "max_days": (max(cycle_times) / MINUTES_PER_DAY) if cycle_times else None,
            "lead_time_proxy": cycle_proxy,
            "finished": len(completions),
            "unmeasurable": len(unmeasurable),
        },
        "sle": sle,
        "findings": find_violations(items, in_progress, unmeasurable, bad_timestamps, args),
        "state_counts": Counter(str(i.get("state", "?")).lower() for i in items),
    }


def throughput_by_week(completions: list[dict]) -> list[tuple[str, int]]:
    weeks: Counter[str] = Counter()
    for item in completions:
        if item["finished_ms"] is None:
            continue
        moment = datetime.fromtimestamp(item["finished_ms"] / 1000, tz=timezone.utc)
        monday = moment - timedelta(days=moment.weekday())
        weeks[monday.strftime("%Y-%m-%d")] += 1
    return sorted(weeks.items())


def looks_like_a_product_name(title: str) -> bool:
    """A title with no separator and at most two words names an installation,
    not a result — the most common board defect."""
    if ":" in title or "—" in title or " - " in title:
        return False
    return 0 < len(title.split()) <= 2


def find_violations(items: list[dict], in_progress: list[dict],
                    unmeasurable: list[dict], bad_timestamps: int, args) -> list[dict]:
    findings: list[dict] = []
    if bad_timestamps:
        findings.append({"kind": "bad-timestamp", "count": bad_timestamps,
                         "message": "timestamp value(s) could not be parsed (not ISO8601 or "
                                    "epoch ms) — silently treated as absent; check the input",
                         "items": []})

    def add(kind: str, message: str, entries: list[str]) -> None:
        if entries:
            findings.append({"kind": kind, "message": message, "count": len(entries),
                             "items": entries[: args.max_items]})

    if len(in_progress) > args.wip_limit:
        add("wip-limit", f"{len(in_progress)} items started, limit is {args.wip_limit} — "
                         "finish before starting",
            [f"{i['title']} ({fmt_duration(i['minutes'])} old)" for i in in_progress])

    open_items = [i for i in items
                  if str(i.get("state", "")).lower() not in (args.done_state.lower(), "dropped")]

    add("title", "titles that name a product instead of a change",
        [f"{i.get('title')} [{i.get('state')}]" for i in open_items
         if looks_like_a_product_name(str(i.get("title", "")))])

    p0 = [str(i.get("title", "")) for i in open_items
          if str(i.get("priority", "")).upper() in ("P0", "URGENT", "5")]
    if len(p0) > args.max_p0:
        add("p0-inflation", f"{len(p0)} open P0s — if six things are urgent, nothing is", p0)

    add("no-measured-start",
        "finished without a recorded start — no start, so no Cycle Time and no SLE contribution",
        [c["title"] for c in unmeasurable])

    return findings


def render(report: dict, args) -> str:
    out: list[str] = []
    wip = report["wip"]
    out.append(f"WIP {wip['count']} / {wip['limit']}  [{'OVER LIMIT' if wip['over_by'] else 'ok'}]")

    if report["in_progress"]:
        out.append("\nWork Item Age (oldest first)")
        for item in report["in_progress"][: args.max_items]:
            mark = "" if item["measured"] else (
                "  (no start recorded)" if item["minutes"] is None else "  ~proxy from created")
            out.append(f"  {fmt_duration(item['minutes']):>10}  {item['title'][:64]}{mark}")

    cycle = report["cycle_time"]
    out.append(f"\nCycle Time  ({cycle['samples']} of {cycle['finished']} finished measurable"
               + (", some from created — LEAD TIME PROXY" if cycle["lead_time_proxy"] else "") + ")")
    if cycle["samples"]:
        out.append(f"  median {cycle['median_days']:.1f}d · 85th {cycle['p85_days']:.1f}d "
                   f"· max {cycle['max_days']:.1f}d")
    elif cycle["finished"]:
        out.append(f"  none measurable — all {cycle['unmeasurable']} finished items lack a start")
    else:
        out.append("  no finished items in the supplied data")

    if report["throughput"]:
        out.append("\nThroughput (finished per week)")
        for week, count in report["throughput"][-args.max_weeks:]:
            out.append(f"  {week}  {'#' * min(count, 40)} {count}")

    out.append("")
    if report["sle"]:
        sle = report["sle"]
        proxy_note = " — includes lead-time-proxy samples" if sle.get("includes_proxy") else ""
        out.append(f"SLE: {sle['percentile']:.0f}% of items finish within "
                   f"{math.ceil(sle['days'])} days  (from {sle['samples']} finished items"
                   f"{proxy_note})")
        out.append("     A forecast with a sample size, not a promise — recompute every ~10.")
    else:
        out.append(f"SLE: not stated — {report['cycle_time']['samples']} usable samples, "
                   f"need {args.min_samples}. A percentile over a handful of tickets is theatre.")

    if report["findings"]:
        out.append("\nFindings")
        for finding in report["findings"]:
            out.append(f"  [{finding['kind']}] {finding['count']}× {finding['message']}")
            for entry in finding["items"]:
                out.append(f"      - {entry[:72]}")
            if finding["count"] > len(finding["items"]):
                out.append(f"      … and {finding['count'] - len(finding['items'])} more")
    else:
        out.append("\nFindings: none from item data (the judgement checks are still yours).")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Flow metrics from normalized work items (any board).",
        epilog="Feed it converted board data; it never touches the network.")
    parser.add_argument("--items", nargs="+", required=True, type=Path,
                        help="normalized work-item JSON file(s) — see the module docstring")
    parser.add_argument("--wip-limit", type=int, default=3)
    parser.add_argument("--percentile", type=float, default=85.0)
    parser.add_argument("--min-samples", type=int, default=10,
                        help="refuse to state an SLE below this many finished items")
    parser.add_argument("--started-states", nargs="+", default=list(STARTED_STATES))
    parser.add_argument("--done-state", default=DONE_STATE)
    parser.add_argument("--max-p0", type=int, default=3)
    parser.add_argument("--max-items", type=int, default=12)
    parser.add_argument("--max-weeks", type=int, default=12)
    parser.add_argument("--now", type=int, default=None,
                        help="epoch ms to treat as 'now' (for reproducible output)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if not 0 < args.percentile < 100:
        parser.error("--percentile must be between 0 and 100 (exclusive)")
    if args.wip_limit < 1:
        parser.error("--wip-limit must be at least 1")

    try:
        items = load_items(args.items)
    except DataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = analyse(items, args)
    if args.json:
        report["state_counts"] = dict(report["state_counts"])
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(render(report, args))
    return 0


if __name__ == "__main__":
    sys.exit(main())
