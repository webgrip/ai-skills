#!/usr/bin/env python3
"""Measure what a fresh coding agent spends on the same change across code versions.

Usage:
    measure.py run    --repo DIR --refs REF[,REF...] --prompt FILE [--check CMD] [--repeats N]
                      [--agent claude|codex] [--model ID] [--effort LEVEL] [--max-budget-usd X]
                      [--mode hermetic|as-shipped] [--agent-cmd TEMPLATE] [--extra-arg ARG ...]
                      [--out DIR] [--seed N]
    measure.py parse  [--adapter claude|codex] [--prices FILE] [--model ID] STREAM [STREAM ...]
    measure.py report RUNS_DIR [--baseline REF] [--prices FILE] [--refactor-cost-usd X]
                      [--changes-per-month N] [--json]

run creates one detached git worktree per trial outside the repository, runs the
agent headless on the same prompt, runs the acceptance check, records the usage
the agent's own stream reports, and removes the worktree. Variants are
interleaved in a seeded random order so drift in the provider, the cache or the
network spreads over every variant. parse summarises existing stream files.
report prints median and interquartile range per variant, the ratio of medians
against the baseline with a bootstrap 95 % interval, pass rate, and cost per
passing change (median cost divided by pass rate). Given the refactoring's own
cost it adds the number of changes to break even, computed on cost per passing
change so a cheaper but less reliable variant does not look like a saving.
Costs are recomputed from token counts with a dated price file; they are
list-price estimates, not a bill.
"""

import argparse
import json
import os
import random
import shlex
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_PRICES = SCRIPT_DIR / "prices.json"
BOOTSTRAP_SAMPLES = 2000
CLAUDE_TOOLS = "Read,Edit,Write,Glob,Grep,Bash"
PINNED_ENVIRONMENT = {
    "DISABLE_AUTOUPDATER": "1",
    "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
    "CLAUDE_CODE_DISABLE_BACKGROUND_TASKS": "1",
    "CLAUDE_CODE_PROMPT_CACHE_TTL": "5m",
    "CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL": "5m",
}
METRICS = ("processed_input", "fresh_input", "cache_read", "output", "cost_usd", "turns", "files_read", "tool_result_bytes")


@dataclass
class Usage:
    input: int = 0
    cache_write_5m: int = 0
    cache_write_1h: int = 0
    cache_read: int = 0
    output: int = 0

    @property
    def cache_write(self):
        return self.cache_write_5m + self.cache_write_1h

    def add(self, other):
        self.input += other.input
        self.cache_write_5m += other.cache_write_5m
        self.cache_write_1h += other.cache_write_1h
        self.cache_read += other.cache_read
        self.output += other.output


@dataclass
class Trial:
    adapter: str
    stream: str
    valid: bool
    model: str = ""
    agent_version: str = ""
    per_model: dict = field(default_factory=dict)
    processed_input: int = 0
    fresh_input: int = 0
    cache_read: int = 0
    output: int = 0
    cost_usd: float = 0.0
    reported_cost_usd: float = 0.0
    turns: int = 0
    files_read: int = 0
    tool_result_bytes: int = 0
    tool_calls: dict = field(default_factory=dict)
    subagent_share: float = 0.0
    overhead_first_request: int = 0
    notes: list = field(default_factory=list)
    ref: str = ""
    repeat: int = 0
    passed: bool = None
    wall_seconds: float = 0.0
    diff_numstat: str = ""


def load_prices(path):
    data = json.loads(Path(path).read_text())
    return data["source"], data["fetched"], data["models"]


def price_for(model, prices):
    candidates = [key for key in prices if model.startswith(key)]
    return prices[max(candidates, key=len)] if candidates else None


def cost_of(model, usage, prices):
    rate = price_for(model, prices)
    if rate is None:
        return None
    per_token = 1_000_000
    return (usage.input * rate["input"]
            + usage.cache_write_5m * rate["cache_write_5m"]
            + usage.cache_write_1h * rate["cache_write_1h"]
            + usage.cache_read * rate["cache_read"]
            + usage.output * rate["output"]) / per_token


def read_events(path):
    events = []
    for line in Path(path).read_text(errors="replace").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def text_size(content):
    if isinstance(content, str):
        return len(content.encode())
    if isinstance(content, list):
        return sum(text_size(part.get("text", "")) if isinstance(part, dict) else text_size(part) for part in content)
    return 0


