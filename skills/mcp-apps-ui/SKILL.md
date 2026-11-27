---
name: mcp-apps-ui
description: Builds interactive MCP Apps, tool results that render as UI (cards, forms, dashboards, approval screens) inside Claude, ChatGPT, VS Code, Cursor, Goose, Open WebUI and other hosts, on the official MCP Apps extension - app vs text vs elicitation vs link, display modes, ui:// resources with the mcp-app MIME type and _meta.ui.resourceUri, content vs structuredContent, app-only tools, CSP, host theming, sizing, accessibility, confirmed writes, a host capability matrix, a dated ecosystem radar and a tested Preact single-file template with a fake host. Use when building or reviewing an MCP App, MCP Apps, mcp-ui or Apps SDK widget; rendering a card, chart, form or dashboard in the chat; showing a form in Claude or a widget in ChatGPT; a ui:// resource renders blank, unstyled, clipped or blocked by CSP; adding approvals, runbook actions or an operator console over MCP; or choosing an MCP Apps framework, SDK or host.
---

# MCP Apps — interactive UI from MCP tools, built for the weakest host

The server underneath (tool design, auth, transport, evals) belongs to the **mcp-server** skill. This skill owns what the host renders: the `ui://` resource, the view, and the actions it takes.

## 1. Decide before building

| The user needs | Build |
|---|---|
| An answer, a number, a short list | Plain tool result. No app |
| One missing value or a yes/no mid-call | Elicitation (form mode for non-sensitive input, URL mode for credentials or payment) |
| A full product page, long document, external flow | A link (`ui/open-link` or a URL in the text) |
| To see structured data and act on it in place: filter, compare, approve, retry, pick | **MCP App** |
| An approval or runbook step a human must own | MCP App with a server-checked two-step write ([actions.md](actions.md)) |

Freeform text, follow-ups and "redo" stay in the chat, never in the app.

**Display mode:** `inline` by default (auto-height card, at most 2 actions, 4-5 data points, no nested scroll, no menus). `fullscreen` only for dashboards, editors and maps that need their own scroll; Claude's side panel reports `fullscreen`, so lay out by container size. `pip` exists on few hosts; never depend on it. Declare modes in `appCapabilities.availableDisplayModes` and request only one listed in `hostContext.availableDisplayModes`.

## 2. Start from the template

Copy [template/](template/README.md): Preact + TypeScript + Vite + `vite-plugin-singlefile`, a shared JSON Schema contract with fixtures, a fake host with `full` and `minimal` profiles, Playwright + axe tests, and the same server in TypeScript (official SDK), FastMCP and stdlib Python. `npm ci && npx playwright install chromium && npm run build && npm test` must stay green. Vanilla-TS fallback: the official `examples/basic-server-vanillajs` in `modelcontextprotocol/ext-apps`.

## 3. Server contract

