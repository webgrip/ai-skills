# Tool design detail

Contents: choosing tools · names · descriptions · input schemas · outputs · errors · annotations · state and handles · mid-call input (MRTR) · server instructions and skills · open disagreements

## Choosing tools

- Start from the agent stories, not the API reference. A story that takes four calls in a known order is one outcome tool (`get_customer_context`, `schedule_event`, `track_latest_order(email)`); keep known orchestration in code.
- Prefer `search_*` over `list_*`: a list that dumps everything wastes context and invites the model to filter by eye.
- One distinct purpose per tool, no overlap. If a human engineer cannot say which of two tools fits a request, the model cannot either.
- Generate from OpenAPI only to explore or bootstrap, then curate: rename cryptic arguments, hide parameters behind defaults, drop endpoints no story needs.
- Count across all servers the agent sees. Rough ceilings in practice: 5–15 per server is comfortable, ~25 is the point where mature servers switch patterns, clients with hard caps (Cursor, see [clients.md](clients.md)) fail beyond them.
- Large surfaces, in increasing order of machinery:
  1. **Consolidate** related tools behind a `method` enum (`issue_read` with `get|get_comments|get_labels`), keeping read and write tools separate.
  2. **Layered**: `*_search_api` → `*_api_details` → `*_api_read` (GET) / `*_api_write` (mutations), over an allowlist of operations.
  3. **Code mode**: `search()` over the spec plus `execute()` running code in an isolate with no filesystem, no env and egress off by default. Needs a real sandbox.
  4. **Toolsets**: named groups selectable by config, header or URL path, plus a read-only switch that removes every write tool. Operator settings are an upper bound request headers cannot raise.
- Leave tool discovery to the client where it exists (deferred loading, tool search); server-side "dynamic toolsets" that add tools mid-conversation have been tried and shelved by large servers.

## Names

- `service_verb_resource` (`tickets_search`, `tickets_create`) or `service_resource_verb`; the prefix-vs-suffix effect varies by model, so pick one and let the eval decide if in doubt.
- Characters `[A-Za-z0-9_.-]`, case-sensitive, unique per server, ≤ 64 chars for the Claude directory.
- Unambiguous parameter names: `user_id`, not `user`.
- Renaming a published tool breaks agent prompts and allowlists: keep the old name as a deprecated alias for a release window.

## Descriptions

Write for a capable new colleague who has never seen the system.

- First line: what it does and **when to use it** ("Use when you have a ticket id and need …").
- What it returns: the fields and their meaning; code consumers parse this.
- What it does **not** do, and the sibling for that ("To find an id from words, use tickets_search first").
- Prerequisites, formats, units, time zones; the current date when relative dates matter.
- For a freeform query tool, name and link the target query language or API docs.
- Domain terms made explicit; one term per concept across all tools.
- Never: instructions to call other tools first, to ignore or override other tools or the system prompt, hidden or encoded text, product promotion. Directory review rejects it and it is the tool-poisoning pattern.
- Small description edits move accuracy a lot; change one at a time and re-run the eval.
- Workflows spanning several tools belong in server instructions or a shipped skill, not in each description.

## Input schemas

- JSON Schema 2020-12. No-parameter tools: `{"type": "object", "additionalProperties": false}`.
- Flat top-level primitives; no opaque `options`/`config` objects; no tightly coupled parameter pairs.
- `enum` for closed sets, `minimum`/`maximum` and a `default` for counts, `pattern` for IDs, `format` for dates.
- A `description` on every property, with one realistic example when the format is not obvious.
- `x-mcp-header` mirrors a primitive parameter into an `Mcp-Param-*` header for gateways; only for routing keys, never secrets or PII.
- Validate again in the handler: the schema is advice to the client, the handler is the contract.

## Outputs

