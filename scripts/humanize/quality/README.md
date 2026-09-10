# Quality runs

One file per run of `workflows/quality-retest.js`, the return value of the workflow verbatim: per
comparison and language, each case's verdict, facts kept, inventions quoted, both graders'
naturalness scores, the flattening decision with the scanner's variation numbers, and the leakage
count. These are the evidence behind the tables in `../COMPARISON.md`; render them with
`workflows/render_results.py "<label>=<file>" ...`.

| File | Skill measured |
| --- | --- |
| `seed1.json` | Before the stance rule (SKILL.md step 5 and the stance gotcha as shipped in 0.2.0 minus commit `04afd69`) |
| `seed2.json` | After the stance rule, as shipped in 0.2.0 |
| `seed3.json` | Same skill as seed 2; the second measurement of the after-state |
