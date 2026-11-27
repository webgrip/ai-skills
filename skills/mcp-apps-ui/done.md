# Definition of done for an MCP App

Every line is checkable. The template's tests cover the ones marked **(t)**.

## Decision

- [ ] A plain tool result, elicitation or a link was considered and rejected for a stated reason.
- [ ] Display mode chosen; inline cards hold at most 2 actions and 4-5 data points, with no nested scroll or menus.

## Server

- [ ] Tool `_meta.ui.resourceUri` points at a versioned `ui://` URI **(t)**.
- [ ] Resource served as `text/html;profile=mcp-app` **(t)**.
- [ ] `content` alone answers the question; read in a text-only client it says what the user cannot do there **(t)**.
- [ ] `structuredContent` matches a versioned JSON Schema with `additionalProperties: false`, published as `outputSchema` **(t)**.
- [ ] No secret, credential or internal-only id in `content`, `structuredContent`, `_meta` or the HTML; a confirmation token lives only in `_meta` **(t)**.
- [ ] Actions are app-only tools; the server authorizes every call for the calling principal **(t)**.
- [ ] Writes use prepare/confirm with a principal-bound, single-use, expiring token and an idempotency key **(t)**.
- [ ] Every accepted write is audited with principal, target and operation id.
- [ ] Annotations explicit on every tool; writes carry `destructiveHint: true` **(t)**.
- [ ] CSP empty, or each declared origin justified and scheme-qualified, on the `resources/read` content item.
- [ ] `ui.domain` set only if the view needs a stable origin, in each target host's format.
- [ ] Same contract verified for every server implementation **(t)**.

## View

- [ ] One self-contained HTML file; no request leaves the host during tests **(t)**.
- [ ] Handlers registered before `connect()`; skeleton on input, render on result.
- [ ] Malformed, unknown-version and text-only results render a pointer to the text answer **(t)**.
- [ ] Fallback tokens for every variable used; host variables override them **(t)**.
- [ ] Light and dark pass axe WCAG 2.2 AA with and without host variables **(t)**.
- [ ] Locale and time zone from host context; at least two locales tested **(t)**.
- [ ] Auto-height with no inner vertical overflow inline; no horizontal overflow at 320 px **(t)**.
- [ ] Targets at least 44 px, visible focus, focus moves into a confirmation and back on cancel **(t)**.
- [ ] Reduced motion stops animation **(t)**.
- [ ] Buttons hidden with an explanation when the host lacks `serverTools` or the caller lacks permission **(t)**.
- [ ] No reliance on `localStorage`, cookies or `window.openai`; any use sits behind try/catch or detection.

## Hosts

- [ ] `--app-info` probe green in CI for every UI tool.
- [ ] Rendered and exercised in every target host, plus one text-only client.
- [ ] Host rows in [hosts.md](hosts.md) re-read for each target and the date bumped where they changed.
- [ ] Screenshot baselines committed from the CI operating system.
