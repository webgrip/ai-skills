# adr-writer reference

Contents: [Section anatomy](#section-anatomy) · [Status lifecycle](#status-lifecycle--date-semantics) ·
[Format generations & migration](#format-generations--migration) · [Registry spec](#registry-index-spec) ·
[Validator](#validator) · [CI wiring](#ci-wiring) · [Companion standards](#companion-standards) ·
[Bootstrap decisions](#bootstrap-decisions)

## Section anatomy

MADR 4.0.0, in order. "Required" = what the bundled validator enforces (stricter than upstream,
where most elements are optional — a decision log is only defensible if every record argues).

| Section | Required | Carries |
| --- | --- | --- |
| frontmatter `status`/`date` | yes | Lifecycle state + last-updated date (never creation date). |
| frontmatter `decision-makers`/`consulted`/`informed` | teams | RACI-lite. Drop in solo repos. |
| `# H1` | yes | Bare title = problem + solution ("Use PostgreSQL for relational data"). No `ADR-NNNN:` prefix — the number lives in the filename and registry. |
| `## Context and Problem Statement` | yes | 2–3 sentences or a story; scope made explicit (components/paths). |
| `## Decision Drivers` | no | Forces, constraints, quality attributes. |
| `## Considered Options` | yes | Titles only; the chosen option listed first. |
| `## Decision Outcome` | yes | Opens `Chosen option: "…", because …`, then load-bearing specifics (exact component/config/paths). |
| `### Consequences` | no | `* Good, because …` / `* Bad, because …` bullets. |
| `### Confirmation` | no* | The concrete check proving the decision is implemented. *Include whenever checkable — see [fitness functions](#companion-standards). |
| `## Pros and Cons of the Options` | no | 1–3 `Good/Neutral/Bad, because` bullets per option; omit when no real alternative was weighed. |
| `## More Information` | yes | `Technical story:` (parent RFC/issue), dated history oldest-first, cross-ADR relations (Supersedes / Refined by / Supported by). |

## Status lifecycle & date semantics

```
proposed ──ratified──▶ accepted ──replaced──▶ superseded by ADR-NNNN
    │                      │
    └──declined──▶ rejected └──no longer relevant──▶ deprecated
```

- Every transition = three writes: frontmatter `status:` + `date:`, a dated More Information
  bullet citing the commit/evidence, and the registry row. The validator fails on any drift.
- `date` = last update of the decision (MADR semantics). A format-only touch (e.g. migration)
  is not a decision update — log the bullet, keep the date.
- `rejected` records are kept forever: they prevent re-deriving a dead end.
- A reversal is never an edit — write a new ADR that supersedes; the old record's body stays
  as decided, its history gains a dated bullet pointing forward.

## Format generations & migration

| Generation | Recognize by | Validator treatment |
| --- | --- | --- |
| MADR 4.0.0 (2024) | YAML frontmatter `status:` | Full checks; history section = `## More Information`. |
| MADR 2.x/3.x | `* Status:` / `* Date:` bullets | Full checks; history section = `## Links`. |
| Nygard (2011) | `## Status` heading | Status legality + registry parity only; sections skipped, skip reported. |

Records keep their **birth format** — amendments append in the record's own shape. If a repo
deliberately migrates (e.g. to make an exemplar), the mapping 2.x → 4.0.0 is mechanical:

- `* Status:` / `* Date:` bullets → frontmatter; `Deciders` → `decision-makers`.
- `Technical Story:` line → `* Technical story:` bullet in More Information.
- `### Positive/Negative Consequences` → `### Consequences` with `Good/Bad, because` bullets.
- `## Links` → `## More Information` (bullets unchanged).
- Content stays verbatim; add a dated bullet `restructured to MADR 4.0.0 (format-only)`.

## Registry (index) spec

`index.md` (or `README.md`) in the ADR directory carries the reader-visible state — static-site
generators hide frontmatter, so without the registry a published superseded ADR looks current.

- Row shape: `| [NNNN](adr-NNNN-file.md) | Decision | status | YYYY-MM-DD |`. Extra middle
  columns are fine — the validator reads the link from the first cell, the date from the last,
  the status from the cell before it.
- Keep the Records table the **last element** of the file so a new record is one appended line.
- Group rows into themed sections if the corpus grows — the validator only cares about rows.

## Validator

`scripts/validate_adr_consistency.py` — stdlib-only; copy it into the adopting repo (CI needs a
committed file; the plugin copy is the distribution source, the repo copy is canonical there).

```
python3 scripts/validate_adr_consistency.py .            # auto-discovers the ADR dir
python3 scripts/validate_adr_consistency.py . --adr-dir docs/adr
```

Enforces: one filename style per corpus, unique never-reused numbers, status+date in exactly
one format generation per file, legal status values, superseded-by targets exist, single
bare-title H1, required sections, `Chosen option:` line, and file ↔ registry parity on status
(primary word) + date. Reports (without failing): Nygard skips, missing registry. Exit codes:
0 clean, 1 violations, 2 no ADR directory.

## CI wiring

GitHub Actions / Forgejo Actions step (any job with python3):

```yaml
- name: Validate ADR consistency
  run: python3 scripts/validate_adr_consistency.py "$GITHUB_WORKSPACE"
```

Optional pre-commit (lefthook): run the same command when `docs/adr/**` is staged. Pair with a
docs link-checker if the repo has one — the validator checks structure and parity, not link
targets outside the registry.

## Companion standards

- **Architecture fitness functions** (Ford/Parsons, *Building Evolutionary Architectures*) —
  the Confirmation section names a check; the mature move is promoting it to an automated gate
  (admission policy, alert, CI test, ArchUnit-style rule). An ADR whose Confirmation runs in CI
  cannot silently rot. The bundled validator is this idea applied to the decision log itself.
- **Y-statements** (Zimmermann et al., Sustainable Architectural Decisions) — one-sentence
  form: "In the context of ⟨use case⟩, facing ⟨concern⟩, we decided ⟨option⟩ to achieve
  ⟨quality⟩, accepting ⟨downside⟩." Useful as a compact `Decision Outcome` phrasing; MADR's
  `Chosen option: …, because …` covers the same ground.
- **Nygard ADRs** (2011) — the ancestor format; MADR subsumes it. Tolerate in legacy corpora.
- **ISO/IEC/IEEE 42010** — formal architecture-description vocabulary (stakeholders, concerns,
  rationale); MADR's team frontmatter fields are its RACI-lite echo. Relevant only when a
  client/compliance context demands the formal standard.
- **RFC / design doc split** — exploration happens in an RFC; each resulting choice lands as
  one ADR linking back via `Technical story:`. Operational procedure goes to a runbook, not
  an ADR.

## Bootstrap decisions

- Default home: `docs/adr/`. Respect an existing docs tree (`doc/adr/` for adr-tools shops,
  `docs/decisions/` for log4brains-style setups) — the validator discovers all of them.
- If the repo publishes docs (mkdocs.yml, Docusaurus, Backstage TechDocs): register `index.md`
  and the records in the nav, and remember the frontmatter-invisibility rule — the registry
  and dated history are what readers see.
- Number width is fixed at four digits (`0001`); at 10,000 decisions you have a different
  problem.