def parse_claude(path, prices, default_ttl="5m"):
    events = read_events(path)
    trial = Trial(adapter="claude", stream=str(path), valid=False)
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    trial.model = init.get("model", "")
    trial.agent_version = init.get("claude_code_version", "")
    results = [e for e in events if e.get("type") == "result"]
    if not results:
        trial.notes.append("no result event; the run did not finish")
        return trial
    final = results[-1]
    if len(results) > 1:
        trial.notes.append(f"{len(results)} result events; used the last")
    trial.valid = final.get("subtype") == "success" and not final.get("is_error")
    if not trial.valid:
        trial.notes.append(f"result subtype {final.get('subtype')}")
    trial.reported_cost_usd = float(final.get("total_cost_usd") or 0.0)

    seen, write_split, groups = set(), {}, {}
    files, tool_calls, first_main = set(), {}, None
    for event in events:
        if event.get("type") != "assistant":
            continue
        message = event.get("message") or {}
        identifier = message.get("id")
        group = event.get("parent_tool_use_id") or "main"
        for block in message.get("content") or []:
            if block.get("type") == "tool_use":
                name = block.get("name", "?")
                tool_calls[name] = tool_calls.get(name, 0) + 1
                path_read = (block.get("input") or {}).get("file_path")
                if name == "Read" and path_read:
                    files.add(path_read)
        if identifier in seen:
            continue
        seen.add(identifier)
        usage = message.get("usage") or {}
        model = message.get("model", "")
        split = usage.get("cache_creation") or {}
        bucket = write_split.setdefault(model, [0, 0])
        bucket[0] += split.get("ephemeral_5m_input_tokens", 0)
        bucket[1] += split.get("ephemeral_1h_input_tokens", 0)
        processed = usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
        groups[group] = groups.get(group, 0) + processed
        if group == "main" and first_main is None:
            first_main = processed
    for event in events:
        if event.get("type") != "user":
            continue
        content = (event.get("message") or {}).get("content")
        if isinstance(content, list):
            trial.tool_result_bytes += sum(text_size(part.get("content")) for part in content if isinstance(part, dict) and part.get("type") == "tool_result")

    total = Usage()
    for model, entry in (final.get("modelUsage") or {}).items():
        written = entry.get("cacheCreationInputTokens", 0)
        five, hour = write_split.get(model, [0, 0])
        share_1h = hour / (five + hour) if five + hour else (1.0 if default_ttl == "1h" else 0.0)
        usage = Usage(input=entry.get("inputTokens", 0), cache_write_1h=round(written * share_1h),
                      cache_read=entry.get("cacheReadInputTokens", 0), output=entry.get("outputTokens", 0))
        usage.cache_write_5m = written - usage.cache_write_1h
        computed = cost_of(model, usage, prices)
        if computed is None:
            trial.notes.append(f"no price for {model}; used the agent's own estimate")
            computed = float(entry.get("costUSD") or 0.0)
        trial.per_model[model] = {**asdict(usage), "cost_usd": round(computed, 6)}
        trial.cost_usd += computed
        total.add(usage)
    fill(trial, total)
    trial.turns = sum(1 for _ in seen)
    trial.files_read = len(files)
    trial.tool_calls = tool_calls
    trial.overhead_first_request = first_main or 0
    subagents = sum(value for key, value in groups.items() if key != "main")
    trial.subagent_share = round(subagents / sum(groups.values()), 3) if groups and sum(groups.values()) else 0.0
    return trial


def parse_codex(path, prices, model):
    events = read_events(path)
    trial = Trial(adapter="codex", stream=str(path), valid=False, model=model)
    total, files = Usage(), set()
    completed = [e for e in events if e.get("type") == "turn.completed"]
    for event in completed:
        usage = event.get("usage") or {}
        cached = usage.get("cached_input_tokens", 0)
        total.add(Usage(input=usage.get("input_tokens", 0) - cached, cache_read=cached, output=usage.get("output_tokens", 0)))
    for event in events:
        item = event.get("item") or {}
        if item.get("type") == "command_execution":
            trial.tool_calls["command"] = trial.tool_calls.get("command", 0) + 1
            trial.tool_result_bytes += text_size(item.get("aggregated_output", ""))
        if item.get("type") == "file_change":
            for change in item.get("changes") or []:
                files.add(change.get("path", ""))
    trial.valid = bool(completed) and not any(e.get("type") == "turn.failed" for e in events)
    if not completed:
        trial.notes.append("no turn.completed event; codex reports no usage for failed turns")
    computed = cost_of(model, total, prices) if model else None
    trial.cost_usd = computed or 0.0
    if model and computed is None:
        trial.notes.append(f"no price for {model}")
    trial.per_model[model or "unknown"] = asdict(total)
    fill(trial, total)
    trial.turns = len(completed)
    trial.files_read = len(files)
    return trial


