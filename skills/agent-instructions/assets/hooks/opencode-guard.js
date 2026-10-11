import { spawnSync } from 'node:child_process';
import { join } from 'node:path';

const GUARDS = ['.claude/hooks/stage-explicit-paths.py'];

export const ShellGuards = async ({ worktree }) => ({
  'tool.execute.before': async (input, output) => {
    const command = output.args?.command;
    if (typeof command !== 'string') return;
    for (const guard of GUARDS) {
      const result = spawnSync('python3', [join(worktree, guard)], {
        input: JSON.stringify({ tool_name: input.tool, tool_input: { command } }),
        encoding: 'utf8',
      });
      if (result.status === 2) throw new Error(result.stderr.trim());
    }
  },
});