- Return what the next decision needs: names, titles, status, URLs, and the IDs a follow-up call takes. Drop internal plumbing IDs, null and empty placeholders, raw upstream JSON.
- Resolve opaque IDs to readable names where the model must reason about them; row objects beat positional arrays for weaker models.
- Pagination: `limit` (default 20–50, bounded), `cursor` or `offset`, and `has_more`, `next_cursor`, `total_count` in the result.
- Truncation: cap size, then say so and how to narrow ("Showing 10 of 847; filter by status or date").
- `response_format` enum (`concise` | `detailed`) when both summaries and IDs are needed; concise answers run at roughly a third of the tokens.
- Declare `outputSchema` and return `structuredContent` that conforms, plus the same data serialized into a text block for clients that ignore structured output.
- `resource_link` for large or optional payloads; embedded `resource` only when small and always needed.
- Mutations: short confirmation with the created or changed ID and URL, never a bare "ok".
- Respect client caps (Claude Code ~25k tokens by default, hosted Claude ~150k characters, ~240 s call timeout); see [clients.md](clients.md).
- Result format (Markdown vs JSON) measurably matters and is model-dependent; decide by eval.

## Errors

| Situation | Return |
|---|---|
| Unknown tool, malformed JSON-RPC, invalid params at the protocol level | JSON-RPC error |
| Bad argument values, not found, permission denied, upstream failure | result with `isError: true` and teaching text |
| Expired or unknown handle | `isError: true`: "Basket expired after 24 h idle; call create_basket again" |
| Internal bug | generic message to the model, full detail to your logs and error tracker |

Teaching text says what went wrong, the valid shape or value, and the next call. Avoid alarming wording that makes the agent abandon the tool. Never leak stack traces, SQL or internal hostnames.

## Annotations

| Hint | Default when unset | Set it to |
|---|---|---|
| `readOnlyHint` | false | true for every pure read |
| `destructiveHint` | **true** (only meaningful when not read-only) | false for additive writes (create, comment), true for delete/overwrite/send/pay |
| `idempotentHint` | false | true when repeating the call with the same arguments has no extra effect |
| `openWorldHint` | **true** | false for a bounded private system (your own database, one tenant's tickets) |
| `title` | none | human-readable label for approval UIs |

Annotations are untrusted hints to clients. They decide auto-approval and confirmation prompts in Claude, never authorization. Assert them in tests so a refactor cannot silently flip one.

## State and handles

- 2026-07-28 has no protocol session. Any instance must serve any request.
- Stateful workflows mint an explicit opaque handle in a creation tool and take it as a parameter afterwards.
- A handle is a name, not a capability: high entropy, bound to the authenticated principal (`sub`), re-authorized on every call.
- State the retention in the creating tool's description ("expires after 24 hours of inactivity").
- Durable state lives in application storage (database, Durable Object, Redis), never in process memory tied to a connection.

## Mid-call input (MRTR and elicitation)

- A tool that needs input returns `resultType: "input_required"` with `inputRequests` (for example `elicitation/create`) and an opaque `requestState`; the client retries with `inputResponses` under a new JSON-RPC id.
- Only send input-request types the client declared in its capabilities; always have a path for clients that cannot answer (an `isError` result asking for the missing parameter).
- Handle decline and cancel; never assume a retry arrives.
- `requestState` is attacker-controlled: integrity-protect it (HMAC or AEAD) when it influences authorization or business logic, add anti-replay fields, enforce one-time use server-side.
- Form mode: confirmations, choosing among ambiguous matches, a missing required parameter. Never secrets, credentials or PII.
- URL mode: third-party OAuth, payments, anything sensitive. No pre-authenticated URLs, no PII in the URL, bind the flow to the MCP token's `sub`. URL-mode elicitation is not a replacement for MCP authorization.
- High-impact writes can also use out-of-band approval: return a URL where a human approves, then accept the retry with an approval token that expires.

## Server instructions and skills

- Server instructions act like a system prompt for the server: tool order, conventions ("always paginate"), cross-tool workflows.
- Ship workflow knowledge as skills next to the server (a plugin bundling connector plus skills, or the Skills over MCP extension where clients support it).

## Open disagreements

- **Coverage vs curation**: resolved in practice as curated top tools plus a searchable long tail.
- **Thresholds**: 5–15, ~20 with a hard 25, "switch at 30"; client tool search softens counts in Claude but not in clients with hard caps.
- **Format**: Markdown, JSON or structured plus text; measure.
- **Naming scheme**: `service_verb_resource`, `domain.action`, or `resource_verb` grouping; be consistent and measure.
- **Confirmation**: client annotations vs server-side MRTR vs out-of-band approval; only server-side gates are enforceable.
