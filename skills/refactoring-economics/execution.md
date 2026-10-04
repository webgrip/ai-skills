# Execution: getting an agent to refactor without breaking things

Agents execute a well-specified refactoring well and choose refactorings badly. So selection stays with a human or a stronger planning model, and execution is one named, tool-driven, tested step at a time.

Contents: what the evidence says · selection · tools · safety nets · the per-step gate · commits and merges · cost of the steps

## What the evidence says

| Study | Finding | Strength |
| --- | --- | --- |
| [Liu et al. 2024](https://arxiv.org/abs/2411.04444) | Naming the refactoring type and narrowing scope: 52 % → 87 % correct; 7.4 % of solutions unsafe; re-applying through an IDE engine avoided every buggy one | Moderate |
| [CodeTaste 2026](https://arxiv.org/abs/2603.04177) | With a detailed spec, up to 76 % pass; given only a focus area, the best agent matched the human's choice 7.9 % of the time, 15.1 % with a plan first; "destructive search-and-replace" a named failure | Moderate |
| [SWE-Refactor 2026](https://arxiv.org/abs/2602.03712) | Single-step refactorings 82.6 % vs compound 39.4 % | Moderate |
| [RefactorBench 2025](https://arxiv.org/abs/2503.07832) | Agents 22 % vs a human with five minutes 87 %; explicit edit history +44 % relative | Moderate |
| [SWE-Bench ProMax 2026](https://arxiv.org/abs/2608.09802) | Best 41 %; the main failure is stopping before every call site, config and fixture is updated | Moderate |
| [CodeScene 2024](https://codescene.com/hubfs/whitepapers/Refactoring-vs-Refuctoring-Advancing-the-state-of-AI-automated-code-improvements.pdf) | Raw LLMs ≤ 37 % correct; ~98 % with a fact-checking layer | Vendor |
| [JetBrains 2026](https://blog.jetbrains.com/dotnet/2026/08/19/rider-refactoring-code-skill/) | Agents driving the IDE's refactoring engine: −83 % time, −64 % cost per solved task | Vendor, clean design |
| [Agent PR mining](https://arxiv.org/abs/2511.04824) | Unguided agents mostly rename and edit annotations | Strong |

## Selection

- **Plan in a fresh context with the whole target visible**, ideally a stronger model than the executor. The anchor found the chat interface (whole file in view) planned better than the coding agent; Anthropic's migration work uses its strongest models to plan and review and Sonnet to execute ([migration post](https://claude.com/blog/ai-code-migration), [kit](https://github.com/anthropics/code-migration-kit-with-claude-code)).
- **A human approves the plan and each high-value step.** The anchor's strongest qualitative finding: Claude could not tell which refactorings were suitable.
- **Break compound refactorings into atomic ones**: single steps succeed at about twice the rate.
- **Use a deterministic quality signal** to steer selection where available (complexity, duplication, CodeScene or SonarQube): guided agents do far more structural extraction and fewer cosmetic renames.

## Tools

Prefer, in this order, and never edit multi-line code with sed, awk or regex scripts:

1. **A semantic engine** (type-aware rename, move, extract):
   - Go: `gopls rename -w`, `gopls codeaction -exec -kind refactor.extract.function`.
   - TypeScript: ts-morph `rename()`, `sourceFile.move()` (updates imports).
   - Python: Rope (rename, extract, move).
   - PHP: Phpactor CLI `class:move`, `references:class --replace`, `references:member --replace`.
   - Java and Kotlin: OpenRewrite recipes; IntelliJ engines via the JetBrains MCP server or Serena's JetBrains backend.
   - C#: Rider's refactoring skill.
2. **A type-aware or AST rewrite**:
   - Rust: `rust-analyzer ssr 'pattern ==>> replacement'`.
   - PHP: Rector with rector-laravel (`withComposerBased(laravel: true)`).
   - Python: LibCST codemods.
   - JavaScript and TypeScript: jscodeshift `--dry`.
3. **A syntax-aware rewrite** for many-site shape changes: [ast-grep](https://ast-grep.github.io/guide/rewrite-code.html) (keeps indentation) or [Comby](https://comby.dev/docs/basic-usage) (whitespace-insensitive). Dry-run and count matches first.
4. **The agent's own content-anchored Edit tool**, moving one whole item at a time.

No tool moves a Rust module in one step. There, Move Function is: create the module file and declaration, move one item with the Edit tool, let `cargo check` list every broken path, fix them (rust-analyzer ssr for many callers), commit, repeat. The compiler is the completeness oracle.

Claude Code's LSP plugins push diagnostics after every edit and offer find-references, but they have no rename or code actions ([code intelligence](https://code.claude.com/docs/en/plugins/code-intelligence)). Use find-references for the completeness check, and an MCP server ([Serena](https://github.com/oraios/serena), [mcp-language-server](https://github.com/isaacphi/mcp-language-server)) or a CLI engine for the rename itself.

## Safety nets

- **Characterisation tests first**, in their own commit, proven green on the old code: capture what the code does, not what it should do (Feathers). Snapshot tools: `insta` (Rust), ApprovalTests, Jest snapshots, syrupy, Pest snapshots.
- **Check the net catches changes**, once, on the target region before the session:
  - Rust: `cargo mutants --in-diff`.
  - PHP: `pest --mutate` and Infection `--git-diff-lines`.
  - JavaScript and TypeScript: `stryker run --incremental --mutate file:lines`.
  - Python: mutmut.
- **Compiler or type checker after every step**: `cargo check`, `tsc --noEmit`, `phpstan`/Larastan, `pyright`, `go build ./... && go vet`. Print only new errors; full lint dumps flood the agent's context.
- **No tests and no way to add them** means no refactoring. Spotify's background agents could not verify migrations in repositories without build-time tests ([Honk](https://engineering.atspotify.com/2026/4/background-coding-agents-dataset-migrations-honk-part-4)).
- **Refactoring engines have bugs too**; tests still run after tool-driven changes.

## The per-step gate

Each step passes all of these before it is committed:

1. The named refactoring and nothing else changed.
2. Compile or type check is clean.
3. The targeted tests pass, and the full suite passes at milestones.
4. **Completeness:** find-references, the compiler, or `git grep` for the old name returns zero stale hits.
5. **Diff shape:** a move shows as moved, not rewritten. Check with `git diff --color-moved=zebra --color-moved-ws=allow-indentation-change`. A large non-moved delta in a Move Function commit is a rewrite: redo it.
6. Tests were not edited in the same commit as production code, except renames the tool made.
7. The ledger of moves and renames is updated.

A Stop hook or a pre-commit hook can enforce 2–4 mechanically.

## Commits and merges

- **Structure and behaviour never share a commit** (Beck, *Tidy First?*). Message: `refactor(scope): Move Function watch_item to store/watch.rs`. In repositories with release trains, check that the commit type triggers the intended release.
- **One catalog refactoring per commit** keeps `git bisect` and review cheap; list mass mechanical commits in `.git-blame-ignore-revs`.
- **Merge risk:** Move Class, Move Method and Move Attribute raise the likelihood of merge effort by over 400 %, renames by over 200 % ([arXiv 2608.15384](https://arxiv.org/html/2608.15384)). Announce a move window, land the moves as one quick batch on a short-lived branch, rebase other branches and agent worktrees straight after, and never refactor a hotspot while parallel work is editing it.
- **Rewrite is not refactor.** If the system is broken for more than minutes, it isn't refactoring ([Fowler](https://martinfowler.com/bliki/RefactoringMalapropism.html)). Throw the step away and take a smaller one.

## Cost of the steps

Small steps are a safety practice, not a token-saving one. Böckeler measured TDD-style micro-step loops at 3–8× the tokens with no quality gain ([TDD inside the agent loop](https://martinfowler.com/articles/exploring-gen-ai/tdd-in-the-agent-loop.html)). For agents, "small" means one named refactoring per commit with a cheap check, and a codemod across 200 call sites counts as one step. Meter the steps ([measurement.md](measurement.md#metering-the-refactoring-itself)); this is the number the anchor experiment never recorded.
