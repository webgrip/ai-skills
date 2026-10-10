# adr-writer

A Claude skill for **Architecture Decision Records done properly** — writing, amending, and
superseding ADRs in [MADR 4.0.0](https://adr.github.io/madr/) (the current de-facto ADR
standard), in any repo, with the conventions that keep a decision log trustworthy over years:

- **Locate or bootstrap** — finds an existing ADR corpus (`docs/adr/`, `doc/adr/`,
  `docs/decisions/`, …) and follows its conventions, or bootstraps one from bundled templates:
  an annotated MADR 4.0.0 record template plus a registry index with status legend.
- **Append-only history** — ADRs are records, not living docs. Ratifications, reverts, and
  supersessions land as dated history bullets and status transitions; the decided body is
  never rewritten. Reversals get a *new* superseding ADR.
- **Confirmation as a fitness function** — every checkable decision names the concrete
  command/dashboard/policy/test that proves it is implemented, not a proxy.
- **A bundled, CI-ready validator** — `validate_adr_consistency.py` (stdlib-only Python)
  enforces numbering discipline, legal statuses, required sections, and file ↔ registry
  parity on status + date. It understands three format generations (MADR 4.0 frontmatter,
  MADR 2.x bullets, legacy Nygard) so it drops into existing corpora without a rewrite.
- **Static-site awareness** — MkDocs/TechDocs/Docusaurus hide frontmatter, so the skill keeps
  status visible where readers actually look: the registry row and the dated history.

## Install

**`npx skills` (recommended — works in every agent, not just Claude):**

```bash
npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s adr-writer -g
```

**Claude Code plugin:**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/ai-skills.git
/plugin install adr-writer@ai-skills
```

**Claude Code (manual):** copy `skills/adr-writer/` into your project's
`.claude/skills/` (shared with your team via git) or `~/.claude/skills/` (just you).

**Claude app / claude.ai:** grab `adr-writer.skill` from the
[latest release](https://forgejo.webgrip.dev/webgrip/ai-skills/releases/latest),
upload it via Settings → Skills (or attach it in a chat), and hit *Save skill*.

The validator needs only `python3` (any recent version, stdlib only).

## Use

Open Claude in a project and say, for example:

- *"record the decision to move to PostgreSQL as an ADR"*
- *"we don't have ADRs yet — set them up"*
- *"we reverted the Kafka migration — update the ADR"*
- *"this decision replaces ADR-0007, supersede it"*
- *"we agreed on ADR-0012 in today's review — accept it"*
- *"wire ADR validation into our CI"*

## Why

A decision log is only useful if it can be trusted: statuses that match reality, history that
explains every transition, and records nobody quietly rewrote. Most ADR tooling stops at a
template; this skill encodes the full lifecycle — MADR 4.0.0 structure, status/date semantics,
supersession mechanics, registry parity — and ships the validator that keeps all of it true
in CI, so the log stays defensible long after the decisions were made.

## Contents

```
skills/adr-writer/
  SKILL.md                              # the procedure Claude follows
  reference.md                          # section semantics, lifecycle, migration, CI wiring
  assets/adr-template.md                # annotated MADR 4.0.0 record template
  assets/index-template.md              # registry index starter (status legend + Records table)
  scripts/validate_adr_consistency.py   # stdlib-only consistency validator (copy into repos)
```
