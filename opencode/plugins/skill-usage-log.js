/**
 * skill-usage-log — opencode twin of the skill-usage plugin's Claude Code hook.
 * Appends one JSONL line per skill invocation to
 * ~/.config/opencode/skill-usage.jsonl (local file, never sent anywhere), so
 * the skill-usage skill can report which skills are used, dead, or
 * undertriggering across both tools.
 * Fail-open: telemetry must never break a session, so every error is swallowed.
 * Distributed by scripts/install_opencode.sh (symlinked into
 * ~/.config/opencode/plugins/).
 */
import { appendFile, mkdir } from "node:fs/promises";
import { homedir } from "node:os";
import { dirname, join } from "node:path";

const LOG = join(homedir(), ".config", "opencode", "skill-usage.jsonl");

export const SkillUsageLog = async () => {
  return {
    "tool.execute.after": async (input, output) => {
      try {
        if ((input?.tool ?? "").toLowerCase() !== "skill") return;
        const args = output?.args ?? {};
        const skill = args.name ?? args.skill ?? "";
        if (!skill) return;
        await mkdir(dirname(LOG), { recursive: true });
        await appendFile(
          LOG,
          JSON.stringify({
            ts: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
            skill,
            cwd: input?.directory ?? process.cwd(),
            session: input?.sessionID ?? "",
            tool: "opencode",
          }) + "\n",
        );
      } catch {
        // best-effort: never disrupt the session
      }
    },
  };
};
