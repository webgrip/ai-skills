# mcp-server

Design, build, secure, deploy and evaluate Model Context Protocol servers on the stateless
2026-07-28 spec while still serving 2025-11-25 clients: an interview that turns agent stories
into tools, remote-by-default deployment, the tool pattern by surface size, the contract for
names, descriptions, schemas, outputs, errors and annotations, a lethal-trifecta threat model,
OAuth resource-server auth done by the book (Protected Resource Metadata, audience checks, no
token passthrough, CIMD, pre-registered clients or a consenting proxy when the IdP lacks CIMD
and DCR), the per-client facts for Claude Code, claude.ai, VS Code and Cursor, and an
evaluation stack from a static linter to held-out agent evals.

Ships:

- `scripts/tools_lint.py` — stdlib check of a `tools/list` result or a directory of tool
  snapshots: missing or contradictory annotations, undescribed parameters, name rules,
  instructions hidden in descriptions, secrets mirrored into headers, oversized surfaces.
- `case-webgrip.md` — the Webgrip estate's Authentik, Envoy Gateway, LiteLLM and Go SDK facts.

**Install:**

```text
/plugin install mcp-server@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s mcp-server`.

**Try:** "build an MCP server for our ticket API", "should this MCP server be local or
remote?", "the agent keeps picking the wrong tool", "add OAuth to our MCP server with our
IdP", "Claude never shows the Connect button", "lint our tools/list", "write an eval set for
this MCP server".