- Register a tool with `_meta.ui.resourceUri` and a resource at that `ui://` URI served as `text/html;profile=mcp-app`. TypeScript: `registerAppTool` / `registerAppResource` from `@modelcontextprotocol/ext-apps/server`. Python: `@mcp.tool(app=AppConfig(...))` in FastMCP, or `mcp.server.apps` in the official SDK.
- **Version the URI** (`ui://service-status/v1/card.html`); hosts cache by URI, so a breaking view change gets a new one.
- **`content` is the complete answer** for the model and for hosts without Apps. A tool must be useful with the UI stripped.
- **`structuredContent` is the view's data**: a versioned contract, declared as `outputSchema`, `additionalProperties: false`. Treat it as model-visible: the spec says hosts keep it out of model context, ChatGPT feeds it to the model. View-only data that the model must not reason over goes in result `_meta`.
- **No secrets, credentials or internal-only ids in any result field or in the HTML.** All of it lands in the transcript, and the resource is readable by any client. The one token a result may carry is a short-lived, single-use confirmation bound to the caller, in `_meta`.
- **Actions are app-only tools** (`_meta.ui.visibility: ["app"]`). Visibility hides a tool from the model; it is not authorization. Every call is checked on the server for the calling principal.
- **CSP:** bundle everything inline and declare nothing. Need a network origin? Declare the narrowest `connectDomains` / `resourceDomains` / `frameDomains` with scheme, on the `resources/read` content item.
- **Capability check per request:** read `extensions["io.modelcontextprotocol/ui"].mimeTypes` from the client capabilities (on the 2026-07-28 protocol they arrive in each request's `_meta`) and make the text answer say what the user cannot do in a text-only client.
- **`_meta.ui.domain`** is optional: set it only when the view needs a stable origin (OAuth callback, CORS or API-key allowlist). The format is per host; Claude's is the first 32 hex chars of SHA-256(server URL) + `.claudemcpcontent.com`, so choose the value per connecting client. Without it the host uses its default sandbox origin.

Field-by-field detail, message list, style variables, Python and stdlib wiring → [build.md](build.md).

## 4. View rules

- **One HTML file.** No CDN scripts, fonts or images; icons as inline SVG.
- Register `ontoolinput`, `ontoolresult`, `ontoolcancelled`, `onhostcontextchanged` **before** `app.connect()`. Skeleton on input, render on result.
- **Read `structuredContent` with a tolerant reader**; unknown version or shape renders a pointer to the text answer, never a blank frame.
- **Theming:** a fallback token layer on `:root` defining every spec variable you use with `light-dark()`, then `applyDocumentTheme`, `applyHostStyleVariables`, `applyHostFonts`; host values win. Structure in host tokens, brand only as an accent. Test both themes with and without host variables.
- **Language** from `hostContext.locale`, times with `Intl` in `hostContext.timeZone`; set `document.documentElement.lang`.
- **Size:** keep `autoResize` on, transparent background, no `100vh`, no inner vertical scroll inline, container queries from 320 px; pad with `safeAreaInsets`.
- **Accessibility:** WCAG 2.2 AA, targets ≥ 44 px, visible `:focus-visible`, focus moved into a confirmation and back after cancel, `role="status"` for outcomes, `prefers-reduced-motion` honoured.
- **Feature-detect** from `app.getHostCapabilities()`: no `serverTools` → hide buttons and say "ask in the chat"; call `updateModelContext`, `sendMessage`, `openLink`, `downloadFile` only when offered.
- **State:** the view restarts from HTML; keep anything that matters on the server. `localStorage` keyed by a server-issued `viewUUID` only for cosmetic state, inside try/catch.

## 5. Writes and operator surfaces

Prepare → confirm with a short-lived, principal-bound, single-use token; idempotency key per confirmation; server-side authorization on every call; optimistic "requested" state reconciled with the receipt; audit log with principal and operation id; few app tools, because some hosts ask the user to approve each one. Full pattern, approval queues and runbook actions → [actions.md](actions.md).

## 6. Many hosts, one server

Design for the weakest host, enhance per capability. The weakest common host today renders inline only, sends no style variables, gives an opaque origin without storage and confirms every app tool call; terminal clients such as Claude Code show only `content`. Per-host facts with dates and sources → [hosts.md](hosts.md). Which SDKs, frameworks and test tools to bet on → [ecosystem.md](ecosystem.md).

## 7. Verify

1. Template tests: contract fixtures against schema, each server against the contract, the view in the fake host per profile × theme × locale with axe and screenshots.
2. `npx @modelcontextprotocol/inspector --cli --transport http --server-url https://host/mcp --method tools/list --app-info` in CI: one JSON line per tool with `hasApp`, CSP, permissions and domain, read without invoking the tool.
3. A real host per target, connected as a custom connector, plus one text-only client.
4. Walk [done.md](done.md) before calling it finished.

## Gotchas

- **Blank frame:** wrong MIME, a deprecated flat `_meta["ui/resourceUri"]` only, handlers set after `connect()`, or the host does not render Apps. Check `--app-info` first.
- **Opaque origin:** in a `srcdoc` iframe without `allow-same-origin`, `localStorage` throws and cookies do not exist. Never require them.
- **CSP blocks `fetch`** with only a console error, and Claude drops CSP entries it cannot parse (always write the scheme). Prefer `callServerTool` over fetching from the view.
- **`_meta` is not meant for the model**, and only some hosts let the view push context; tell the model what happened through `updateModelContext` when offered, otherwise through the next tool result.
- **Confirmation fatigue:** one approval card per app tool on some hosts; fold related actions into one tool with an action enum.
- **Height jitter:** async fonts, images without dimensions and skeletons taller than the result cause repeated `size-changed`. Reserve space.
- **Dark mode contrast:** fallback tokens must pass AA on their own; partial host palettes mix host and fallback colours.
- **Version skew:** hosts embed different `ext-apps` versions; the wire protocol is stable across 1.x and 2.x, but new methods are missing on older hosts. Feature-detect, never assume.
- **ChatGPT-only extensions** (`window.openai.widgetState`, `requestCheckout`, `uploadFile`) are lock-in; keep them behind detection and off the core path.

## Additional resources

- Field and message reference, theming variables, server wiring per language → [build.md](build.md)
- Two-step writes, approvals, runbook actions, audit → [actions.md](actions.md)
- Host capability matrix with dates and sources → [hosts.md](hosts.md)
- Ecosystem radar (Adopt / Trial / Watch / Avoid) and hype filter → [ecosystem.md](ecosystem.md)
- Definition of done → [done.md](done.md)
- Ready-to-copy app, harness, servers and tests → [template/README.md](template/README.md)