def fill(trial, total):
    trial.processed_input = total.input + total.cache_write + total.cache_read
    trial.fresh_input = total.input + total.cache_write
    trial.cache_read = total.cache_read
    trial.output = total.output
    trial.cost_usd = round(trial.cost_usd, 6)


def parse_stream(path, adapter, prices, model="", cache_ttl="5m"):
    return parse_claude(path, prices, cache_ttl) if adapter == "claude" else parse_codex(path, prices, model)


def claude_command(arguments, prompt):
    command = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--no-session-persistence", "--permission-mode", "acceptEdits", "--tools", CLAUDE_TOOLS]
    if arguments.model:
        command += ["--model", arguments.model]
    if arguments.effort:
        command += ["--effort", arguments.effort]
    if arguments.max_budget_usd:
        command += ["--max-budget-usd", str(arguments.max_budget_usd)]
    if arguments.mode == "hermetic":
        command += ["--bare"] if os.environ.get("ANTHROPIC_API_KEY") else ["--safe-mode"]
    else:
        command += ["--setting-sources", "project", "--strict-mcp-config"]
    return command + list(arguments.extra_arg or [])


def codex_command(arguments, prompt):
    command = ["codex", "exec", "--json", "--full-auto"]
    if arguments.model:
        command += ["--model", arguments.model]
    return command + list(arguments.extra_arg or []) + [prompt]


def agent_command(arguments, prompt, prompt_file):
    if arguments.agent_cmd:
        return shlex.split(arguments.agent_cmd.format(prompt_file=shlex.quote(str(prompt_file))))
    return claude_command(arguments, prompt) if arguments.agent == "claude" else codex_command(arguments, prompt)


def run_trial(arguments, ref, repeat, prompt, prompt_file, prices, out_dir):
    label = f"{ref.replace('/', '_')}-{repeat}"
    stream_path, error_path = out_dir / f"{label}.jsonl", out_dir / f"{label}.err"
    workdir = Path(tempfile.mkdtemp(prefix="measure-")) / label
    subprocess.run(["git", "-C", arguments.repo, "worktree", "add", "--detach", str(workdir), ref], check=True, capture_output=True)
    try:
        started = time.monotonic()
        with stream_path.open("w") as stream, error_path.open("w") as errors:
            subprocess.run(agent_command(arguments, prompt, prompt_file), cwd=workdir, stdout=stream, stderr=errors,
                           env={**os.environ, **PINNED_ENVIRONMENT}, check=False)
        wall = time.monotonic() - started
        passed = None
        if arguments.check:
            passed = subprocess.run(arguments.check, shell=True, cwd=workdir, capture_output=True).returncode == 0
        numstat = subprocess.run(["git", "-C", str(workdir), "diff", "--numstat"], capture_output=True, text=True).stdout
    finally:
        subprocess.run(["git", "-C", arguments.repo, "worktree", "remove", "--force", str(workdir)], capture_output=True)
    trial = parse_stream(stream_path, arguments.agent, prices, arguments.model or "")
    trial.ref, trial.repeat, trial.passed, trial.wall_seconds, trial.diff_numstat = ref, repeat, passed, round(wall, 1), numstat
    (out_dir / f"{label}.json").write_text(json.dumps(asdict(trial), indent=2))
    return trial


