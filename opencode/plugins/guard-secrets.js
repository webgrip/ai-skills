/**
 * guard-secrets — opencode v2 plugin (Plugin.define / ctx.tool.hook).
 * Port of the v1 plugin (git history) and claude-config's PreToolUse hook.
 * Blocks plaintext-secret leaks before the edit/write tool runs:
 *   1. never create decrypted secret artifacts (*.decrypted*, *decrypted~*)
 *   2. a *.sops.yaml / *.sops.yml write must contain SOPS ciphertext (ENC[)
 *   3. best-effort plaintext-secret scan via gitleaks (warns and continues
 *      when gitleaks isn't installed)
 * Blocking = throw; a hook failure fails the operation it intercepts and
 * the message surfaces to the model (v2 equivalent of v1's throw / the
 * shell hook's exit-2).
 *
 * G3-probed 2026-07-14 on 0.0.0-next-15495: args live at input.input with
 * {path, content}. Older fallbacks retained for cross-build safety.
 * Pinned against @opencode-ai/plugin 0.0.0-next-15495.
 */
import { Plugin } from "@opencode-ai/plugin/v2";
import { basename, dirname, join, relative, resolve } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { writeFile, rm, mkdir, mkdtemp, stat } from "node:fs/promises";
import { tmpdir } from "node:os";

const run = promisify(execFile);

async function gitleaksPath() {
  try {
    const { stdout } = await run("/bin/sh", ["-c", "command -v gitleaks || mise which gitleaks 2>/dev/null"]);
    return stdout.trim() || null;
  } catch {
    return null;
  }
}

async function exists(path) {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

// The repository root above `file` and its .gitleaks.toml, if any, so the
// repository's own allowlist (test fixtures, published test vectors) applies.
async function repoConfig(file) {
  let dir = dirname(resolve(file));
  for (;;) {
    const config = join(dir, ".gitleaks.toml");
    if (await exists(config)) return { root: dir, config };
    if (await exists(join(dir, ".git"))) return { root: dir, config: null };
    const parent = dirname(dir);
    if (parent === dir) return { root: null, config: null };
    dir = parent;
  }
}

export default Plugin.define({
  id: "webgrip.guard-secrets",
  setup: async (ctx) => {
    ctx.tool.hook("execute.before", async (input) => {
      const tool = (input?.tool ?? input?.name ?? "").toLowerCase();
      if (tool !== "edit" && tool !== "write") return;

      // G3-probed on 0.0.0-next-15495: hook input = {tool, sessionID, agent,
      // assistantMessageID, toolCallID, input}; write args = {path, content}.
      const args = input?.input ?? input?.args ?? {};
      const file = args.path ?? args.filePath ?? args.file_path ?? "";
      const content = args.content ?? args.newString ?? args.new_string ?? "";
      if (!file) return;
      const base = basename(file);

      // 1) Never create decrypted secret artifacts.
      if (/\.decrypted|decrypted~/.test(base)) {
        throw new Error(
          `BLOCKED: refusing to write a decrypted secret artifact (${base}). Secrets live only in *.sops.yaml.`,
        );
      }

      // 2) A SOPS file must contain ciphertext, never plaintext.
      if (/\.sops\.ya?ml$/.test(base) && content && !content.includes("ENC[")) {
        throw new Error(
          `BLOCKED: ${base} is a SOPS file but the content isn't encrypted. Edit plaintext elsewhere, then 'sops --encrypt'.`,
        );
      }

      // 3) Best-effort plaintext-secret scan.
      if (content) {
        const gl = await gitleaksPath();
        if (!gl) {
          console.warn("guard-secrets: gitleaks not on PATH or in mise; plaintext scan skipped. Pin it in .mise.toml.");
          return;
        }
        const { root, config } = await repoConfig(file);
        const scratch = await mkdtemp(join(tmpdir(), "guard-secrets-"));
        try {
          let rel = root ? relative(root, resolve(file)) : basename(file);
          if (!rel || rel.startsWith("..")) rel = basename(file) || "content.txt";
          const target = join(scratch, rel);
          await mkdir(dirname(target), { recursive: true });
          await writeFile(target, content);
          const argv = ["detect", "--no-banner", "--no-git", "--redact", "-s", scratch];
          if (config) argv.push("--config", config);
          await run(gl, argv);
        } catch (err) {
          if (err?.code === 1) {
            throw new Error(
              `BLOCKED: gitleaks flagged a likely plaintext secret in ${base}. Use a SOPS secret + Helm value wiring (existingSecret/envFromSecret).`,
            );
          }
          if (err instanceof Error && err.message.startsWith("BLOCKED:")) throw err;
          // other environment noise: swallow, mirroring the shell hook's best-effort
        } finally {
          await rm(scratch, { recursive: true, force: true }).catch(() => {});
        }
      }
    });
  },
});
