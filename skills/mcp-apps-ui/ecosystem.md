# MCP Apps ecosystem radar

**Classification dated 2026-11-27.** Signals come from the npm and PyPI registries and the GitHub API on that date, plus each project's own docs. Refresh it by re-running those queries (commands at the bottom) and re-reading the adopter sources; change a ring only on evidence, and update this date.

- [Radar](#radar)
- [Signals per project](#signals-per-project)
- [Breaking-change history](#breaking-change-history)
- [Named adopters](#named-adopters)
- [Hype filter](#hype-filter)
- [Refresh](#refresh)

## Radar

| Ring | Project | One-line reason |
|---|---|---|
| **Adopt** | MCP Apps spec 2026-01-26 + `@modelcontextprotocol/ext-apps` | the standard and its reference SDK; Claude, ChatGPT and Microsoft docs all point at it; wire-compatible across 1.x and 2.x. Pin an exact version: npm `latest` lags the newest release |
| **Adopt** | MCP Inspector `--app-info` | official, scriptable CI probe with a JSON and exit-code contract; its rendering is only partial |
| **Adopt** (as test reference, not a product) | ext-apps `examples/basic-host` and `AppBridge` | the shortest path to a fake host for tests; the repo says it is not a supported host |
| **Trial** | Python SDK `mcp.server.apps` | official, in the 2.x line since 2.0.0 (2026-07-28); no adopters seen yet |
| **Trial** | FastMCP 4 apps (custom HTML) | large, very active project; `AppConfig`, CSP, visibility and capability checks are thin, correct wrappers over the spec |
| **Trial** | MCPJam inspector | very active, listed in the official matrix, emulates MCP Apps and ChatGPT; 2 npm maintainers and a separately licensed evals part |
| **Trial** | ext-apps agent skills plugin (`create-mcp-app`, `add-app-to-server`, `migrate-oai-app`, `convert-web-app`) | official, linked from Claude's docs; complements this skill for scaffolding and migration |
| **Trial** (Node and React stacks only) | Skybridge | multi-host full-stack framework with an emulator and README adopters; vendor-led, two majors in 2026 |
| **Trial** (Node stacks only) | mcp-use | very active, also a host in the official matrix; vendor-led and extremely high release churn |
| **Trial** (Next.js only) | Vercel MCP Apps Next.js starter | spec-only template, no `window.openai`; a starting point, not a framework |
| **Watch** | xmcp | spec metadata support, active; no adopters found, 2 npm maintainers |
| **Watch** | FastMCP Prefab components (`prefab-ui`) | UI from Python is attractive, but 0.x with documented frequent breaking changes |
| **Watch** | mcp-ui (`@mcp-ui/client`, `@mcp-ui/server`) | still the most complete off-the-shelf host renderer (`AppRenderer`), but no release in 6 months, 1 npm maintainer, 7 majors |
| **Watch** | Vercel AI SDK host helpers (`MCPAppRenderer`, `splitMCPAppTools`) | a real option for building your own host; no dated maturity signal |
| **Watch** | C# `ModelContextProtocol.Extensions.Apps` | marked experimental by its own diagnostic (MCPEXP003) |
| **Watch** | Figma kits (Claude "MCP Apps for Claude", OpenAI component library) | useful design references, each branded for one host, undated |
| **Avoid** for host-neutral views | `@openai/apps-sdk-ui` | ChatGPT look, React plus Tailwind 4, no release since 2026-05-05 |
| **Avoid** as a base | `openai/openai-apps-sdk-examples` | demos lean on ChatGPT-only `widgetState` and `widgetSessionId`; last push 2026-04-15 |
| **Avoid** | `mcp-ui-server` (PyPI) | two releases ever, last 2025-11-04 |
| **Avoid** on the core path | `window.openai` extensions | ChatGPT-only; see the hype filter |
| **Not applicable** | Cloudflare Agents, Vercel `mcp-handler` | transport and agent frameworks without MCP Apps helpers; put ext-apps on top |

## Signals per project

Concentration = share of the last 100 default-branch commits by the top committer.

| Project | First release | Latest (date) | Releases last 90 days | Behind it, concentration | License | Host coverage | Source |
|---|---|---|---|---|---|---|---|
| `@modelcontextprotocol/ext-apps` | 0.0.1 2025-12-08; 1.0.0 2026-01-26 | 2.0.4 `latest` 2026-10-27; 2.1.0 GitHub 2026-11-10 | 6 | MCP project, 49 contributors, top committer 68%, 5 npm maintainers | MIT on npm | spec-neutral | [repo](https://github.com/modelcontextprotocol/ext-apps), [npm](https://registry.npmjs.org/@modelcontextprotocol/ext-apps) |
| MCP Inspector | 0.1.0 2024-11-19 | 2.16.0 2026-11-18 | 17 | MCP project, top committer 100% | see repo LICENSE | partial Apps host | [mcp-app-review.md](https://github.com/modelcontextprotocol/inspector/blob/main/docs/mcp-app-review.md) |
| Python SDK `mcp.server.apps` | in 2.0.0 (2026-07-28) | `mcp` 2.3.0 2026-10-02 | 3 | MCP project | MIT | spec-neutral server | [API docs](https://py.sdk.modelcontextprotocol.io/api/mcp/server/apps/), [source](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/server/apps.py) |
| FastMCP apps | apps since 3.0.0 (2026-02-18) | 4.2.6 2026-11-25 | 38 | PrefectHQ, 100+ contributors | Apache-2.0 | spec-neutral server, Python | [docs](https://github.com/PrefectHQ/fastmcp/blob/main/docs/apps/low-level.mdx), [PyPI](https://pypi.org/pypi/fastmcp/json) |
| `prefab-ui` | 0.x | 0.21.1 2026-10-26 | 2 | PrefectHQ | Apache-2.0 | via FastMCP | [PyPI](https://pypi.org/pypi/prefab-ui/json) |
| MCPJam inspector | 0.1.0 2025-05-23 | 3.25.3 2026-11-26 | 58 | MCPJam, 2 npm maintainers | Apache-2.0 except evals | emulates MCP Apps and ChatGPT | [repo](https://github.com/MCPJam/inspector) |
| Skybridge | 0.0.1 2025-10-07 | 2.1.2 2026-11-12 | 8 | Alpic, 42 contributors, top committer 58% | MIT in repo, ISC on npm | Claude, ChatGPT, VS Code, other spec hosts; Node | [repo](https://github.com/alpic-ai/skybridge) |
| mcp-use | 0.0.1 2025-04-20 | 2.12.10 2026-11-25 | 35 (911 versions ever) | vendor-led, 64 contributors | MIT | spec plus ChatGPT extras; Node; also a host | [repo](https://github.com/mcp-use/mcp-use) |
| xmcp | 0.0.1 2025-05-17 | 1.13.4 2026-11-26 | 26 | basement.studio, 2 npm maintainers | MIT | spec metadata; Node and Next.js | [repo](https://github.com/basementstudio/xmcp) |
| Vercel MCP Apps Next.js starter | repo 2026-02-10 | push 2026-11-20 | n/a | Vercel Labs | see repo | Claude and ChatGPT via the spec | [repo](https://github.com/vercel-labs/mcp-apps-nextjs-starter) |
| Vercel AI SDK MCP Apps | undated | n/a | n/a | Vercel | Apache-2.0 | host-side rendering | [docs](https://ai-sdk.dev/docs/ai-sdk-core/mcp-apps) |
| mcp-ui | 1.0.1 2025-05-16 | client 7.1.1 2026-05-09, server 6.1.0 2026-02-13 | 0 | MCP-UI-Org, 1 npm maintainer, 20 contributors | Apache-2.0 | spec hosts via `AppRenderer`, legacy MCP-UI hosts | [repo](https://github.com/MCP-UI-Org/mcp-ui) |
| `@openai/apps-sdk-ui` | 0.1.0 2025-11-20 | 0.2.2 2026-05-05 | 0 | OpenAI, 6 contributors | MIT | ChatGPT styling | [repo](https://github.com/openai/apps-sdk-ui) |
| C# Extensions.Apps | 2.0.0-preview.1 2026-06-26 | 2.4.0 2026-11-07 | 4 | MCP project | see repo | server, experimental | [NuGet](https://www.nuget.org/packages/ModelContextProtocol.Extensions.Apps) |
| Cloudflare Agents | 0.x | 0.34.1 2026-11-25 | 15 | Cloudflare, top committer 98% | MIT | no Apps helpers found in code search | [repo](https://github.com/cloudflare/agents) |
| Vercel `mcp-handler` | 0.0.1 2025-05-08 | 2.4.0 2026-11-12 | 5 | Vercel Labs | Apache-2.0 | transport only | [repo](https://github.com/vercel-labs/mcp-handler) |

Go and Java SDKs: no MCP Apps helpers found by code search for `io.modelcontextprotocol/ui`; hand-write the `_meta` fields from [build.md](build.md).

## Breaking-change history

| Project | Majors and renames |
|---|---|
| ext-apps | 1.0.0 2026-01-26; 2.0.0 2026-09-08 (split SDK packages, zod 4; wire unchanged); flat `ui/resourceUri` deprecated, 1.x handler registration "goes away in 3.0" |
| mcp-ui client | 2.0.0 2025-05-23, 3.0.0 2025-07-04, 4.0.0 2025-07-05, 5.0.0 2025-07-17, 6.0.0 2026-01-26, 7.0.0 2026-03-12; `UIResourceRenderer` now legacy; repo moved to MCP-UI-Org |
| Skybridge | 1.0.0 2026-05-18, 2.0.0 2026-09-04 |
| mcp-use | 1.0.0 2025-10-09, 2.0.0 2026-08-03 |
| xmcp | 1.0.0 2026-08-22 |
| mcp-handler | 1.0.0 2025-07-11, 2.0.0 2026-07-29 |
| FastMCP | 3.0.0 2026-02-18 (apps introduced), 4.0.0 2026-08-31 |
| MCPJam | 1.0.0 2025-10-05, 2.0.0 2026-02-23, 3.0.0 2026-08-26 |
| MCP Inspector | 1.0.0 2026-07-18, 2.0.0 2026-07-28 |
| ChatGPT | `openai/visibility` deprecated for `_meta.ui.visibility` (2026-07-21); `window.openai.toolInput`, `toolOutput`, `callTool`, `sendFollowUpMessage` are compatibility aliases |

## Named adopters

| Project | Adopters | Source type |
|---|---|---|
| ext-apps | Claude's and Microsoft's developer docs build on it | [Claude docs](https://claude.com/docs/connectors/building/mcp-apps/getting-started), [Microsoft Learn](https://learn.microsoft.com/microsoft-365/copilot/cowork/mcp-apps-support) |
| Open WebUI (as a host) | embeds `AppBridge` from ext-apps 2.0.4 | [MCPApp.svelte](https://github.com/open-webui/open-webui/blob/main/src/lib/components/chat/Messages/MCPApp.svelte) |
| Skybridge | Datadog, Bitmovin, Evaneos, Touchstream, Cottages.com | logos in the project's own README; not independently verified |
| mcp-use | AgentMail, CoinGecko, Alpha Vantage and others | logos on the vendor homepage; the one case study is about a server, not an App |
| mcp-ui | Goose, LibreChat as hosts | project README |
| everything else | none found | |

## Hype filter

- **"Production ready" without adopters:** mcp-ui says its packages are "ready for production use"; no adopters beyond hosts and no release in 90 days.
- **Self-reported logos:** Skybridge and mcp-use adopter logos are the vendors' own; no third-party source ties them to MCP Apps.
- **Stars are not a signal here:** FastMCP's stars measure the server framework, mcp-ui's a stalled renderer. No ring used stars.
- **Demo-only:** ext-apps examples and basic-host, openai-apps-sdk-examples, framework example galleries.
- **Single-maintainer risk:** mcp-ui (1 npm maintainer); MCP Inspector and Cloudflare Agents (one committer wrote almost all recent commits); xmcp and MCPJam (2 npm maintainers).
- **Vendor lock-in:** ChatGPT-only `window.openai` (`widgetState`, `setWidgetState`, `widgetSessionId`, `uploadFile`, `selectFiles`, `getFileDownloadUrl`, `requestModal`, `requestCheckout` in private beta). Claude-only: side panel, entry points, embedded sites, behind organization access and a Verified listing. Host-specific `ui.domain` formats.
- **Packaging mismatches:** ext-apps npm `latest` is 2.0.4 while 2.1.0 is published; Skybridge MIT in the repo, ISC on npm.
- **Not verified:** the contents and dates of both Figma kits, the LibreChat version that introduced Apps, whether the Cursor 3.10 rendering regression is fixed, and whether logo companies ship MCP Apps.

## Refresh

```bash
curl -s https://registry.npmjs.org/@modelcontextprotocol/ext-apps | jq '{latest: ."dist-tags".latest, time: .time | to_entries | sort_by(.value) | .[-5:]}'
gh api repos/OWNER/REPO/releases --jq '.[:10][] | .tag_name + " " + .published_at'
gh api 'repos/OWNER/REPO/commits?per_page=100' --jq '[.[].author.login] | group_by(.) | map({(.[0]): length}) | add'
curl -s https://pypi.org/pypi/fastmcp/json | jq '.info.version'
```

Then re-read the [Extension Support Matrix](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/extensions/client-matrix.mdx) and each adopter source.
