---
name: adr-writer
description: Write, amend, or supersede Architecture Decision Records in MADR 4.0.0 — locate or bootstrap the ADR directory and registry index, numbering, frontmatter status/date semantics, Confirmation checks, append-only dated history, supersession mechanics, and a bundled CI-ready consistency validator. Use when recording or ratifying an architecture/technology decision, creating an ADR, updating an ADR's status after a rollout/revert/supersession, adopting ADRs in a repo that has none, or wiring ADR validation into CI. NOT for design exploration (that's an RFC/design doc) or operational procedure (runbook).
---

# ADR writer — MADR 4.0.0, append-only decision log

One defensible decision per record — the durable answer to *"why is it built this way?"*.
Format = [MADR 4.0.0](https://adr.github.io/madr/) plus the conventions that keep a decision
log trustworthy: a registry index in lock-step with the files, append-only dated history, and
a Confirmation check per decision.

## Locate or bootstrap

Find the corpus first: look for `adr-NNNN-*.md` / `NNNN-*.md` in the usual homes —
`docs/adr/`, `doc/adr/`, `docs/decisions/`, `docs/architecture/decisions/`, or the repo's
docs tree.

- **Corpus exists** → its local conventions win (the `index.md`/`README.md` in that directory,
  the repo's CLAUDE.md, or a repo-local ADR skill). Keep the corpus's filename style; write NEW
  records in MADR 4.0.0 unless the repo declares a different format.
- **No corpus** → bootstrap:
  1. `mkdir -p docs/adr` (or match the repo's existing docs layout).
  2. Copy [assets/adr-template.md](assets/adr-template.md) → `docs/adr/adr-0000-template.md`
     and [assets/index-template.md](assets/index-template.md) → `docs/adr/index.md`.
  3. Copy [scripts/validate_adr_consistency.py](scripts/validate_adr_consistency.py) into the
     repo's scripts directory and add a CI step (snippets → [reference.md](reference.md)).
  4. If a static-site config exists (`mkdocs.yml`, Docusaurus sidebar), register the pages.

## New ADR

1. Number = next free (never reuse). Filename `adr-NNNN-<kebab-title>.md`; H1 = bare title
   stating problem + solution (no `ADR-NNNN:` prefix).
2. Copy the template. Frontmatter: `status:` lowercase — proposed | accepted | rejected |
   deprecated | superseded by ADR-NNNN (as a markdown link to the superseding record);
   `date:` = **last-updated** date (MADR semantics, not creation). Teams keep `decision-makers:`/`consulted:`/`informed:`; solo
   repos drop them.
3. Body: `## Considered Options` lists the chosen option first. `## Decision Outcome` opens
   `Chosen option: "…", because …`, then the load-bearing specifics (component, config, exact
   paths). `### Consequences` = `* Good/Bad, because …` bullets. `### Confirmation` = the
   concrete check that proves the decision is implemented — a command, dashboard, policy, or
   test by name, not a proxy. Why-nots → `## Pros and Cons of the Options`
   (`Good/Neutral/Bad, because` bullets per option; omit when no real alternative was weighed).
4. `## More Information`: parent RFC/issue first (`* Technical story: …`), then dated history
   bullets `* YYYY-MM-DD — <event> (<commit>)` oldest first, then cross-ADR relations
   (Supersedes / Refined by / Supported by).
5. Register a row in the index Records table (the table is the last thing in `index.md`, so
   appending a row keeps it valid), then run the validator.

## Amend / status change

Reality changed (revert, partial rollout, ratification)? Append a dated More Information
bullet citing the commit, update frontmatter `status:` + `date:`, mirror the index row.
**The body stays as decided** — never rewrite it to match new reality. A reversed decision
gets a *new* superseding ADR; the old one's status becomes superseded-by, linking forward.
Records keep their **birth format**: amend older MADR 2.x records (`* Status:` bullets,
`## Links`) or Nygard records in their own shape; don't retro-migrate the corpus
(deliberate migration → [reference.md](reference.md)).

## Validate

`python3 scripts/validate_adr_consistency.py .` (the repo's copy) — filename/number
discipline, status legality, required sections per format generation, and file ↔ index parity
on status + date. Run after every ADR touch; keep it in CI so drift can't land.

## Gotchas

- Static-site generators (MkDocs/TechDocs, Docusaurus, Hugo) do NOT render frontmatter — on
  the published page `status`/`date` are invisible. The index row + dated history ARE the
  reader-visible status; never skip those two mirrors.
- Frontmatter is YAML — quote `status:` whenever it contains a markdown link (`[`/`]`).
- Dates come from `git log --follow --oneline -- <file>` or the triggering commit — never
  from memory. No ratification commit exists? Log `status corrected in audit YYYY-MM-DD`;
  don't backdate acceptance.
- Numbers are never reused; files never renamed (inbound links break).

## Additional resources

- Section semantics, status lifecycle, format generations + migration, registry row spec,
  validator details, CI snippets, companion standards → [reference.md](reference.md)
