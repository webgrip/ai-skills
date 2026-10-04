# Refactorings: which ones shrink what an agent must read

The goal is not smaller files. It is that the next change can be made after reading the smallest set of code that matters, found by a grep or a file name on the first try. "Randomly cutting the file into smaller files is unlikely to help as much" (Edwards-Alexander), and the controlled study measured why: extraction that spreads one concern over more files raised files read 11 % and saved nothing ([arXiv 2605.20049](https://arxiv.org/abs/2605.20049)).

Contents: the order · the catalog · the cohesion rule · anti-patterns · the plan format · lock it in

## The order

Work through the target in this order; re-measure at milestones and stop when the curve flattens.

| Step | Why first | Typical catalog moves |
| --- | --- | --- |
| 1. Characterisation tests | Nothing else is safe without them | ([execution.md](execution.md#safety-nets)) |
| 2. Remove dead code | Tokens read for nothing, near-zero risk when nothing reaches the code | Remove Dead Code |
| 3. Remove duplication | Duplicates get updated in one place and missed in others; helpers also cut output tokens per change | Replace Inline Code with Function Call, Extract Function, Parameterize Function |
| 4. Names an agent can grep | Agents localise by grep and names; identifiers carry intent | Change Function Declaration (rename), Rename Variable, Rename Field |
| 5. Separate concerns into classes | Splits transport, mapping and domain logic that share one file | Extract Class, Combine Functions into Class, Split Phase |
| 6. Move into cohesive, domain-named modules | The measured lever: a change touches one small file plus its exemplar | Move Function, Move Field, contracts (traits, interfaces) in their own files |
| 7. Co-locate tests | The feedback sits next to the code; one place to look | Move tests beside the code under test |
| 8. Split what is still large | Only along the seams the earlier steps exposed | More Move Function |

The anchor followed roughly this order (extract helpers, a client class and a builder first; then move queries, traits, codecs, the fake store and per-domain store files), and its largest drop came at the per-domain split, after the seams existed.

## The catalog

Names and sections from Fowler, *Refactoring*, 2nd edition; each has a page at [refactoring.com/catalog](https://refactoring.com/catalog/). Name the refactoring in every plan step and commit: naming the type and narrowing the region raised GPT-4's correct refactorings from 52 % to 87 % ([Liu et al., arXiv 2411.04444](https://arxiv.org/abs/2411.04444)).

| Refactoring | § | Agent-reading effect |
| --- | --- | --- |
| [Extract Function](https://refactoring.com/catalog/extractFunction.html) | 6.1 | Names a chunk; precondition for moving it. Inside one hotspot alone it is token-neutral |
| [Inline Function](https://refactoring.com/catalog/inlineFunction.html) | 6.2 | Undoes over-extraction: fewer hops to follow |
| [Change Function Declaration](https://refactoring.com/catalog/changeFunctionDeclaration.html) | 6.5 | Grep-able names guide retrieval |
| [Combine Functions into Class](https://refactoring.com/catalog/combineFunctionsIntoClass.html) | 6.9 | Behaviour grouped around its data: one file to read |
| [Split Phase](https://refactoring.com/catalog/splitPhase.html) | 6.11 | Parse and compute apart: the agent reads one phase |
| [Encapsulate Record](https://refactoring.com/catalog/encapsulateRecord.html) | 7.1 | Stable data structures that changes can rely on |
| [Extract Class](https://refactoring.com/catalog/extractClass.html) | 7.5 | Separates concerns sharing a file (anchor steps 1 and 6) |
| [Hide Delegate](https://refactoring.com/catalog/hideDelegate.html) / [Remove Middle Man](https://refactoring.com/catalog/removeMiddleMan.html) | 7.7 / 7.8 | Tune indirection depth both ways |
| [Move Function](https://refactoring.com/catalog/moveFunction.html) | 8.1 | The big lever (anchor steps 7–15); also the most merge-conflict-prone |
| [Move Field](https://refactoring.com/catalog/moveField.html) | 8.2 | Data next to the behaviour that uses it |
| [Move Statements into Function](https://refactoring.com/catalog/moveStatementsIntoFunction.html) | 8.3 | Removes repeated boilerplate at call sites |
| [Replace Inline Code with Function Call](https://refactoring.com/catalog/replaceInlineCodeWithFunctionCall.html) | 8.5 | Fewer places to read and to write (anchor step 5) |
| [Remove Dead Code](https://refactoring.com/catalog/removeDeadCode.html) | 8.9 | Pure reduction |
| [Parameterize Function](https://refactoring.com/catalog/parameterizeFunction.html) | — | Collapses near-duplicates |

"Split file" is not a catalog entry; it is a sequence of Move Function steps. Kent Beck's tidyings (*Tidy First?*: guard clauses, dead code, cohesion order, extract helper and others) are the small-scale versions; skip "explaining comments" where the repository bans comments in code.

## The cohesion rule

Every new file or module gets a one-line reason in the plan: **what changes together here, and which future change will read only this file**. Name files for the responsibility, in the domain's words (`store/watch_lists.rs`, not `store/part3.rs` or `helpers2.ts`). A split without a reason is not done.

Watch the measured signature of fragmentation: **files read rising while tokens don't fall**. If it appears, merge back (Inline Function, Inline Class) rather than splitting further. Granularity has an optimum: every extra file is a tool call and a turn, and every turn re-sends the fixed prefix.

## Anti-patterns

| Anti-pattern | Why it fails | Instead |
| --- | --- | --- |
| Split by line count | Spreads one concern; more files read, no saving | Split by what changes together |
| Script or regex splitting of multi-line code | Indentation and scope errors; the anchor's sed scripts failed | Semantic or AST tools ([execution.md](execution.md#tools)) |
| Letting the agent pick refactorings unaided | Agents default to renames and annotation edits | Plan with a human or a stronger model in a fresh context |
| Indirection for its own sake (registries, factories, deep inheritance) | Scatters one behaviour; untested hypothesis that it hurts, but no evidence it helps | Direct calls until a real variation point exists |
| A long AGENTS.md overview instead of structure | Overviews didn't help and raised cost in one study; contested | A short index of non-obvious entry points; fix the code |
| Optimising one benchmark change | Other changes may get worse | One to three representative changes; guard metrics |
| Refactoring inside a behaviour change | Tangled refactorings hurt compilability ([arXiv 2605.22526](https://arxiv.org/abs/2605.22526)) | Structure and behaviour in separate commits |

## The plan format

One row per step. The value column makes sure the most valuable step (the anchor missed it on the first pass) gets done and measured.

```text
| # | Refactoring (catalog name) | Target (file:symbol)        | Cohesion reason                    | Tool              | Verify                         | Expected value          | Status |
| 1 | Extract Class              | store.rs:FirestoreStore    | HTTP transport changes apart      | Edit + cargo check| cargo test -p data             | enables 6–8             | done   |
| 7 | Move Function              | store.rs → store/watch.rs  | watch lists change together       | Edit + cargo check| cargo test -p data store::watch| high: next 3 features   | todo   |
```

Keep a ledger of every move and rename (old path → new path) beside the plan; explicit state tracking improved agents' multi-file refactoring 44 % in RefactorBench ([arXiv 2503.07832](https://arxiv.org/abs/2503.07832)).

## Lock it in

Agents erode structure as they extend code, and quality prompts don't slow the decline ([SlopCodeBench, arXiv 2603.24755](https://arxiv.org/abs/2603.24755)). A refactoring without enforcement decays.

- **Mechanical checks in CI and agent hooks:** a file-size or function-length budget for the refactored area, dependency or layer rules (import-linter, ArchUnit, deptrac, dependency-cruiser, cargo-deny style), duplicate detection (jscpd, PMD CPD).
- **A short map, not an encyclopedia:** a few lines in AGENTS.md or CLAUDE.md pointing to non-obvious entry points (where watch lists live, which file is the exemplar for a new store). Claude Code's own guidance: keep it short and leave out what the agent can learn by reading code ([best practices](https://code.claude.com/docs/en/best-practices)).
- **A recurring cleanup cadence:** OpenAI's harness team moved from a weekly human clean-up day to recurring agents opening small refactoring PRs against drift ([harness engineering](https://openai.com/index/harness-engineering/)).
- **Trend metrics:** files touched per change and tokens per change, the refactoring triggers Böckeler recommends after finding TDD's refactor step ineffective in agent loops ([TDD inside the agent loop](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)). Re-run the representative changes every few months; a rising curve says it is time again.
