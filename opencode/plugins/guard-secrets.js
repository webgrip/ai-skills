/**
 * guard-secrets — opencode v2 plugin (Plugin.define / ctx.tool.hook).
 * Port of the v1 plugin (git history) and claude-config's PreToolUse hook.
 * Blocks plaintext-secret leaks before the edit/write tool runs:
 *   1. never create decrypted secret artifacts (*.decrypted*, *decrypted~*)
 *   2. a *.sops.yaml / *.sops.yml write must contain SOPS ciphertext (ENC[)
 *   3. gitleaks scans the new content, and only a finding blocks: gitleaks
 *      missing, timing out or exiting with anything but the findings code
 *      warns and continues
 * Blocking = throw; a hook failure fails the operation it intercepts and
 * the message surfaces to the model (v2 equivalent of v1's throw / the
 * shell hook's exit-2).
 *
 * G3-probed 2026-07-14 on 0.0.0-next-15495: args live at input.input with
 * {path, content}. Older fallbacks retained for cross-build safety.
 * Pinned against @opencode-ai/plugin 0.0.0-next-15495.
 */
import { Plugin } from "@opencode-ai/plugin/v2";
import { basename, join } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";

const run = promisify(execFile);

const LEAKS_FOUND_EXIT_CODE = 10;
const SCAN_TIMEOUT_MS = 30_000;
const COMPLIANT_PATH =
  "Reference the value instead of writing it: follow the repo's own secrets convention " +
  "where it documents one, else keep the value in the vault and read it with an " +
  "ExternalSecret (SOPS only at the floor), wired by existingSecret/envFromSecret.";

function blocked(message) {
  return new Error(`BLOCKED: ${message}`);
}

function warn(message) {
  console.warn(`guard-secrets: ${message}`);
}

async function gitleaksPath() {
  try {
    const { stdout } = await run("/bin/sh", ["-c", "command -v gitleaks"]);
    return stdout.trim() || null;
  } catch {
    return null;
  }
}

async function gitleaksExitCode(gitleaks, content) {
  const scanDir = await mkdtemp(join(tmpdir(), "guard-secrets-"));
  const target = join(scanDir, "content.txt");
  try {
    await writeFile(target, content);
    await run(
      gitleaks,
      ["detect", "--no-banner", "--no-git", "--redact", "--exit-code", String(LEAKS_FOUND_EXIT_CODE), "-s", target],
      { timeout: SCAN_TIMEOUT_MS },
    );
    return 0;
  } catch (error) {
    if (typeof error?.code === "number") return error.code;
    throw error;
  } finally {
    await rm(scanDir, { recursive: true, force: true }).catch(() => {});
  }
}

async function scanPlaintext(base, content) {
  const gitleaks = await gitleaksPath();
  if (!gitleaks) {
    warn("gitleaks not on PATH; plaintext scan skipped. Pin it in .mise.toml.");
    return;
  }
  let exitCode;
  try {
    exitCode = await gitleaksExitCode(gitleaks, content);
  } catch (error) {
    warn(`gitleaks could not run (${error?.message ?? error}); plaintext scan skipped.`);
    return;
  }
  if (exitCode === LEAKS_FOUND_EXIT_CODE) {
    throw blocked(`gitleaks flagged a likely plaintext secret in ${base}. ${COMPLIANT_PATH}`);
  }
  if (exitCode !== 0) {
    warn(`gitleaks exited ${exitCode} without a finding; plaintext scan skipped. Run 'gitleaks version' by hand to see why.`);
  }
}

export default Plugin.define({
  id: "webgrip.guard-secrets",
  setup: async (ctx) => {
    ctx.tool.hook("execute.before", async (input) => {
      const tool = (input?.tool ?? input?.name ?? "").toLowerCase();
      if (tool !== "edit" && tool !== "write") return;

      const args = input?.input ?? input?.args ?? {};
      const file = args.path ?? args.filePath ?? args.file_path ?? "";
      const content = args.content ?? args.newString ?? args.new_string ?? "";
      if (!file) return;
      const base = basename(file);

      if (/\.decrypted|decrypted~/.test(base)) {
        throw blocked(
          `refusing to write a decrypted secret artifact (${base}). Plaintext secrets never ` +
            "touch disk: the value stays in the vault, or at the floor in an encrypted *.sops.yaml.",
        );
      }

      if (/\.sops\.ya?ml$/.test(base) && content && !content.includes("ENC[")) {
        throw blocked(`${base} is a SOPS file but the content isn't encrypted. Edit plaintext elsewhere, then 'sops --encrypt'.`);
      }

      if (content) await scanPlaintext(base, content);
    });
  },
});
