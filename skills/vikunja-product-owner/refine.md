# Refinement — raw ticket → Definition of Ready

The DoR (7 points + agent-assignability gate) is in [SKILL.md](SKILL.md). This file is the
execution: per-ticket procedure, the HTML template, and the bulk fan-out pattern.

## Per-ticket procedure

1. **Research before writing.** The repo (manifests/source, docs tree, decision records,
   runbooks, incident notes) + live state where the premise depends on live truth. Every Problem
   claim and criterion cites `file:line` or a live check. Never invent — an unverifiable claim
   becomes an explicit evidence-gap line, not a fact.
2. **Stale premises are a first-class finding.** If the work already shipped or the failure no
   longer exists, write the Problem as "Premise stale — …", reframe as verify-and-close, flag it.
3. Write the description per the template via `task_update`; sanity-check `priority`, the
   `impact/·` label, and set all three estimation labels — `effort/S|M|L` (work size),
   `time/hours|days|weeks` (wall-clock lead incl. soaks/waits), `uncertainty/low|med|high`
   (path clarity; high ⇒ spike first, never `agent-ready`) — against what research showed;
   correct drift and say so.
4. Labels: add `ready`, remove `needs-refinement` — via `label_add_to_task`/`label_remove_from_task`
   (NOT `labels_bulk_set_on_task` unless passing the complete set).
5. If sizing tripped (effort L without a slice, or uncertainty high without a spike): split — children via `task_create` +
   `relation_create` kind `subtask`, sequence with `precedes`.
6. Report per ticket: one-line what-changed + any evidence gap left open.

## HTML description template

TipTap HTML (verified round-trip: `<h3>`, `<p>`, `<code>`, `<ul>`, and the checkbox markup below
survive sanitization; the checklist renders with an x/y counter). Escape `&` as `&amp;`, shell
`<`/`>` as `&lt;`/`&gt;`. 1500–3500 chars. Never omit Problem, Acceptance criteria, or Verification.

```html
<p><strong>&lt;theme&gt;</strong> — <code>[P1 · impact H · effort M · time d · unc low]</code></p>
<h3>Problem</h3><p>What is wrong today + evidence: <code>path/file:12</code>, live symptom, decision record.</p>
<h3>Outcome</h3><p>One sentence end-state.</p>
<h3>Acceptance criteria</h3>
<ul data-type="taskList">
  <li data-checked="false" data-type="taskItem"><label><input type="checkbox"><span></span></label><div><p>criterion, verifiable against real state</p></div></li>
</ul>
<h3>Approach</h3><ol><li>Step naming a real repo path + applicable skill.</li></ol>
<h3>Verification</h3><p>The exact command/check that proves it live.</p>
<h3>Gates &amp; links</h3><ul><li>Blocked by: <em>&lt;exact ticket title&gt;</em> · <code>docs/…</code></li></ul>
```

(`data-checked="true"` + `checked` on the input for a pre-ticked box.)

## Condensed worked example (from the origin repo)

Title (unchanged): `Default-deny the security namespace — crown jewels sit on a flat network`

```html
<p><strong>Security — network containment</strong> — <code>[P1 · impact H · effort M · time d · unc low]</code></p>
<h3>Problem</h3><p>The <code>security</code> ns has no NetworkPolicy — any pod can reach the
secrets store. The opt-in default-deny generator is live but this ns never got the label
(<code>kubernetes/apps/security/namespace.yaml</code>).</p>
<h3>Outcome</h3><p>security ns default-deny; store reachable only from its clients.</p>
<h3>Acceptance criteria</h3><ul data-type="taskList">
<li data-checked="false" data-type="taskItem"><label><input type="checkbox"><span></span></label><div><p>generated default-deny + allow-dns present (<code>kubectl -n security get netpol</code>)</p></div></li>
<li data-checked="false" data-type="taskItem"><label><input type="checkbox"><span></span></label><div><p>a probe pod in another ns can NOT reach the store port</p></div></li>
</ul>
<h3>Approach</h3><ol><li>Sequence the DB-layer netpol component BEFORE the label flip (deadlock
otherwise); label the ns; per-app allows per the repo's reference pattern.</li></ol>
<h3>Verification</h3><p><code>kubectl -n security get netpol</code> + the blocked-probe test.</p>
<h3>Gates &amp; links</h3><ul><li><code>docs/…/adr-….md</code></li></ul>
```

## Bulk fan-out (N tickets, research-grade, without flooding the parent context)

Proven on 92 tickets / 11 agents; **60/92 came back flagged** — stale premises, drift, real bugs.

1. **Packets**: split tickets into theme groups of ~7–10; write each group as a JSON file
   (`packet-<group>.json`: `[{n, theme, title, prio, impact, effort, …}]`).
2. **Shared brief** (`brief.md`, one file all agents read): the DoR + template contract, research
   standard (cite `file:line`; stale premises are findings; never invent), output contract —
   write `refined-<group>.json` as `[{"n": <int>, "html": "...", "flags": ["..."]}]`, validate it
   parses before finishing, final message = one line per ticket, **never paste HTML into the
   final message**.
3. **Launch one general-purpose agent per packet** (single message, parallel); each researches the
   repo read-only and writes only its output JSON.
4. **Central validation** before applying: JSON parses · every packet ticket covered ·
   `'data-type="taskList"' in html` · no markdown smells (`re.search(r'(^|\n)#{1,3} |\]\(', html)`) ·
   cited repo paths exist (beware regex false-positives on basename fragments — check context
   before accusing) · spot-read 2–3 drafts for invented claims.
5. **Apply centrally in ONE MCP session** (sequential — parallel sessions stress the server) via
   [scripts/mcp_client.py](scripts/mcp_client.py); swap labels; report flags grouped
   (stale premises / drift / bugs / evidence gaps).

Gotcha: a sub-agent that itself spawns children may stall after its children finish (their
notifications bubble to the main loop) — nudge it via `SendMessage` with the findings summary.
