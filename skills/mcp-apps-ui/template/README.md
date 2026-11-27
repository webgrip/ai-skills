# MCP App template

A host-neutral MCP App: one model-visible read tool that renders a status card, two app-only tools for a confirmed write, a single-file Preact view, a fake host to test it in, and the same contract served by a TypeScript, a FastMCP and a stdlib Python server.

```bash
npm ci
npx playwright install chromium
npm run build
npm test
```

`npm test` runs the contract, the TypeScript server, the stdlib Python server (needs `python3`) and the view in the fake host under a full-featured and a minimal profile, in light and dark, in two locales, with axe and screenshots.

## Layout

| Path | What it is |
|---|---|
| `contract/service-status.schema.json` | The tool result contract, source of truth for every server and the view |
| `contract/fixtures/`, `contract/invalid/` | Shared fixtures; servers and view are tested against the same files |
| `src/contract.ts` | Types, tool names, the resource URI and tolerant readers the view uses |
| `src/app/` | The view: `bridge.ts` (handshake, theme, capability detection), `tokens.css` (fallback tokens), `i18n.ts`, `main.tsx` |
| `harness/host.ts` | Fake host on `AppBridge`: profiles `full` and `minimal`, fake app-only tools, a call log on `window.hostLog` |
| `server/ts/` | Official SDK server (`registerAppTool`, `registerAppResource`) and its stdio entry |
| `server/python/stdlib_server.py` | Dependency-free stdio server speaking the same contract |
| `server/python/fastmcp_server.py` | FastMCP 4 server reusing the stdlib domain logic |
| `tests/` | Playwright specs; node-only specs for contract and servers, browser specs for the view |

## Make it yours

1. Rename the contract, the `ui://` URI (keep a version segment) and the tool names in `src/contract.ts` and both Python files.
2. Replace the inventory and `mayRestart` with your data source and your authorization check; keep the check on the server.
3. Run the servers: `npm run serve:stdio`, `python3 server/python/stdlib_server.py`, or `uv run --with fastmcp==4.2.6 server/python/fastmcp_server.py`.
4. Preview the view: `npm run build && npm run harness`, then open `/harness.html?profile=minimal&theme=dark&locale=de-DE`. Query keys: `profile` (`full`, `minimal`), `theme`, `locale`, `fixture` (`healthy`, `degraded`), `result` (`structured`, `text-only`, `malformed`, `none`), `width`.
5. Screenshot baselines are written on the first run and ignored by `.gitignore`. Generate them on your CI's operating system, commit them, and drop the `tests/*-snapshots/` line.
