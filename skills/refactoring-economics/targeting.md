# Targeting: where a refactoring will be repaid

A refactoring saves tokens only on future changes that touch the refactored code. So the target is chosen from change history, not from what looks ugliest.

Contents: hotspots · reading the ranking · coupling · confirming the read set · choosing representative changes · the target card

## Hotspots

Change frequency is steeply skewed: a few percent of files often take 10–25 % of all changes, sometimes over half ([CodeScene docs](https://codescene.io/docs/guides/technical/hotspots.html); [Tornhill, Tech Lead Journal 2025](https://techleadjournal.dev/episodes/241/)). Do not quote "2–4 % of code, 25–70 % of activity" as one statistic; no single source says it. The exact shape varies by repository ([Ortiz & Merelo-Guervós](https://arxiv.org/abs/1905.11044)), so measure yours.

```bash
python3 scripts/hotspots.py --since "12 months ago" --agent-pattern "Co-Authored-By: Claude" --coupling REPO
python3 scripts/hotspots.py --path src/data --exclude "*.json" --json REPO
```

| Column | Meaning |
| --- | --- |
| Commits | Non-merge commits touching the file in the window; release-bot commits (`chore(release)`, `[skip ci]`) are left out by default |
| Commit share | Commits ÷ all commits in the window: the head of the power law |
| Agent share | Share of those commits whose message matches `--agent-pattern`: the changes a refactoring for agents serves |
| Churn | Lines added plus deleted |
| Est. tokens | Bytes ÷ 4: a ranking proxy, never a bill (Claude 4.7+ tokenizers produce ~30 % more) |
| Exposure | Commits × estimated tokens: what agents would read if each change opened the whole file once |

This follows Tornhill's hotspot idea, change frequency × complexity ([Your Code as a Crime Scene](https://pragprog.com/titles/atcrime2/your-code-as-a-crime-scene-second-edition/)), with size in tokens standing in for complexity because tokens are what the agent pays to read.

## Reading the ranking

- **Exposure is an upper bound.** Agents don't read data catalogs, lockfiles, fixtures or generated code whole. Exclude them (`--exclude "*.json"`, the defaults already drop lockfiles, minified, vendored and build output) or they top the list.
- **High commits, small file:** probably fine; check coupling instead.
- **Large file, few commits:** cold. Leave it alone unless the roadmap says it is about to get hot.
- **Large file, many commits, high agent share:** the candidate.
- **Cross-check the roadmap.** Code about to be deleted or replaced is out, however hot. Code about to get a burst of planned features is in, even if it was quiet.
- **Rename history is not followed.** A file renamed in the window counts from its rename.

## Coupling

Files that change together form the hidden read set of a change: an agent asked to touch one will open the other.

`--coupling` lists pairs with code-maat's degree: shared commits ÷ the pair's mean commits. Files under `--min-revs` (5) commits, pairs under `--min-shared` (5) and commits touching more than 30 files are ignored. High coupling between files in different modules is a design signal: the boundary is in the wrong place, and moving behaviour so that things that change together live together is often the highest-value refactoring.

## Confirming the read set

The ranking guesses what agents read; the measurement shows it. After a baseline run, look at what the agent opened (`files_read`, `tool_calls` and `tool_result_bytes` in each trial JSON from `measure.py`). The refactoring target is where reads concentrate and repeat. Sonar found file **revisits** fell 34 % on cleaner code even where tokens moved little, so revisits are a cheap, telling metric ([arXiv 2605.20049](https://arxiv.org/abs/2605.20049)).

## Choosing representative changes

The anchor used one invented change. Use one to three real ones:

1. Pick recent commits to the target area that were representative of ongoing work (not the big refactor, not a one-line typo). `git log --format='%h %s' -- <path> | head -30`.
2. For each, write a **fully specified prompt** describing the change as it was requested, not as it was implemented. Underspecified prompts raise token use about 30 % and add variance ([arXiv 2608.25399](https://arxiv.org/abs/2608.25399)).
3. Write an **acceptance check** the harness can run: the commit's own tests, a test you add, or a compile plus targeted test command. A run that doesn't pass doesn't count as a saving.
4. Keep the prompt and check unchanged for the whole experiment. Store them next to the plan.

Prefer changes that cross the module boundary you intend to fix: the controlled study found savings concentrate in multi-module tasks, while extraction inside one hotspot was token-neutral.

## The target card

Write this before planning any refactoring:

```text
Target: src/data/store.rs (17,155 lines, ~170k est. tokens)
Evidence: 46 commits in 12 months (9 % of all), agent share 92 %, couples with src/api/items.rs (degree 0.71)
Roadmap: watch lists and sharing land next quarter, both in this file
Representative changes: (1) add ItemWatchStore (from a1b2c3d), (2) add a field to Item (e4f5a6b)
Acceptance: cargo test -p data store:: && cargo check
Not now: src/legacy/importer.rs (cold, being replaced in Q1)
```
