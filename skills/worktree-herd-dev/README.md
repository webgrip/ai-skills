# worktree-herd-dev

Parallel git worktrees, each with its own Laravel Herd `.test` domain and isolated Vite port — so you can run several branches of the same Laravel app side by side and switch between them in the browser by switching tabs.

What the skill does:

- **Worktree + Herd site in one command** — `worktree-herd-setup <branch>` creates (or reuses) a worktree next to the main repo, copies `.env`, sets `APP_URL`, an auto-incremented `VITE_PORT`, and a unique `SESSION_COOKIE`, derives the Herd site name from the main repo's `herd.yml`/`APP_URL` (with a collision guard against existing Herd sites), links it with `herd link --secure --isolate`, and installs composer + node dependencies. If any step fails, everything the run created is rolled back
- **Per-worktree databases (opt-in)** — `--db` or `database: per-worktree` creates a database per branch (pgsql/mysql/sqlite from `DB_CONNECTION`), runs `artisan migrate`, and drops it on cleanup — with open-session diagnostics when a drop is blocked
- **Safe teardown** — `worktree-herd-cleanup` resolves the Herd site from a per-worktree marker (never guesses), supports `--dry-run`, refuses in-use or genuinely dirty worktrees without `--force`, verifies Herd actually unlinked, and refuses to touch the main worktree
- **Project config + hooks** — a `worktree-herd.yml` (base branch, worktree location, database mode, asset build, editor) plus executable `.worktree-herd/post-setup` / `pre-cleanup` hooks for anything project-specific: seeders, admin users, multi-domain `.env` rewrites
- **Registry-based port allocation** — `<repo>-worktrees/.registry.json` tracks each worktree's site and Vite port so they never collide
- **Editor tasks** — `worktree-herd-install-tasks` writes per-project `.vscode/tasks.json` entries for setup/cleanup

Requires macOS with [Laravel Herd](https://herd.laravel.com), plus `git`, `node`, and `composer` (`psql`/`mysql` only when per-worktree databases are enabled).

## Install

**Claude Code (as a plugin, recommended):**

```
/plugin marketplace add https://forgejo.webgrip.dev/webgrip/webgrip-ai-skills.git
/plugin install worktree-herd-dev@webgrip-ai-skills
```

**Claude Code (manual):** copy `skills/worktree-herd-dev/` into your project's `.claude/skills/` (shared with your team via git) or `~/.claude/skills/` (just you).

**Claude app / claude.ai:** grab `worktree-herd-dev.skill` from the [latest release](https://forgejo.webgrip.dev/webgrip/webgrip-ai-skills/releases/latest), upload it via Settings → Skills (or attach it in a chat), and hit *Save skill*.

After installing, run the skill's one-time CLI install (links `worktree-herd-setup`, `worktree-herd-cleanup`, and `worktree-herd-install-tasks` into `~/.local/bin`):

```bash
bash <path-to-skill>/scripts/install.sh
```

## Use

Open Claude in a Laravel project served by Herd and say, for example:

- *"set up a worktree for feature/my-branch with its own Herd site"*
- *"give this branch its own .test domain and database so I can test it next to main"*
- *"clean up the worktree for feature/old-branch"*
- *"configure Herd for the worktree workspace I have open"*
- *"set up worktree-herd config for this project: branch off development, per-worktree databases"*

## Why

Reviewing or testing several branches of the same Laravel app normally means stashing, switching, and re-migrating — or juggling one shared `.test` domain. A worktree per branch with its own Herd site and Vite port makes branches independently servable: main stays at `https://mijn.example.test` while the feature branch runs at `https://feature.example.test`, dev servers and all.

## License

MIT
