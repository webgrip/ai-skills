# Evaluate an MCP server

Contents: the layers · tools_lint rules · protocol checks · handler tests · agent eval set · the improvement loop · real-client tests

## The layers

| Layer | Catches | Runs |
|---|---|---|
| `scripts/tools_lint.py` | missing annotations, undescribed params, name rules, oversized surface | every commit |
| Inspector `--strict` + conformance suite | wire-level spec violations, schema portability, auth flow | CI |
| Handler tests + schema snapshots | wrong results, silent schema or annotation drift | CI |
| Agent eval set | wrong tool choice, wasted calls, unhelpful outputs and errors | before a release, after description changes |
| Real clients | auth quirks, tool caps, rendering | before a release |

## tools_lint rules

```bash
python3 scripts/tools_lint.py tools.json
python3 scripts/tools_lint.py path/to/toolsnaps/ --json --fail-on error
```

Input: a `tools/list` result (`{"tools": [...]}`), a JSON-RPC response, a bare array, or a directory of one-tool `*.json`/`*.snap` files. Get the live list with the Inspector CLI (below, `--format json`). Exit 0 clean, 1 findings at or above `--fail-on` (default `warn`), 2 unreadable input. Stdlib only, no network.

| Rule | Severity | Fires when |
|---|---|---|
| `no-tools` | error | the input holds no tools |
| `name-invalid` | error | name outside 1–128 chars of `[A-Za-z0-9_.-]` |
| `name-duplicate` | error | two tools share a name |
| `name-over-64` | warn | name longer than the Claude directory's 64 |
| `description-missing` | error | no description |
| `description-thin` | note | under 40 characters |
| `description-instructs-model` | warn | "ignore previous", "before using any other tool", "instead of the other tools", `<IMPORTANT>`, "system prompt", "do not tell the user" |
| `title-missing` | warn | no `title` or `annotations.title` |
| `readonly-hint-missing` | warn | `readOnlyHint` not an explicit boolean |
| `destructive-hint-missing` | warn | not read-only and `destructiveHint` not an explicit boolean |
| `hint-contradiction` | error | read-only and destructive both true |
| `openworld-hint-missing` | note | `openWorldHint` not an explicit boolean |
| `read-name-not-read-only` | note | name reads like `get`/`list`/`search`/`read` but `readOnlyHint` is not true |
| `input-schema-missing` | error | no `inputSchema` of type object |
| `schema-open` | note | top-level `additionalProperties` not false |
| `required-unknown` | error | `required` names a property that does not exist |
| `param-undescribed` | warn | a top-level property without description |
| `param-opaque-object` | note | a free-form object parameter |
| `page-size-unbounded` | note | `limit`/`per_page`/`page_size`-style number without `maximum` |
| `sensitive-header-mirror` | error | `x-mcp-header` on a token, secret, password, key, email or similar parameter |
| `read-write-mixed` | warn | one enum offers both GET-style and POST/PUT/PATCH/DELETE-style values |
| `output-schema-missing` | note | no `outputSchema` |
| `tool-count` | note over 15, warn over 25 | surface size |
| `surface-tokens` | warn | definitions exceed ~10,000 tokens (chars / 4, icons excluded) |

A false-positive pass against GitHub's 134 published tool snapshots raised only real findings: write tools without `destructiveHint`, duplicate names from feature-flag variants in one snapshot directory, and the size of the full surface.

## Protocol checks

```bash
npx @modelcontextprotocol/inspector --cli https://mcp.example.org/mcp --method tools/list --strict --format json > tools.json
npx @modelcontextprotocol/conformance server --url http://localhost:3000/mcp --requirements 2026-07-28 --expected-failures conformance-baseline.yml
```

- Inspector (web, CLI and TUI in one package, Node ≥ 22.19) handles both protocol eras; `--strict` exits 6 on tool-schema portability errors, 3 when auth is needed, 4 when unreachable. Docs: [Inspector CLI](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/cli).
- Conformance suite: `--requirements 2026-07-28` runs exactly what that revision requires, including auth and back-compat scenarios; keep known gaps in an expected-failures baseline so new regressions fail CI. Repo: [modelcontextprotocol/conformance](https://github.com/modelcontextprotocol/conformance).
- Run both against a 2025-11-25 client path too if the SDK exposes it, so the back-compat route stays alive.

## Handler tests and snapshots

- Table-driven handler tests with the upstream mocked (HTTP mocking library or a fake client).
- Snapshot the full tool output for representative calls and review diffs against the output rules in [design.md](design.md).
- Snapshot each tool's definition (name, description, schemas, annotations); CI fails on unreviewed change.
- Assert annotations explicitly per tool.
- Cover invalid, unauthorized and out-of-scope inputs; each must produce a teaching error.

## Agent eval set

Two kinds of cases, kept in the repo next to the server:

1. **Task cases** (≥ 10, aim for 20–40): realistic, multi-hop (several calls, paging, joining results), independent of each other, read-only, answerable with one string a script can compare, stable over time (closed or historical data), not answerable by a keyword search. The author explores with small `limit` calls without reading server code, then solves each task to confirm the answer.
2. **Selection cases**: direct prompts ("search tickets about login timeouts"), indirect prompts ("what's blocking the release?"), and **negative** prompts that must not call the server or must pick a sibling tool. Score precision and recall of tool choice; weight precision on negatives.

Hold out a third of both kinds; tune only on the rest.

Run each case in an agent loop with only this server connected, at least three times per case and per target model. Record: answer correctness, tools chosen, number of calls, total tokens, tool errors, duration. Ask the agent for short feedback on names, parameters, descriptions, errors and response size alongside its answer.

Anthropic's `mcp-builder` skill ships a reusable harness and question format; its script defaults to an old model, so pass the current model explicitly. Third-party options (MCPJam, Braintrust, DeepEval) add cross-client and repeated-trial reporting. Public benchmarks (MCP-Atlas, MCP-Universe, MCPMark, MCP-Bench) measure models more than your server.

## The improvement loop

1. Read failing transcripts first; what the agent never tried is often the finding.
2. Form one hypothesis (a description is ambiguous, an error does not name the next step, output buries the ID).
3. Change one field: a description, a parameter name, an error text, a default.
4. Re-run the training split; keep the change only if it helps without hurting negatives.
5. Confirm on the held-out split before release.
6. A coding agent can propose the refactor from pasted transcripts; the held-out split is the check on it.

## Real-client tests

- Add the server in each target client ([clients.md](clients.md)): sign in, call a public tool, a protected tool, a tool needing step-up; let the token expire and confirm refresh.
- Check tool caps and truncation in each client with the full surface enabled alongside the user's other servers.
- For the Claude directory, walk the review criteria list before submitting.
