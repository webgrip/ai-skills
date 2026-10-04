#!/usr/bin/env python3
"""Estimate whether a refactoring pays for itself in agent tokens before or after measuring it.

Usage:
    roi.py --model ID --baseline-input N [--baseline-output N] [--after-input N | --saving PCT ...]
           [--after-output N] [--cache-read-share 0.75] [--refactor-cost-usd X | --refactor-input N --refactor-output N]
           [--review-hours H --hourly-rate EUR_OR_USD] [--changes-per-month N] [--horizon-months 12]
           [--safety-factor 2.5] [--prices FILE] [--json]

Inputs are per representative change: processed input tokens (fresh plus cache
reads, as measure.py reports them) and output tokens. Give the measured after
state, or one or more --saving percentages to model scenarios; with neither, the
published range is used: 7 % (the median of the only controlled study, Sonar
2026), 25 % and 83 % (the single-run best case in Edwards-Alexander 2026).
Input is priced as a blend: the cache-read share at the cache-read rate and the
rest at the five-minute cache-write rate, which is how agent loops bill. The
refactoring's own cost comes from measured tokens or dollars, plus human review
time when given. Prints saving per change, break-even changes, payback months,
net value over the horizon and a verdict: refactor only when the changes
expected over the horizon reach the safety factor times break-even, because one
change measured a few times is a noisy estimate of every future change.
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PUBLISHED_SAVINGS = (7.0, 25.0, 83.0)
PER_MILLION = 1_000_000


def load_rates(path, model):
    data = json.loads(Path(path).read_text())
    matches = [key for key in data["models"] if model.startswith(key)]
    if not matches:
        sys.exit(f"no price for {model} in {path}; known: {', '.join(data['models'])}")
    return data["models"][max(matches, key=len)], data["source"], data["fetched"]


def change_cost(input_tokens, output_tokens, rates, cache_read_share):
    blended = cache_read_share * rates["cache_read"] + (1 - cache_read_share) * rates["cache_write_5m"]
    return (input_tokens * blended + output_tokens * rates["output"]) / PER_MILLION


def scenario(label, after_input, after_output, arguments, rates, baseline_cost, refactor_cost):
    after_cost = change_cost(after_input, after_output, rates, arguments.cache_read_share)
    saving = baseline_cost - after_cost
    row = {"scenario": label, "after_input": round(after_input), "after_output": round(after_output),
           "cost_per_change": round(after_cost, 4), "saving_per_change": round(saving, 4)}
    if saving > 0:
        row["break_even_changes"] = round(refactor_cost / saving, 1)
        if arguments.changes_per_month:
            monthly = saving * arguments.changes_per_month
            row["payback_months"] = round(refactor_cost / monthly, 1)
            row["net_over_horizon"] = round(monthly * arguments.horizon_months - refactor_cost, 2)
            expected = arguments.changes_per_month * arguments.horizon_months
            row["verdict"] = "refactor" if expected >= arguments.safety_factor * row["break_even_changes"] else "wait"
    else:
        row["break_even_changes"] = None
        row["verdict"] = "wait"
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True)
    parser.add_argument("--baseline-input", type=float, required=True)
    parser.add_argument("--baseline-output", type=float, default=0.0)
    parser.add_argument("--after-input", type=float)
    parser.add_argument("--after-output", type=float)
    parser.add_argument("--saving", type=float, action="append", help="input-token saving in percent; repeatable")
    parser.add_argument("--cache-read-share", type=float, default=0.75, help="share of processed input billed as cache reads")
    parser.add_argument("--refactor-cost-usd", type=float)
    parser.add_argument("--refactor-input", type=float, default=0.0, help="processed input tokens spent refactoring")
    parser.add_argument("--refactor-output", type=float, default=0.0)
    parser.add_argument("--review-hours", type=float, default=0.0)
    parser.add_argument("--hourly-rate", type=float, default=0.0)
    parser.add_argument("--changes-per-month", type=float)
    parser.add_argument("--horizon-months", type=float, default=12.0)
    parser.add_argument("--safety-factor", type=float, default=2.5, help="expected changes must reach this multiple of break-even")
    parser.add_argument("--prices", default=str(SCRIPT_DIR / "prices.json"))
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args()

    if not 0 <= arguments.cache_read_share <= 1:
        sys.exit("--cache-read-share must be between 0 and 1")
    rates, source, fetched = load_rates(arguments.prices, arguments.model)
    token_spend = arguments.refactor_cost_usd if arguments.refactor_cost_usd is not None else change_cost(
        arguments.refactor_input, arguments.refactor_output, rates, arguments.cache_read_share)
    refactor_cost = token_spend + arguments.review_hours * arguments.hourly_rate
    baseline_cost = change_cost(arguments.baseline_input, arguments.baseline_output, rates, arguments.cache_read_share)
    after_output = arguments.after_output if arguments.after_output is not None else arguments.baseline_output

    if arguments.after_input is not None:
        rows = [scenario("measured", arguments.after_input, after_output, arguments, rates, baseline_cost, refactor_cost)]
    else:
        savings = arguments.saving or list(PUBLISHED_SAVINGS)
        rows = [scenario(f"{pct:g} % input saving", arguments.baseline_input * (1 - pct / 100), after_output,
                         arguments, rates, baseline_cost, refactor_cost) for pct in savings]

    result = {"model": arguments.model, "prices": {"source": source, "fetched": fetched},
              "baseline_cost_per_change": round(baseline_cost, 4), "refactor_cost": round(refactor_cost, 2),
              "token_spend": round(token_spend, 2), "cache_read_share": arguments.cache_read_share, "scenarios": rows}
    if arguments.json:
        print(json.dumps(result, indent=2))
        return
    print(f"{arguments.model}: baseline {baseline_cost:.4f} per change; refactoring cost {refactor_cost:.2f} "
          f"(tokens {token_spend:.2f}, review {refactor_cost - token_spend:.2f}). Prices from {source}, fetched {fetched}.\n")
    print("| Scenario | After input | Cost per change | Saving per change | Break-even changes | Payback months | Net over horizon | Verdict |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        even = "never" if row["break_even_changes"] is None else f"{row['break_even_changes']:,.0f}"
        payback = f"{row['payback_months']:.1f}" if "payback_months" in row else "-"
        net = f"{row['net_over_horizon']:.2f}" if "net_over_horizon" in row else "-"
        verdict = row.get("verdict", "-")
        print(f"| {row['scenario']} | {row['after_input']:,} | {row['cost_per_change']:.4f} | {row['saving_per_change']:.4f} | {even} | {payback} | {net} | {verdict} |")


if __name__ == "__main__":
    main()
