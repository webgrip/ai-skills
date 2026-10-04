# Measurement: what the same change costs, honestly

The anchor experiment measured one run per step by counting characters ÷ 4. Every agent CLI now reports the tokens the API actually billed, so nothing needs estimating; what needs care is variance, caching and isolation.

Contents: protocol · the harness · what the numbers mean · Claude Code stream details · other agents · statistics · metering the refactoring itself · static estimates

## Protocol

1. **Freeze the variants.** Commit the baseline and each refactoring step (or milestone) so each is a git ref.
2. **Fix everything else:** model id, effort, agent CLI version (`DISABLE_AUTOUPDATER=1`), tool set, subagent model, cache TTL, prompt, acceptance check. Stamp every run.
3. **Fresh agent, fresh checkout per trial.** A detached worktree outside the repository, no session resume (a resumed session reports the whole session's spend).
4. **Repeat and interleave.** At least 5 runs per variant; 8–10 if the expected effect is under 30 %. Run variants in a seeded random order so provider, cache and network drift spread over all of them.
5. **Count only passing runs as savings.** Record pass rate separately and compare cost per passing change.
6. **Compare medians with an interval**, never two single runs.
7. **Meter the refactoring sessions too**, with the same pricing, so return on investment can be computed.

Measure after every step when steps are cheap to measure; otherwise after milestones. The anchor's series was non-monotonic (104,080 at step 12, 131,871 just before step 15), so a single cliff in a single-run series is not evidence that one step did all the work.

## The harness

```bash
python3 scripts/measure.py run --repo . --refs baseline,step-03,step-07 \
    --prompt bench/watch-store.md --check "cargo test -p data store::" \
    --model claude-sonnet-5-5 --effort medium --repeats 5 --max-budget-usd 3 --out token-runs/
python3 scripts/measure.py report token-runs/ --refactor-cost-usd 7.40 --changes-per-month 20
python3 scripts/measure.py parse --adapter claude some-run.jsonl
```

Per trial it adds a detached worktree, runs the agent headless with a pinned environment, runs the check, records `git diff --numstat`, parses the stream into a trial JSON and removes the worktree. Claude Code is run as:

```text
claude -p <prompt> --output-format stream-json --verbose --no-session-persistence
       --permission-mode acceptEdits --tools Read,Edit,Write,Glob,Grep,Bash
       --model <id> [--effort <level>] [--max-budget-usd <x>]
       hermetic:   --bare (needs ANTHROPIC_API_KEY) or --safe-mode
       as-shipped: --setting-sources project --strict-mcp-config      (default)
env: DISABLE_AUTOUPDATER=1 CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1
     CLAUDE_CODE_PROMPT_CACHE_TTL=5m CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL=5m
```

- **as-shipped** keeps the project's CLAUDE.md and settings, so it measures what your agents actually experience. Use it by default.
- **hermetic** strips customisation, which isolates the code's effect. `--bare` needs an API key; `--safe-mode` drops custom agents.
- Name the tools explicitly: `--tools default` omits Glob and Grep on Linux.
- `--agent-cmd 'my-agent --prompt-file {prompt_file}'` runs any other CLI; pick the matching `--agent` adapter for parsing.
- Each run spends real money. Estimate first: runs × variants × a baseline run's cost, and confirm the budget with whoever pays.

## What the numbers mean

| Field | Definition | Use |
| --- | --- | --- |
| `processed_input` | input + cache writes + cache reads | Caching-independent; comparable to the anchor's "input tokens" |
| `fresh_input` | input + cache writes | What this run added |
| `cache_read` | cache reads | Cheap per token, large in volume |
| `output` | output tokens | 5× input price |
| `cost_usd` | recomputed from tokens with `scripts/prices.json` | The decision number |
| `reported_cost_usd` | the agent CLI's own estimate | Sanity check only; can be stale |
| `files_read`, `tool_calls`, `tool_result_bytes` | from the stream | Where the reading went; revisits |
| `subagent_share` | share of processed input in subagents | Subagents can hide most of the spend |
| `overhead_first_request` | processed input of the first main request | The fixed prefix (system prompt, tools, CLAUDE.md), re-sent every turn |

Costs are list-price estimates, not invoices.

## Claude Code stream details

Captured from Claude Code 2.1.208 (`fixtures/claude-*.jsonl` are sanitised real captures):

- Take the **last** `type: "result"` event. Background subagents can emit two; the first one's totals can disagree with its own breakdown.
- `modelUsage` (per model: `inputTokens`, `outputTokens`, `cacheReadInputTokens`, `cacheCreationInputTokens`, `costUSD`) is the authoritative total and **includes subagents and helper calls**. `result.usage` covers only the main agent's last turn.
- Per-step `assistant` events repeat per content block: deduplicate by `message.id`. Their `output_tokens` is a placeholder; read output from `modelUsage`.
- `parent_tool_use_id` is null for the main agent and the spawning call's id inside a subagent: group by it for subagent share.
- The 5-minute vs 1-hour cache-write split is in each step's `usage.cache_creation`; subscriptions write the main conversation at 1 hour (2×), API keys at 5 minutes (1.25×).
- `total_cost_usd` comes from the CLI's bundled price table. In 2.1.208 it still priced Sonnet 5 at $3/$15 after the price stayed $2/$10: the subagent fixture's Sonnet line shows it. Always recompute.
- The cache prefix includes the working directory and git state, so the first run of a batch writes cache and later ones read it. Compare `processed_input`, which doesn't depend on that.

OpenTelemetry (`CLAUDE_CODE_ENABLE_TELEMETRY=1`) gives exact per-request events (`claude_code.api_request` with token classes, `query_source` main/subagent) and `claude_code.tool_result` sizes, if you need per-request precision ([monitoring docs](https://code.claude.com/docs/en/monitoring-usage)).

## Other agents

| Agent | Usage source | Watch out for |
| --- | --- | --- |
| Codex (`--agent codex`) | `codex exec --json` → `turn.completed.usage{input_tokens, cached_input_tokens, output_tokens}` | Cached tokens are **inside** `input_tokens`; failed turns report no usage; the stream doesn't name the model, so pass `--model` |
| Gemini CLI | `stats.models.<m>.tokens{prompt, candidates, cached, thoughts}` | `cached` is inside `prompt` |
| Cursor CLI | `result.usage{inputTokens, outputTokens, cacheReadTokens, cacheWriteTokens}` | Seen in the wild, not in official docs |
| opencode | `step_finish.part.tokens{input, output, reasoning, cache{read, write}}` | Per step: sum them |
| Aider | `Tokens: X sent, Y received. Cost: …` | Text, needs a regex |

Only the Claude and Codex adapters are built in; for others, convert to the trial JSON shape (see any trial file) and `report` works unchanged.

## Statistics

Same task, same code: runs typically differ ~2.5× and up to 30× ([Bai et al., arXiv 2604.22750](https://arxiv.org/abs/2604.22750); [Sonar, arXiv 2605.20049](https://arxiv.org/abs/2605.20049)). Temperature can't be set in Claude Code. So `report` gives:

- median and interquartile range per variant for every metric;
- the ratio of medians against the baseline with a bootstrap 95 % interval (2,000 resamples, fixed seed);
- pass rate, and cost per passing change;
- with `--refactor-cost-usd`, saving per change, break-even changes and payback months.

An interval that includes 1.0 means "no demonstrated saving". Then either measure more runs, try another representative change, or stop.

## Metering the refactoring itself

The anchor's biggest gap. Options, best first:

1. Run the refactoring steps headless through the same harness pattern (`claude -p … --output-format stream-json`) and parse each stream with `measure.py parse`.
2. For interactive sessions, read Claude Code's session transcripts with [ccusage](https://github.com/ryoppippi/ccusage) (`ccusage session --json`) and sum the sessions that did refactoring work.
3. Record human review time per refactoring commit; it often dominates ([economics.md](economics.md#worked-example)).

## Static estimates

Before spending on runs, a free floor: count the tokens of the files the change needs to read, before and after. Anthropic's `POST /v1/messages/count_tokens` counts in real Claude tokens and is free but needs an API key; `hotspots.py`'s bytes ÷ 4 is a rough proxy. A static count misses re-reads, search, failed attempts and the fixed prefix, so it underestimates both cost and saving. Use it to decide whether measuring is worth it, never to claim a saving.
