# Auth — how opencode talks to Claude at webgrip

One file controls this for the whole team: `opencode/org.opencode.json`
(distributed by `scripts/install_opencode.sh`). Changing auth = editing that
file + everyone re-running the bootstrap.

Context (2026-07-14): Anthropic's billing split went live — **any**
third-party/Agent-SDK usage (opencode, `claude -p`, the Max bridge) now
meters against the prepaid extra-usage pool at API rates, not plan limits.
That killed the bridge's only advantage (free Max quota), so the estate
default is now the **metered LiteLLM plane** — which is where we were headed
anyway (homelab ADR-0044). First-party Claude Code still draws plan limits,
so a Max subscription keeps its value there.

## 1. Default: the webgrip LiteLLM plane

opencode's `webgrip` provider points at **`https://litellm.webgrip.dev/v1`**
(OpenAI-compatible; VPN/LAN only). LiteLLM fronts the Anthropic models
(`claude-opus-4-8`, `claude-sonnet-5`, `claude-haiku-4-5`), meters spend
per key in its Postgres ledger, and enforces per-key budgets. You
authenticate with a **personal virtual key**, never the master key.

**One-time setup:**

```bash
# 1. Mint a personal virtual key from the master key (needs cluster access;
#    LITELLM_MASTER_KEY lives in OpenBao secret/litellm). From a kube context:
kubectl -n ai exec deploy/litellm -- \
  sh -c 'curl -s localhost:4000/key/generate \
    -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"key_alias\":\"ryan-opencode\",\"max_budget\":50,\"models\":[\"claude-opus-4-8\",\"claude-sonnet-5\",\"claude-haiku-4-5\"]}"'
# → returns {"key":"sk-..."} . That is your WEBGRIP_LLM_KEY.

# 2. Put it in your shell profile (never in any config file):
export WEBGRIP_LLM_KEY="sk-..."

# 3. Verify the endpoint before touching opencode (must be on VPN/LAN):
curl -s https://litellm.webgrip.dev/v1/models \
  -H "Authorization: Bearer $WEBGRIP_LLM_KEY" | head
# 4. Then:
opencode2 run "say ok"
```

The org config sets `model: webgrip/claude-opus-4-8` — nothing else to do.

> Higher fidelity (prompt caching / extended thinking) rides better on
> LiteLLM's **Anthropic** route than the OpenAI-compatible one. To switch,
> point opencode's built-in provider instead:
> `"providers": { "anthropic": { "settings": { "baseURL": "https://litellm.webgrip.dev/anthropic", "apiKey": "{env:WEBGRIP_LLM_KEY}" } } }`
> and `model: anthropic/claude-opus-4-8`. Try this if OpenAI-shape params
> get dropped; verify with a real prompt first.

## 2. Direct Anthropic API key (no proxy)

If LiteLLM is down or you're off-VPN: swap the provider to Anthropic direct.

```jsonc
"providers": { "anthropic": { "settings": { "apiKey": "{env:ANTHROPIC_API_KEY}" } } }
```

Metered on your own Console org; loses the central ledger/budgets. `{env:…}`
only — never a literal key.

## 3. Personal Max bridge — personal use only, now metered

The `opencode-with-claude` / Meridian bridge (Agent SDK → your `claude`
login) still works, but post-split it draws your **extra-usage** balance at
API rates — no cheaper than a key, plus personal-account risk. Kept only as
a documented personal option (`meridian profile add personal`), never the
org default, never on work repos. See git history of this file for the full
bridge setup.

## 4. Local / offline (Ollama)

Zero cost, no network: `providers.ollama` (see onboarding §5). Weaker at
multi-step tool use — a floor and a scratch/retest driver, not a Claude
replacement.

## House rules

- **Work repos never hard-code auth** — repo `opencode.json` carries MCP +
  permissions only; providers/credentials live in the org config + your env.
- **Secrets in env or a password manager, never in JSON, never committed.**
- `small_model` no longer exists on v2 — titles/compaction hit the main
  model, metered like everything else.

## Watch items

- LiteLLM `/metrics` is Enterprise-gated in OSS; a ledger→VictoriaMetrics
  exporter is the tracked follow-up (homelab). Spend still lands in the DB.
- Server-side guards (homelab ADR-0045): opencode does not run `.claude/`
  hooks, and `guard-secrets` blocking is unconfirmed on v2 — the durable
  control is moving secret/destructive guards into the LiteLLM/gateway
  layer. Until then, treat secret discipline as human-enforced.
