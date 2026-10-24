# security-review-triage

A defensive security skill for the questions that arrive after a scanner, an agent or a person says "this looks like a vulnerability": is it real, does it affect us, how far does it reach, who do we tell, and did the fix work.

What it teaches the agent:

- **Evidence discipline**: every claim labelled supplied, inspected, observed or inferred, and "not proven" as the default
- **Code and infrastructure review**: diff-scoped review with a confidence gate, and infrastructure rated by exposure × blast radius
- **Triage**: restate the claim, run the dismissal tests, find the asset's real guard, argue the opposite case, end on a clear verdict
- **Blast-radius cards**: entry point, position and privileges needed, asset reached, what limits it and what it does not give
- **Advisory mapping**: OSV and GitHub advisories checked against the shipped artifact, worded without overclaiming
- **Private disclosure**: the right channel, nothing public before the advisory, and a report draft that matches GitHub's form
- **Two-way verification**: a fix counts only when the bad case is blocked and the legitimate case still works, proven on the live object

It describes attacks by their shape only and never produces payloads or exploits.
