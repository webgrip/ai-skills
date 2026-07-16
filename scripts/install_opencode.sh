#!/usr/bin/env bash
# install_opencode.sh — set up (or update) the webgrip opencode estate for one person.
#
#   bash scripts/install_opencode.sh --profile junior|senior   (from a checkout)
#   curl -fsSL https://forgejo.webgrip.dev/webgrip/webgrip-ai-skills/raw/branch/main/scripts/install_opencode.sh | bash -s -- --profile senior
#
# Idempotent — run it again any time to pull updates. It:
#   1. clones/updates the repo to ~/.webgrip/webgrip-ai-skills
#   2. symlinks every skills/<name> into ~/.config/opencode/skills/ (per-skill
#      links, so personal skills coexist; stale org links are swept)
#   3. symlinks opencode/plugins/* and opencode/agents/* likewise
#   4. merges opencode/org.opencode.json + the chosen profile into
#      ~/.config/opencode/opencode.json (org keys win on conflict; every other
#      key you added yourself is preserved)
# See docs/onboarding-opencode.md for the human walkthrough and docs/auth.md
# for the auth story (bridge vs API key vs LiteLLM).
set -euo pipefail

# The estate's pinned opencode v2 beta build (Ryan owns bumps — see
# docs/onboarding-opencode.md "Bump runbook"). The binary is `opencode2`
# until GA.
OPENCODE_VERSION="0.0.0-next-15495"
OPENCODE_PLUGIN_VERSION="0.0.0-next-15495"  # tracks the binary generation

REPO_URL="${WEBGRIP_SKILLS_REPO:-https://forgejo.webgrip.dev/webgrip/webgrip-ai-skills.git}"
HOME_DIR="${WEBGRIP_SKILLS_HOME:-$HOME/.webgrip/webgrip-ai-skills}"
OC_DIR="$HOME/.config/opencode"
PROFILE="senior"

while [ $# -gt 0 ]; do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --profile=*) PROFILE="${1#*=}"; shift ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done
case "$PROFILE" in junior|senior) ;; *) echo "profile must be junior or senior" >&2; exit 1 ;; esac

echo "webgrip opencode bootstrap — profile: $PROFILE"

# 1. Clone or update. The clone is a managed cache (never hand-edited), so it
# hard-tracks origin/main — this survives force-pushes/amends upstream.
if [ -d "$HOME_DIR/.git" ]; then
  git -C "$HOME_DIR" fetch -q origin main
  git -C "$HOME_DIR" reset --hard -q origin/main
  echo "updated $HOME_DIR ($(git -C "$HOME_DIR" rev-parse --short HEAD))"
else
  mkdir -p "$(dirname "$HOME_DIR")"
  git clone -q "$REPO_URL" "$HOME_DIR"
  echo "cloned to $HOME_DIR ($(git -C "$HOME_DIR" rev-parse --short HEAD))"
fi

mkdir -p "$OC_DIR/skills" "$OC_DIR/plugins" "$OC_DIR/agents"

# Runtime deps opencode loads from the config dir: the plugin API
# (guard-secrets imports @opencode-ai/plugin/v2) and the openai-compatible
# provider the LiteLLM default uses. Pinned to the binary generation.
( cd "$OC_DIR" && npm i --silent --no-audit --no-fund \
    "@opencode-ai/plugin@$OPENCODE_PLUGIN_VERSION" "@ai-sdk/openai-compatible" >/dev/null 2>&1 ) \
  && echo "runtime deps ensured (@opencode-ai/plugin@$OPENCODE_PLUGIN_VERSION + @ai-sdk/openai-compatible)" \
  || echo "WARN: could not install config-dir runtime deps (need node/npm on PATH)"

# 2+3. Symlink skills, plugins, agents (org-owned links carry our clone path,
# so sweeping stale ones never touches personal files).
sweep_and_link() { # $1 = source dir, $2 = target dir
  local src="$1" dst="$2" link target
  for link in "$dst"/*; do
    [ -L "$link" ] || continue
    target="$(readlink "$link")"
    case "$target" in "$HOME_DIR"/*) [ -e "$target" ] || { rm "$link"; echo "swept stale $(basename "$link")"; } ;; esac
  done
  [ -d "$src" ] || return 0
  for entry in "$src"/*; do
    [ -e "$entry" ] || continue
    local name; name="$(basename "$entry")"
    case "$name" in README.md) continue ;; esac
    ln -sfn "$entry" "$dst/$name"
  done
}
sweep_and_link "$HOME_DIR/skills"           "$OC_DIR/skills"  && echo "skills linked"
sweep_and_link "$HOME_DIR/opencode/plugins" "$OC_DIR/plugins" && echo "plugins linked"
sweep_and_link "$HOME_DIR/opencode/agents"  "$OC_DIR/agents"  && echo "agents linked"

# 4. Merge org config + profile into the personal config. Org+profile keys win;
# everything else the user set is preserved. `_comment` keys are dropped.
python3 - "$HOME_DIR" "$OC_DIR/opencode.json" "$PROFILE" <<'PY'
import json, sys, os
home, cfg_path, profile = sys.argv[1], sys.argv[2], sys.argv[3]

def load(p):
    if not os.path.exists(p): return {}
    with open(p) as f: return json.load(f)

def strip_comments(o):
    if isinstance(o, dict):
        return {k: strip_comments(v) for k, v in o.items() if k != "_comment"}
    return o

def deep_merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out

org = strip_comments(load(f"{home}/opencode/org.opencode.json"))
prof = strip_comments(load(f"{home}/opencode/profiles/{profile}.json"))
managed = deep_merge(org, prof)
# substitute the clone path into instruction entries etc.
managed = json.loads(json.dumps(managed).replace("__WEBGRIP_SKILLS_HOME__", home))
user = load(cfg_path)
merged = deep_merge(user, managed)   # managed keys win; user keeps the rest

# v1→v2 migration: purge superseded v1 keys a pre-migration personal config
# may still carry (they'd otherwise survive as corpses next to the v2 keys —
# and a stale v1 `plugin` entry errors on v2).
for dead in ("provider", "permission", "plugin", "small_model", "command", "agent"):
    if dead in merged and dead not in managed:
        merged.pop(dead)
        print(f"migrated: dropped v1 key '{dead}'")
if isinstance(merged.get("mcp"), dict) and "servers" not in merged["mcp"]:
    merged["mcp"] = {"servers": merged["mcp"]}
    print("migrated: wrapped v1 mcp map into mcp.servers")

os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
with open(cfg_path, "w") as f: json.dump(merged, f, indent=2); f.write("\n")
print(f"config merged -> {cfg_path}")
PY

# Sanity notes.
if command -v opencode2 >/dev/null 2>&1; then
  installed="$(opencode2 --version 2>/dev/null | sed 's/^opencode2 v//')"
  [ "$installed" = "$OPENCODE_VERSION" ] ||     echo "WARN: opencode2 is $installed but the estate pin is $OPENCODE_VERSION — align with: npm i -g @opencode-ai/cli@$OPENCODE_VERSION"
else
  echo "NOTE: opencode2 not on PATH — install the pinned beta: npm i -g @opencode-ai/cli@$OPENCODE_VERSION (never @next — see docs/onboarding-opencode.md)"
fi
command -v claude   >/dev/null 2>&1 || echo "NOTE: the Claude bridge needs the claude CLI logged in (npm i -g @anthropic-ai/claude-code && claude auth) — see docs/auth.md"
echo "done. Open a repo and run: opencode2"
