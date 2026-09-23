# Routing an agent to knowledge

## Evidence

- **Always-loaded index beats a skill.** Vercel's Next.js eval: baseline 53 %; the same knowledge
  as a skill 53 % (never invoked in 56 % of runs); skill plus an explicit instruction to use it
  79 %; a compressed docs index in `AGENTS.md` 100 %. The index was 8 KB, one path per line, under
  one directive: "Prefer retrieval-led reasoning over pre-training-led reasoning"
  ([post](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)).
- **Skills under-trigger.** Sandboxed `claude -p` runs: 50–59 % activation unaided; a
  UserPromptSubmit hook that makes the model decide per skill reached 100 %
  ([Spence](https://scottspence.com/posts/measuring-claude-code-skill-activation-with-sandboxed-evals)).
  Activation behaves closer to keyword matching than to semantic matching.
- **Just-in-time**: keep lightweight identifiers (paths) in context and load content when needed
  ([Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)).
  Grep finds code facts; semantic search helps in large repos with unfamiliar vocabulary
  ([Cursor](https://cursor.com/blog/semsearch)).

## Decision table

| Knowledge | Route |
|---|---|
| Must hold on every task | hook / CI, one line in the root file |
| Project decisions, flows, domain rules | `docs/` + an always-loaded pointer row |
| One subtree | path rule or nested file + a root pointer for tools without path loading |
| Procedure the user asks for by name | skill with a keyword-rich description, named in a root pointer |
| Version-specific framework API | docs MCP (Laravel Boost `search-docs`, Context7) + a root line saying when to call it |
| Public dependency internals | DeepWiki / GitMCP |
| Code facts (where X lives, who calls Y) | nothing written: grep finds them, a copy goes stale |
| Your docs for other people's agents | `llms.txt` + `.md` pages; agents inside a repo do not read it |

## Pointer table template

```markdown
## Before you change…
Prefer these docs over what you remember about this project.

| Before changing… | Read | Wrong without it |
|---|---|---|
| quotation PDFs (`app/Domains/Sqs/**/Pdf*`) | docs/quotation-pdfs.md | amounts derived in PHP |
| anything that recalculates prices | docs/recalculate-flow.md | writer called inside a transaction |
| a Laravel or Inertia API | Boost `search-docs` | a stale major-version API |
```

- Open each row with a trigger (verb + path or subject), point at one openable path, name the
  failure in a few words.
- One row per doc or subject, not per fact. Past ~40 rows, split by area into nested files.
- MCP tool names in generated guidelines differ per client
  ([laravel/boost#844](https://github.com/laravel/boost/issues/844)); check the name in each client.
