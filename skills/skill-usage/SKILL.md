---
name: skill-usage
description: Report which agent skills actually get used, from the local usage log the bundled hook writes (~/.claude/skill-usage.jsonl; opencode twin at ~/.config/opencode/skill-usage.jsonl). Use when asked which skills are used or unused, for a skill usage report, to find dead or undertriggering skills, or to decide what to consolidate or remove from a skills estate.
---

# Skill usage — find the dead and the undertriggering

The plugin's PostToolUse hook appends one line per Skill invocation to
`~/.claude/skill-usage.jsonl` (`{ts, skill, cwd, session}` — local file, no
network). opencode users get the same via the estate's
`skill-usage-log.js` plugin, writing `~/.config/opencode/skill-usage.jsonl`.

## Produce a report

1. Read both JSONL files (either may be missing — say so; a missing/empty log
   right after install means "no data yet", not "no usage").
2. Aggregate: invocations per skill, per ISO week; distinct sessions and
   distinct repos (`cwd`) per skill.
3. List the installed estate (marketplace catalog, `~/.claude/skills`,
   project `.claude/skills`) and diff: **installed but never fired = dead
   candidate**; fired only via explicit `/name` and never auto-triggered =
   undertriggering candidate (the log can't distinguish these — flag, don't
   conclude).
4. Report: a count table, the dead list, the trend (this month vs last), and
   one recommendation per finding.

## Acting on findings

- **Dead skill** → propose consolidation into a neighbor or removal via the
  estate's deprecation process (CONTRIBUTING.md there) — never silently
  delete; usage logs miss colleagues' machines unless theirs are collected.
- **Undertriggering** → tune the `description` with the skillsmith skill and
  re-probe with the estate's `run_evals.py`.
- Cross-machine picture: each person's log is local; ask teammates to run the
  report and compare, or aggregate the files manually. There is deliberately
  no central collection.

## Gotchas

- The hook only sees sessions where the plugin is enabled — enable it
  everywhere before trusting a "dead" verdict.
- Claude Code's own OTel telemetry redacts skill names unless
  `OTEL_LOG_TOOL_DETAILS=1`; this log exists so nobody needs OTel infra.
