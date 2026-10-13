# Sources and credits

The rules in this skill are paraphrased and recombined from the sources below; no passage is copied at length. Anthropic's `mcp-builder` and `mcp-server-dev` are Apache-2.0 and informed the interview, deployment tree, surface-size patterns and eval format. Sentry's MCP docs and skills are FSL-1.1 and are paraphrased only. Evidence strength: the MCP specification is normative; Claude and vendor docs are authoritative for their own products; practitioner posts and talks are experience reports; tool-count thresholds are heuristics, not measured limits.

## Specification and project

- [Versioning (current revision)](https://modelcontextprotocol.io/specification/versioning)
- [2026-07-28 key changes](https://modelcontextprotocol.io/specification/2026-07-28/changelog) and the [release post](https://blog.modelcontextprotocol.io/posts/2026-07-28/) by David Soria Parra and Den Delimarsky
- [Tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools), [schema](https://modelcontextprotocol.io/specification/2026-07-28/schema), [Streamable HTTP](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http)
- [Authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization) and [client registration](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/client-registration)
- [Multi round-trip requests](https://modelcontextprotocol.io/specification/2026-07-28/basic/patterns/mrtr), [elicitation](https://modelcontextprotocol.io/specification/2026-07-28/client/elicitation), [deprecated features](https://modelcontextprotocol.io/specification/2026-07-28/deprecated)
- [Security best practices](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices), [local server security](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/local-server-security)
- [SDKs and tiers](https://modelcontextprotocol.io/docs/2026-07-28/sdk), [extensions client matrix](https://modelcontextprotocol.io/extensions/client-matrix)
- [Inspector CLI](https://modelcontextprotocol.io/docs/2026-07-28/tools/inspector/cli), [conformance suite](https://github.com/modelcontextprotocol/conformance), [Go SDK](https://github.com/modelcontextprotocol/go-sdk)
- Den Delimarsky: [2025-11-25 authorization changes](https://den.dev/blog/mcp-november-authorization-spec/), [resource server split](https://den.dev/blog/new-mcp-authorization-spec/)

## Anthropic and Claude

- [`mcp-builder` skill](https://github.com/anthropics/skills/tree/main/skills/mcp-builder) (Apache-2.0)
- [`mcp-server-dev` plugin](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/mcp-server-dev) (Apache-2.0)
- [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp), [advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use)
- Claude connector docs: [building](https://claude.com/docs/connectors/building), [authentication](https://claude.com/docs/connectors/building/authentication), [lazy authentication](https://claude.com/docs/connectors/building/lazy-authentication), [review criteria](https://claude.com/docs/connectors/building/review-criteria), [what to build](https://claude.com/docs/connectors/building/what-to-build)

## Practitioners and vendors

- Jeremiah Lowin: [Stop converting your REST APIs to MCP](https://jlowin.dev/blog/stop-converting-rest-apis-to-mcp), [Your MCP server is bad](https://ai.engineer/talks/96G7FLab8xc-your-mcp-server-is-bad-you-should), [FastMCP 3.0](https://jlowin.dev/blog/fastmcp-3-launch), [FastMCP what's new](https://gofastmcp.com/getting-started/whats-new)
- Simon Willison: [the lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/), [MCP prompt injection problems](https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/), [Supabase MCP](https://simonwillison.net/2025/Jul/6/supabase-mcp-lethal-trifecta/), [stateless MCP](https://simonwillison.net/2026/Jul/31/)
- GitHub: [github-mcp-server](https://github.com/github/github-mcp-server), [server instructions and consolidated tools](https://github.blog/changelog/2025-10-29-github-mcp-server-now-comes-with-server-instructions-better-tools-and-more/), [scope filtering](https://github.blog/changelog/2026-01-28-github-mcp-server-new-projects-tools-oauth-scope-filtering-and-new-features/), [lessons from the launch](https://www.arcade.dev/blog/enterprise-mcp-lessons-from-githubs-mcp-server-launch/)
- Cloudflare: [the next generation of MCP](https://blog.cloudflare.com/mcp-v2/), [Code Mode for MCP](https://blog.cloudflare.com/code-mode-mcp/)
- Block: [layered tools](https://engineering.block.xyz/blog/build-mcp-tools-like-ogres-with-layers)
- Sentry: [sentry-mcp](https://github.com/getsentry/sentry-mcp) contributing docs and `mcp-audit`/`mcp-qa` skills (FSL-1.1, paraphrased)
- [Stripe MCP](https://docs.stripe.com/mcp), [Linear MCP](https://linear.app/docs/mcp)
- OpenAI Apps SDK: [plan tools](https://developers.openai.com/apps-sdk/plan/tools), [optimize metadata](https://developers.openai.com/apps-sdk/guides/optimize-metadata)
- Philipp Schmid: [MCP is not the problem, it's your server](https://www.philschmid.de/mcp-best-practices)
- [OWASP MCP Top 10](https://owasp.org/www-project-mcp-top-10/)
- [Braintrust: MCP testing and evals](https://www.braintrust.dev/articles/ultimate-guide-mcp-testing-evals)

## Clients

- [Claude Code MCP](https://code.claude.com/docs/en/mcp), [VS Code MCP configuration](https://code.visualstudio.com/docs/agents/reference/mcp-configuration), [Cursor MCP](https://cursor.com/docs/context/mcp)
