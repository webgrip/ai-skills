---
name: session-tldr
description: 'Hands the person a TL;DR of the current agent session that they can act on in one reply - what is done and how it was verified, what is left and who it waits on, what they need to know (surprises, spend, state left behind), and numbered decisions with options, a recommendation and the next action - with every PR, commit, ticket, file and CI run as a link, checked against the live repository state rather than recalled. Use when the person asks for a tldr, a recap or status of this session, where we are, what is left, what you need from me, what I need to decide, or to be unblocked; at a hand-off or before a break; or when a long session has piled up open threads. Not for summarizing a document, article, thread or codebase. Dutch - waar staan we, wat moet ik beslissen, samenvatting van deze sessie.'
---

# Session TL;DR

The reader's only job after reading is to answer or approve; you do the rest. Write for someone who was away: plain words, jargon explained in a few words, no preamble.

## 1. Check before you write

Recall is not evidence. Before naming any piece of state, check it now:

- `git status --short`, the current branch, `git log @{upstream}..HEAD` (unpushed commits), `git worktree list`, and the same for every other repository the session touched.
- Pull requests: their real state (open, merged, closed) and CI result, through the forge CLI or API you have (`gh`, `glab`, `tea`, a REST call). Tickets: their status in the tracker.
- Background jobs, deployments and anything the session changed outside git (config files, live environments).

Anything you cannot check is marked **unverified**. A statement that something works names the check that showed it.

## 2. Every reference is a link

Never name a thing without linking it.

| Thing | Link |
| --- | --- |
| File or line in the workspace | a markdown link whose target is the path relative to the workspace root, with `#L42` appended for a line |
| PR, commit, branch, release | built from `git remote get-url origin`; [links.md](links.md) has the GitHub, GitLab, Forgejo/Gitea and Bitbucket forms and the SSH-to-web host mapping |
| Ticket | the tracker URL pattern from the repository contract (below), else a URL a tool returned this session |
| CI run, artifact, dashboard, doc | the URL as a tool returned it |

If a link cannot be built, say so instead of leaving a bare name.

**Repository contract.** A consumer repository may declare its instance facts in `AGENTS.md` or `CLAUDE.md` under a `## Session TL;DR` heading: the forge web host when it differs from the SSH host, the tracker URL pattern, and approvals beyond the defaults below. Read it first when present; never guess a host or a ticket URL. The [README](README.md) has the template.

## 3. Approvals the reader must give

List as decisions every action waiting on the person under the rules you were given (project `AGENTS.md` or `CLAUDE.md`, user instructions, memory). Where those are silent, these always need a person: merging, releasing or deploying; changing production or shared live state; spending money (state runs × model × approximate cost); deleting what cannot be restored; anything published or sent outside the session.

## 4. Format

Exactly these four sections, in this order. A section with nothing in it says "none".

### ✅ Done
What this session finished. One bullet each: outcome, link, how it was verified (`tests green`, `CI green`, `pushed, not merged`).

### 🔜 Still to do (this session)
What is left, in the order you will do it. Mark each **I'll do it** or **blocked on you → decision #N**.

### 🧠 What you need to know
Only what changes the reader's picture: surprises, risks, what broke or was skipped, money spent, state left behind (unpushed branches, uncommitted files, worktrees, running jobs, live changes). Leave out anything they need neither to act on nor to remember.

### 🗳️ Decisions for you
Numbered. Each one:
- **The question** in one line, linked to what it touches.
- **Options**, two or three, each with its consequence in one clause.
- **Recommendation** and why, in one line.
- **What you will do the moment they answer.**

With nothing to decide, write "Nothing blocks me - I'll continue with" and the next step.

End with one line: the shortest reply that unblocks you, such as "Reply `1A, 2 ok` and I'll finish."

## Gotchas

- 2026-10-11: from memory, a session described a branch as an open piece of work; checking showed the branch had no commits and its change was already on trunk. Check before you write, every time.
- A TL;DR that only lists work is a status report. The decisions section is the point: if the reader has to work out what you need from them, rewrite it.
- When the person narrows the TL;DR to one PR or topic, keep all four sections, scoped to that focus.