def command_run(arguments):
    prices = load_prices(arguments.prices)[2]
    prompt_file = Path(arguments.prompt).resolve()
    prompt = prompt_file.read_text()
    out_dir = Path(arguments.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    refs = [ref.strip() for ref in arguments.refs.split(",") if ref.strip()]
    schedule = [(ref, repeat) for repeat in range(1, arguments.repeats + 1) for ref in refs]
    random.Random(arguments.seed).shuffle(schedule)
    (out_dir / "experiment.json").write_text(json.dumps({
        "refs": refs, "baseline": refs[0], "repeats": arguments.repeats, "agent": arguments.agent, "model": arguments.model,
        "effort": arguments.effort, "mode": arguments.mode, "check": arguments.check, "prompt": prompt,
        "seed": arguments.seed, "schedule": schedule, "environment": PINNED_ENVIRONMENT,
        "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, indent=2))
    for index, (ref, repeat) in enumerate(schedule, 1):
        trial = run_trial(arguments, ref, repeat, prompt, prompt_file, prices, out_dir)
        print(f"[{index}/{len(schedule)}] {ref} #{repeat}: processed_input={trial.processed_input} output={trial.output} "
              f"cost={trial.cost_usd:.2f} passed={trial.passed} valid={trial.valid}", file=sys.stderr)
    return 0


def command_parse(arguments):
    prices = load_prices(arguments.prices)[2]
    for stream in arguments.streams:
        print(json.dumps(asdict(parse_stream(stream, arguments.adapter, prices, arguments.model or "", arguments.cache_ttl)), indent=2))
    return 0


def quartiles(values):
    if len(values) < 2:
        return values[0], values[0], values[0]
    low, middle, high = statistics.quantiles(values, n=4, method="inclusive")
    return low, middle, high


def ratio_interval(variant, baseline, seed=7):
    generator = random.Random(seed)
    ratios = []
    for _ in range(BOOTSTRAP_SAMPLES):
        resampled_variant = statistics.median(generator.choices(variant, k=len(variant)))
        resampled_baseline = statistics.median(generator.choices(baseline, k=len(baseline)))
        if resampled_baseline:
            ratios.append(resampled_variant / resampled_baseline)
    ratios.sort()
    if not ratios:
        return None, None
    return ratios[int(0.025 * len(ratios))], ratios[min(len(ratios) - 1, int(0.975 * len(ratios)))]


def load_trials(runs_dir):
    trials = []
    for path in sorted(Path(runs_dir).glob("*.json")):
        if path.name == "experiment.json":
            continue
        trials.append(json.loads(path.read_text()))
    return trials


def summarise(trials, baseline_ref, refactor_cost, changes_per_month):
    order = []
    for trial in trials:
        if trial["ref"] not in order:
            order.append(trial["ref"])
    baseline_ref = baseline_ref or (order[0] if order else "")
    by_ref = {ref: [t for t in trials if t["ref"] == ref and t["valid"]] for ref in order}
    rows = []
    baseline_input = [t["processed_input"] for t in by_ref.get(baseline_ref, [])]
    baseline_cost = [t["cost_usd"] for t in by_ref.get(baseline_ref, [])]
    for ref in order:
        valid = by_ref[ref]
        attempted = [t for t in trials if t["ref"] == ref]
        row = {"ref": ref, "trials": len(attempted), "valid": len(valid)}
        checked = [t for t in valid if t["passed"] is not None]
        row["pass_rate"] = round(sum(t["passed"] for t in checked) / len(checked), 2) if checked else None
        for metric in METRICS:
            values = [t[metric] for t in valid]
            row[metric] = quartiles(values) if values else None
        inputs = [t["processed_input"] for t in valid]
        if inputs and baseline_input and ref != baseline_ref:
            row["input_ratio"] = statistics.median(inputs) / statistics.median(baseline_input)
            row["input_ratio_ci"] = ratio_interval(inputs, baseline_input)
        row["cost_per_passing_change"] = cost_per_pass(valid, row["pass_rate"])
        rows.append(row)
    if refactor_cost:
        reference = next((row["cost_per_passing_change"] for row in rows if row["ref"] == baseline_ref), None)
        for row in rows:
            if row["ref"] == baseline_ref or reference is None or row["cost_per_passing_change"] is None:
                continue
            saving = reference - row["cost_per_passing_change"]
            row["saving_per_change_usd"] = saving
            row["break_even_changes"] = refactor_cost / saving if saving > 0 else None
            if changes_per_month and saving > 0:
                row["payback_months"] = refactor_cost / (saving * changes_per_month)
    return baseline_ref, rows


def cost_per_pass(valid, pass_rate):
    if not valid:
        return None
    median_cost = statistics.median(t["cost_usd"] for t in valid)
    if pass_rate is None:
        return median_cost
    return median_cost / pass_rate if pass_rate else None


def format_quartiles(value, money=False):
    if value is None:
        return "-"
    low, middle, high = value
    if money:
        return f"{middle:.4f} [{low:.4f}-{high:.4f}]"
    return f"{middle:,.0f} [{low:,.0f}-{high:,.0f}]"


def command_report(arguments):
    trials = load_trials(arguments.runs_dir)
    if not trials:
        print("no trials found", file=sys.stderr)
        return 1
    baseline, rows = summarise(trials, arguments.baseline, arguments.refactor_cost_usd, arguments.changes_per_month)
    source, fetched, _ = load_prices(arguments.prices)
    if arguments.json:
        print(json.dumps({"baseline": baseline, "prices": {"source": source, "fetched": fetched}, "rows": rows}, indent=2))
        return 0
    print(f"Baseline: {baseline}. Median [IQR] over valid trials. Costs: list-price estimates from {source}, fetched {fetched}.\n")
    print("| Ref | Valid/trials | Pass | Processed input | Fresh input | Cache read | Output | Cost USD | Cost per pass | Files read | Ratio vs baseline (95 % CI) |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in rows:
        ratio = "-"
        if row.get("input_ratio") is not None:
            low, high = row["input_ratio_ci"]
            ratio = f"{row['input_ratio']:.2f} ({low:.2f}-{high:.2f})" if low is not None else f"{row['input_ratio']:.2f}"
        pass_rate = "-" if row["pass_rate"] is None else f"{row['pass_rate']:.0%}"
        per_pass = "-" if row["cost_per_passing_change"] is None else f"{row['cost_per_passing_change']:.4f}"
        print(f"| {row['ref']} | {row['valid']}/{row['trials']} | {pass_rate} | {format_quartiles(row['processed_input'])} | "
              f"{format_quartiles(row['fresh_input'])} | {format_quartiles(row['cache_read'])} | {format_quartiles(row['output'])} | "
              f"{format_quartiles(row['cost_usd'], money=True)} | {per_pass} | {format_quartiles(row['files_read'])} | {ratio} |")
    if arguments.refactor_cost_usd:
        print(f"\nRefactoring cost: {arguments.refactor_cost_usd:.2f} USD")
        for row in rows:
            if "break_even_changes" in row:
                even = row["break_even_changes"]
                payback = f", payback {row['payback_months']:.1f} months" if row.get("payback_months") else ""
                print(f"- {row['ref']}: saves {row['saving_per_change_usd']:.4f} USD per change; "
                      + (f"breaks even after {even:.0f} changes{payback}" if even else "no saving, never breaks even"))
    return 0


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run")
    run.add_argument("--repo", required=True)
    run.add_argument("--refs", required=True, help="comma-separated git refs; the first is the baseline")
    run.add_argument("--prompt", required=True, help="file holding the representative change request")
    run.add_argument("--check", help="acceptance command run in the worktree after the agent finishes")
    run.add_argument("--repeats", type=int, default=5)
    run.add_argument("--agent", choices=["claude", "codex"], default="claude")
    run.add_argument("--model")
    run.add_argument("--effort")
    run.add_argument("--max-budget-usd", type=float)
    run.add_argument("--mode", choices=["hermetic", "as-shipped"], default="as-shipped")
    run.add_argument("--agent-cmd", help="custom command template; {prompt_file} is replaced by the prompt path")
    run.add_argument("--extra-arg", action="append", help="extra argument passed to the agent CLI; repeatable")
    run.add_argument("--out", default="token-runs")
    run.add_argument("--seed", type=int, default=1)
    run.add_argument("--prices", default=str(DEFAULT_PRICES))
    run.set_defaults(handler=command_run)

    parse = commands.add_parser("parse")
    parse.add_argument("streams", nargs="+")
    parse.add_argument("--adapter", choices=["claude", "codex"], default="claude")
    parse.add_argument("--model", help="model id for adapters whose stream does not name it (codex)")
    parse.add_argument("--prices", default=str(DEFAULT_PRICES))
    parse.add_argument("--cache-ttl", choices=["5m", "1h"], default="5m", help="cache write duration to assume when the stream lacks the split")
    parse.set_defaults(handler=command_parse)

    report = commands.add_parser("report")
    report.add_argument("runs_dir")
    report.add_argument("--baseline")
    report.add_argument("--prices", default=str(DEFAULT_PRICES))
    report.add_argument("--refactor-cost-usd", type=float)
    report.add_argument("--changes-per-month", type=float)
    report.add_argument("--json", action="store_true")
    report.set_defaults(handler=command_report)
    return parser


def main():
    arguments = build_parser().parse_args()
    sys.exit(arguments.handler(arguments))


if __name__ == "__main__":
    main()
