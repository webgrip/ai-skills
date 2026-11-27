# mcp-apps-ui

Build interactive MCP Apps, tool results that render as cards, forms, dashboards and approval screens inside Claude, ChatGPT, VS Code, Cursor, Goose, Open WebUI and other hosts, on the official MCP Apps extension (`io.modelcontextprotocol/ui`). Covers when an app is the right answer, display modes, the server contract (`ui://` resources, `_meta.ui`, `content` versus `structuredContent`, app-only tools, CSP), the view (single-file bundle, host theming with fallback tokens, i18n, sizing, WCAG 2.2 AA), confirmed writes for operator surfaces, a dated host capability matrix and a dated ecosystem radar. The server underneath is the `mcp-server` skill's job.

Ships:

- `template/`: Preact + TypeScript + Vite single-file view, a shared JSON Schema contract with fixtures, a fake host on `AppBridge` with full and minimal profiles, Playwright + axe tests, and the same server in TypeScript (official SDK), FastMCP and stdlib Python. `npm ci && npx playwright install chromium && npm run build && npm test`.
- `hosts.md`: per-host capabilities with sources and dates.
- `ecosystem.md`: Adopt / Trial / Watch / Avoid for SDKs, frameworks and test tools, with release, maintainer and adopter evidence and a hype filter.

**Install:**

```text
/plugin install mcp-apps-ui@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s mcp-apps-ui`.

**Try:** "add an interactive status card to my MCP tool", "show a form in Claude from my MCP server", "my ui:// resource renders blank in ChatGPT", "build an approval screen for our runbook actions over MCP", "which MCP Apps framework should we use?", "make our MCP App work in Open WebUI too".
