# MCP Apps host capability matrix

State on **2026-11-27**. Hosts change monthly: re-read the linked source before relying on a row, and update the date when you do. The baseline is the community-maintained [Extension Support Matrix](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/extensions/client-matrix.mdx) (last commit 2026-11-24).

- [Rule: design for the weakest host](#rule-design-for-the-weakest-host)
- [Matrix](#matrix)
- [Connecting a server per host](#connecting-a-server-per-host)
- [Matrix-only hosts](#matrix-only-hosts)

## Rule: design for the weakest host

| Assume | Because |
|---|---|
| Only `content` is shown | terminal and older clients render no Apps |
| Only `inline`, no mode switch | VS Code, Open WebUI |
| No `styles.variables`, only `theme` or nothing | Open WebUI; any host may send a subset |
| Opaque origin, no `localStorage`, no cookies | Open WebUI `srcdoc` sandbox |
| Every app `tools/call` needs a user click | Open WebUI always; Claude per tool unless "Always allow" |
| No `updateModelContext`, no `ui/message` sending | Open WebUI (no model context), VS Code (`ui/message` only fills the input), Microsoft 365 Copilot Cowork |
| Inline height capped and clipped | Claude, Open WebUI (10,000 px) |

Then enhance per capability the host reports in `hostContext` and `getHostCapabilities()`.

## Matrix

| Host | Apps | Display modes | Host style variables | Origin and storage | App tool calls | Notable | Source (read 2026-11-27) |
|---|---|---|---|---|---|---|---|
| **Claude** web and Desktop | yes | inline card or carousel, side panel (reports `fullscreen`), fullscreen; no `pip` | full set, Anthropic Sans | sandbox origin from `ui.domain` (SHA-256 of server URL + `.claudemcpcontent.com`) | user allows the app once or always | side panel, entry points, app tools and embedded sites are not in every organization and need a remote server; entry points and embedded sites need a Verified directory listing; `baseUriDomains` ignored; unparseable CSP entries dropped | [getting started](https://claude.com/docs/connectors/building/mcp-apps/getting-started), [design guidelines](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| **Claude** mobile | yes | inline, fullscreen with composer overlaid | full set | WKWebView or Android WebView; no camera, microphone or location on Android | as above | conversation owns vertical pan gestures; honour `safeAreaInsets`; skeletons, not spinners | [design guidelines](https://claude.com/docs/connectors/building/mcp-apps/design-guidelines.md) |
| **Claude Code** | not listed for MCP Apps | n/a | n/a | n/a | tools work as plain MCP tools | the user sees `content`; write it as the full answer | [matrix](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/extensions/client-matrix.mdx) |
| **ChatGPT** | yes, "fully compatible with the MCP Apps spec" since 2026-02-22 | inline card, inline carousel, fullscreen, picture-in-picture | `hostContext.styles.variables` since 2026-05-28 | own sandbox domain; `window.openai` extras: `widgetState`, `uploadFile`, `selectFiles`, `getFileDownloadUrl`, `requestModal`, `requestCheckout` | per ChatGPT policy | "treat the resource URI as a cache key": new URI on breaking view changes; the model receives `structuredContent`; iframe embeds get extra review | [MCP Apps in ChatGPT](https://developers.openai.com/apps-sdk/mcp-apps-in-chatgpt/), [changelog](https://developers.openai.com/plugins/changelog) |
| **VS Code** GitHub Copilot | yes, "Experimental" | `inline` only | not documented | sandboxed iframe with CSP | not documented | `ui/message` fills the chat input without sending; context updates appear as attachments; clipboard write yes; camera, microphone, geolocation no | [VS Code MCP guide](https://code.visualstudio.com/api/extension-guides/ai/mcp) (updated 2026-11-25) |
| **Cursor** | yes since 2.6 (2026-03-03) | not documented | not documented | sandboxed iframe | not documented | a forum report says rendering stopped in 3.10 and worked in 3.9; fix not confirmed | [changelog 2.6](https://cursor.com/changelog/2-6), [forum](https://forum.cursor.com/t/mcp-apps-stopped-rendering-in-3-10-20-worked-in-3-9-16/165167) |
| **Goose** | yes, "experimental and based on a draft specification" | inline; no persistent app windows | `theme` | not documented | not documented | "does not yet support advanced capabilities"; repo moved to `aaif-goose/goose` | [building-mcp-apps.md](https://github.com/aaif-goose/goose/blob/main/documentation/docs/tutorials/building-mcp-apps.md) |
| **Open WebUI** | yes since v0.13.0 (2026-11-03) | `inline` only; display mode requests answer `inline` | none; `theme` from its dark class | `srcdoc` iframe, `sandbox="allow-scripts allow-downloads allow-popups"`: opaque origin, no storage | **every** app `tools/call` waits for a user confirmation, 120 s timeout | embeds ext-apps 2.0.4; height capped at 10,000 px; capabilities `downloadFile` and `serverTools`, no `updateModelContext` | [MCPApp.svelte](https://github.com/open-webui/open-webui/blob/main/src/lib/components/chat/Messages/MCPApp.svelte), [v0.13.0](https://github.com/open-webui/open-webui/releases/tag/v0.13.0) |
| **LibreChat** | yes, enabled with `mcpSettings.apps` | not documented | not documented | sandbox page on a separate origin (`/api/mcp/sandbox`, `MCP_SANDBOX_FRAME_ANCESTORS`, blank frames when unset) | not documented | `maxActiveViews` 3, `maxPersistedAppBytes` 1 MiB, CSP at most 4096 chars and 32 sources per directive; version that introduced it not stated | [mcpAppSandbox](https://www.librechat.ai/docs/configuration/librechat_yaml/object_structure/mcp_app_sandbox) |
| **Microsoft 365 Copilot** Cowork | yes, documented subset | no `pip` | not checked | not checked | not checked | no `ui/update-model-context`, no partial tool input, results over 64 KiB not pushed to the view | [Cowork MCP Apps support](https://learn.microsoft.com/microsoft-365/copilot/cowork/mcp-apps-support) (updated 2026-11-03) |
| **MCP Inspector** | partial | n/a | n/a | n/a | n/a | `--cli … --app-info` probe for CI: JSON per tool, exit 0 when a tool has an App, 2 when not | [mcp-app-review.md](https://github.com/modelcontextprotocol/inspector/blob/main/docs/mcp-app-review.md) |
| **MCPJam** | yes (matrix) | emulated | emulated | emulated | n/a | inspector that emulates both MCP Apps and the ChatGPT Apps SDK | [repo](https://github.com/MCPJam/inspector) |

## Connecting a server per host

| Host | How | Note |
|---|---|---|
| claude.ai and Desktop | custom connector with the remote server URL; tunnel a local server first | auth per the mcp-server skill; the Desktop config file runs local stdio servers |
| ChatGPT | Plugins → add custom MCP server with the public HTTPS URL including `/mcp`; select **Refresh** after changing tools or UI resources, then start a new conversation | [connect](https://developers.openai.com/apps-sdk/deploy/connect-chatgpt) |
| VS Code, Cursor | `mcp.json` / settings entry | check the client's current docs for the Apps toggle |
| Open WebUI | admin tool server settings | expect confirmations on every app tool call |
| Claude Code | `claude mcp add` | text only: test that `content` stands alone |

## Matrix-only hosts

Postman, Archestra.AI, PostHog Code, Kiro Crew, Glean and mcp-use carry a check mark in the [matrix](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/extensions/client-matrix.mdx); their capabilities were not checked. fast-agent and mcpc carry none.
