---
name: session-tldr
description: 'Tells the person in one screen where the agent session stands and what they must decide to unblock it - done with proof, left to do, what they need to know, numbered decisions with a recommendation - every PR, commit, ticket and file linked and checked live, not recalled. Use when asked for a tldr, recap, status or summary of this session, where are we, what is left, what do you need from me, what should I decide, or to unblock you; before a break or hand-off; when a long session has many open threads. Not for summarizing a document, article, thread or codebase. Dutch - waar staan we, wat moet ik beslissen, samenvatting van deze sessie.'
---

# Session TL;DR

The reader answers or approves; you do everything else. They were away: plain words, a few words for any jargon, no preamble, one screen. Shape and tone: [example.md](example.md).

## 1. Check the state now

Report nothing from recall. For every repository the session touched, run:

```bash
git status --short; git branch --show-current
git log --oneline @{upstream}..HEAD
git worktree list
```

Then read each PR's state and CI result (`gh pr view N --json state,statusCheckRollup`, `glab mr view N`, or the forge's REST API), each ticket's status, and every background job or deployment the session started. Something you cannot check is written **unverified**. "Works" names the check that showed it.

## 2. Link every reference

Never name a thing without linking it. If a link cannot be built, say so.

- **Workspace file:** markdown link to the path relative to the workspace root, `#L42` for a line.
- **PR, commit, branch, release:** from `git remote get-url origin` → [links.md](links.md) (forge path table, SSH-to-web hosts, submodules).
- **Ticket:** the tracker pattern from the repository contract below, else a URL a tool returned this session.
- **CI run, artifact, dashboard, doc:** the URL as a tool returned it.

**Repository contract.** Read a `## Session TL;DR` block in the repo's `AGENTS.md` or `CLAUDE.md` first when present: forge web host, tracker URL pattern, extra approvals. Never guess a host or ticket URL. Template: [README.md](README.md).

## 3. Turn waiting actions into decisions

Every action waiting on the person under the rules you were given (project `AGENTS.md`/`CLAUDE.md`, user instructions, memory) is a decision. Where those rules are silent, these still need a person: merge, release, deploy; changing production or shared live state; spending money (runs × model × approximate cost); deleting what cannot be restored; publishing or sending anything outside the session.

## 4. Write exactly these four sections

**✅ Done** - one bullet per finished outcome: what, link, proof (`tests green`, `CI green`, `pushed, not merged`).

**🔜 Still to do (this session)** - in order; each **I'll do it** or **blocked on you → decision #N**.

**🧠 What you need to know** - only what changes their picture: surprises, risks, broken or skipped steps, money spent, state left behind (unpushed branches, uncommitted files, worktrees, running jobs, live changes).

**🗳️ Decisions for you** - numbered; each has:
- the question in one line, linked to what it touches;
- two or three options, each with its consequence in one clause;
- your recommendation and why, in one line;
- what you do the moment they answer.

With nothing to decide: "Nothing blocks me - I'll continue with" plus the next step. An empty section says "none".

Last line: the shortest reply that unblocks you, such as "Reply `1A, 2 ok` and I'll finish."

## Focus

When the person names a focus (one PR, one topic), keep the four sections, scoped to it. Reply in the person's language.

## Gotchas

- **A branch, PR or job you remember is a claim until checked.** Remembered "open" work is often already merged, empty or gone; step 1 is never skipped.
- **The decisions section is the point.** A TL;DR that only lists work makes the reader find the ask themselves; rewrite until each decision can be answered with one token.
- **Approvals hide in "Still to do".** "Merge after CI" is a decision, not a task you will do.
