# MCP Apps build reference

Facts read from the primary sources on 2026-11-27. Re-check the spec repo before relying on a draft-only field.

- [Spec and SDK status](#spec-and-sdk-status)
- [Tool metadata](#tool-metadata)
- [Resource metadata and CSP](#resource-metadata-and-csp)
- [Messages between view and host](#messages-between-view-and-host)
- [Host context and capabilities](#host-context-and-capabilities)
- [Style variables](#style-variables)
- [Server wiring per language](#server-wiring-per-language)
- [View state](#view-state)
- [Bundle](#bundle)

## Spec and SDK status

| Item | Value | Source |
|---|---|---|
| Extension id | `io.modelcontextprotocol/ui` (SEP-1865) | [draft spec](https://github.com/modelcontextprotocol/ext-apps/blob/main/specification/draft/apps.mdx) |
| Stable spec | `specification/2026-01-26/apps.mdx` | [ext-apps repo](https://github.com/modelcontextprotocol/ext-apps) |
| Draft additions since | app-provided tools, sampling, `ui/notifications/request-teardown`, relaxed iframe architecture (2026-11-04), WebMCP interoperability | [draft history](https://github.com/modelcontextprotocol/ext-apps/commits/main/specification/draft) |
| SDK | `@modelcontextprotocol/ext-apps` npm `latest` 2.0.4 (2026-10-27); 2.1.0 published the same day but not tagged `latest`, GitHub release 2026-11-10 | [npm](https://registry.npmjs.org/@modelcontextprotocol/ext-apps), [releases](https://github.com/modelcontextprotocol/ext-apps/releases) |
| 2.0.0 (2026-09-08) | moved to the split MCP TS SDK 2.x packages and zod 4; wire protocol unchanged, 2.x views run in 1.x hosts | [v2.0.0](https://github.com/modelcontextprotocol/ext-apps/releases/tag/v2.0.0) |
| 2.1.0 | `App.registerTool` mirrored to and from WebMCP `document.modelContext`, on by default, `webMcpBridge: false` turns it off | [v2.1.0](https://github.com/modelcontextprotocol/ext-apps/releases/tag/v2.1.0) |

SDK entry points: `@modelcontextprotocol/ext-apps` (view: `App`, `PostMessageTransport`, `applyDocumentTheme`, `applyHostStyleVariables`, `applyHostFonts`), `/react` (hooks), `/app-bridge` (host side: `AppBridge`), `/server` (`registerAppTool`, `registerAppResource`, `getUiCapability`, `RESOURCE_MIME_TYPE`). Peer dependencies: `@modelcontextprotocol/client`, `@modelcontextprotocol/core` `^2`, `zod` `^4.2`.

## Tool metadata

```json
{ "_meta": { "ui": { "resourceUri": "ui://service-status/v1/card.html", "visibility": ["model", "app"] } } }
```

- `resourceUri`: the `ui://` resource that renders this tool's results.
- `visibility`: default `["model", "app"]`. `["app"]` hides the tool from the model's tool list and leaves it callable from a view of the same server. Hosts MUST reject a view's `tools/call` on a tool without `"app"`.
- The flat `_meta["ui/resourceUri"]` is deprecated and "will be removed before GA". `registerAppTool` still writes both keys for older hosts; a hand-written server can do the same.

## Resource metadata and CSP

`resources/read` content item, which takes precedence over the `resources/list` entry:

```json
{
  "uri": "ui://service-status/v1/card.html",
  "mimeType": "text/html;profile=mcp-app",
  "text": "<!doctype html>…",
  "_meta": { "ui": { "csp": { "connectDomains": [], "resourceDomains": [] }, "prefersBorder": true } }
}
```

| Field | Effect |
|---|---|
| `csp.connectDomains` | `connect-src`: fetch, XHR, WebSocket |
| `csp.resourceDomains` | scripts, styles, images, fonts, media |
| `csp.frameDomains` | nested iframes; default `frame-src 'none'` |
| `csp.baseUriDomains` | `base-uri`; default `'self'`; Claude ignores it |
| `permissions` | `camera`, `microphone`, `geolocation`, `clipboardWrite`; hosts MAY honour them, so feature-detect |
| `domain` | fixed sandbox origin; format differs per host |
| `prefersBorder` | host draws border and background; Claude defaults to borderless on web, bordered on mobile |

Without `csp`, hosts MUST apply `default-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self' data:; object-src 'none'; connect-src 'none'`. Hosts may tighten, never loosen. Hence: inline everything, images as `data:` URIs.

## Messages between view and host

JSON-RPC over `postMessage`.

| Direction | Methods |
|---|---|
| View → host requests | `ui/initialize`, `ui/open-link`, `ui/message`, `ui/request-display-mode`, `ui/update-model-context`, `ui/download-file`, `tools/call`, `tools/list`, `resources/read`, `sampling/createMessage`, `ping` |
| View → host notifications | `ui/notifications/initialized`, `ui/notifications/size-changed`, `ui/notifications/request-teardown`, `notifications/message` |
| Host → view notifications | `ui/notifications/tool-input`, `tool-input-partial`, `tool-result`, `tool-cancelled`, `host-context-changed` |
| Host → view requests | `ui/resource-teardown`; `tools/call` and `tools/list` on tools the view registered |

The host sends nothing before `ui/notifications/initialized`. The SDK's `App` maps these to `ontoolinput`, `ontoolinputpartial`, `ontoolresult`, `ontoolcancelled`, `onhostcontextchanged`, `onteardown`, and methods `callServerTool`, `readServerResource`, `sendMessage`, `updateModelContext`, `openLink`, `downloadFile`, `requestDisplayMode`, `sendLog`, `getHostContext`, `getHostCapabilities`.

## Host context and capabilities

`hostContext`: `toolInfo`, `theme`, `styles.variables`, `styles.css.fonts`, `displayMode`, `availableDisplayModes`, `containerDimensions`, `locale` (BCP 47), `timeZone`, `userAgent`, `platform`, `deviceCapabilities`, `safeAreaInsets`. Any field may be missing.

`hostCapabilities`: `openLinks`, `downloadFile`, `serverTools`, `serverResources`, `logging`, `sandbox` (granted CSP and permissions), `updateModelContext`, `message`, `sampling`. Absent means unsupported.

## Style variables

Hosts may send any subset, usually as `light-dark()` values; views MUST define fallbacks for every variable they use. Families: `--color-background-*`, `--color-text-*`, `--color-border-*`, `--color-ring-*` (each with `primary`, `secondary`, `tertiary`, `inverse`, `ghost`, `info`, `danger`, `success`, `warning`, `disabled` where defined), `--font-sans`, `--font-mono`, `--font-weight-{normal,medium,semibold,bold}`, `--font-text-{xs,sm,md,lg}-{size,line-height}`, `--font-heading-{xs..3xl}-{size,line-height}`, `--border-radius-{xs,sm,md,lg,xl,full}`, `--border-width-regular`, `--shadow-{hairline,sm,md,lg}`. The full key list is `McpUiStyleVariableKey` in the SDK; the template's [tokens.css](template/src/app/tokens.css) is a fallback layer that passes AA in both themes.

## Server wiring per language

| Stack | Tool | Resource | UI capability check |
|---|---|---|---|
| TypeScript, official SDK | `registerAppTool(server, name, { _meta: { ui: { resourceUri } }, outputSchema }, cb)` | `registerAppResource(server, name, uri, { mimeType: RESOURCE_MIME_TYPE }, read)` | `getUiCapability(clientCapabilities)?.mimeTypes` |
| Python, official SDK 2.x | `@apps.tool(resource_uri=..., visibility=[...])` on `Apps()` | `apps.add_html_resource(uri, html, csp=..., prefers_border=...)`; `MCPServer(..., extensions=[apps])` | `client_supports_apps(ctx)` |
| Python, FastMCP 4 | `@mcp.tool(app=AppConfig(resource_uri=..., visibility=[...]))` returning `ToolResult(content=..., structured_content=..., meta=...)` | `@mcp.resource("ui://…", app=AppConfig(csp=ResourceCSP(...)))`, MIME set automatically | `ctx.client_supports_extension("io.modelcontextprotocol/ui")` |
| No dependencies | hand-written `_meta` | `mimeType` on the content item | read `capabilities.extensions` at `initialize`, or per request from `_meta["io.modelcontextprotocol/clientCapabilities"]` |

Template versions: [server.ts](template/server/ts/server.ts), [fastmcp_server.py](template/server/python/fastmcp_server.py), [stdlib_server.py](template/server/python/stdlib_server.py). `outputSchema` in TypeScript comes straight from the JSON Schema via `fromJsonSchema` from `@modelcontextprotocol/server`.

## View state

- The view reloads from the HTML whenever the host re-renders it. Durable state lives on the server, reached through app-only tools.
- Recoverable cosmetic state (page, zoom, selected tab): `localStorage` keyed by a `viewUUID` the server returns in `CallToolResult._meta.viewUUID`, wrapped in try/catch, because opaque-origin hosts have no storage ([patterns.md](https://github.com/modelcontextprotocol/ext-apps/blob/main/docs/patterns.md)).
- ChatGPT adds `window.openai.widgetState` / `setWidgetState`, scoped to one rendered instance; use it only behind feature detection.

## Bundle

- Vite + `vite-plugin-singlefile` produces one HTML with JS and CSS inline. The template's view is about 260 kB (70 kB gzip), mostly `ext-apps` and zod; `App` switches zod to jitless mode so no `unsafe-eval` is needed.
- Grep the built HTML for `src="http` and `href="http`; the template's browser tests also fail on any outbound request.
