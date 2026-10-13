# Security and least privilege

Contents: threat model · server-side controls · input hardening · output hygiene · local servers · OWASP MCP Top 10 map · security tests

## Threat model in five questions

1. **Trifecta legs.** Does the server expose private data? Does it return content an outsider can write (tickets, emails, web pages, PR comments, logs)? Can it send data out (post, email, create a public resource, fetch an arbitrary URL)? Write the answer down per tool. A server with all three, or with two next to a common companion server that has the third, is an exfiltration path once any untrusted text reaches the model.
2. **Blast radius.** What is the worst single call? The worst sequence of calls an injected instruction could chain?
3. **Whose identity.** Does each call run as the human, as a shared service account, or as the server? Shared service accounts lose attribution and usually over-grant.
4. **What crosses the trust boundary.** Tool inputs come from a model that may have read attacker text; tool definitions from third-party servers can change under you.
5. **What gets logged.** Can you reconstruct who called what, with which arguments, under which scopes?

Remove a leg rather than filter it: a read-only default, a project-scoped token, no free-form URL fetch, a human approval on the send step. A prompt-injection filter that stops 95 % of attempts is a failing grade.

## Server-side controls

- Split read and write tools; offer a read-only mode (flag, header or `/readonly` path) that removes write tools from `tools/list`.
- Filter `tools/list` by the caller's authorization (the spec allows variation by authorization, not by connection) and check scopes again inside every handler.
- Progressive scopes: a minimal baseline in `scopes_supported`; 403 `insufficient_scope` naming every scope still needed when a call requires more; log each elevation with a correlation ID.
- Compute required scopes from the arguments where it matters (writing a CI workflow file needs more than writing a README).
- High-impact or irreversible writes (payments, deletes, outbound messages) get a server-enforced human gate: MRTR confirmation or an out-of-band approval URL with an expiring token.
- Rate limits per principal and per tool; size and time caps on every upstream call.
- Per-server, narrowly scoped upstream credentials from a secret store; nothing inherited from a shell.
- Content filters (hiding public content from untrusted authors) are best-effort hygiene, never an authorization boundary.

## Input hardening

- Validate every argument against the schema and business rules in the handler.
- Paths: resolve, then require the result to stay inside an allowed root (resolve + relative check); reject symlink escapes.
- Commands: argv arrays (`execFile`, `exec.Command`), never a shell string with interpolation.
- URLs: allowlist schemes and hosts, resolve and block private, link-local and metadata ranges (SSRF), cap redirects.
- SQL: parameterized queries; a read-only role for read tools; row limits.
- Sizes: cap request bodies, uploads, result sizes and recursion depth.

## Output hygiene

- Strip secrets, tokens, session cookies, internal hostnames and stack traces from results.
- Return only the PII the task needs.
- Third-party content is data: keep it in clearly delimited fields, never merge it into instructions or descriptions.
- Tool definitions are part of the attack surface: never build descriptions from upstream data, and treat a change in a published description as a release (clients may re-prompt).

## Local servers

- Prefer remote. Run locally only when the machine is the point.
- Distribute with provenance and pinned versions (MCPB bundle, signed release, lockfile).
- Isolate where possible: container, sandbox or VM; read-only filesystem mounts; an egress allowlist.
- stdio: nothing but JSON-RPC on stdout.
- Local HTTP: validate `Origin` (403 otherwise) against DNS rebinding, bind `127.0.0.1`, require a random token or use a unix socket. Otherwise any web page or process on the machine can drive it.
- A local server that can delete or send should ask for confirmation through the client, and read-only should be the default mode.

## OWASP MCP Top 10 map

| Risk | Where this skill handles it |
|---|---|
| MCP01 Token mismanagement and secret exposure | output hygiene; [auth.md](auth.md) no passthrough, header-only tokens |
| MCP02 Privilege escalation via scope creep | progressive scopes, read-only mode |
| MCP03 Tool poisoning | description rules in [design.md](design.md); `tools_lint.py` `description-instructs-model` |
| MCP04 Supply chain and dependency tampering | pinned SDK and bundles, provenance |
| MCP05 Command injection and execution | input hardening |
| MCP06 Prompt injection via contextual payloads | trifecta analysis, human gates |
| MCP07 Insufficient authentication and authorization | [auth.md](auth.md) |
| MCP08 Lack of audit and telemetry | [operate.md](operate.md) audit log |
| MCP09 Shadow MCP servers | inventory and allowlist of servers in the fleet |
| MCP10 Context injection and over-sharing | bounded, high-signal outputs |

## Security tests

- Injection payloads planted in upstream content (a ticket body telling the agent to email secrets); confirm the gate or missing leg stops the chain.
- Path traversal, shell metacharacters, private-range and metadata URLs.
- Calls without a token, with a token for another audience, with an expired token, with too few scopes.
- Tampered `requestState`, a replayed `requestState`, another user's handle.
- `tools/list` as a read-only caller contains no write tool.
