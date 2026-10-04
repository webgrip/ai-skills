# AI features: assistants, generated content and agent actions

Guidance has converged across Microsoft's 18 Guidelines for Human-AI Interaction ([Amershi et al., CHI 2019](https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/)), Google's [People + AI Guidebook](https://pair.withgoogle.com/guidebook/), Apple's [Generative AI guidelines](https://developer.apple.com/design/human-interface-guidelines/generative-ai) (updated 8 June 2026) and the [Shape of AI](https://www.shapeof.ai/) pattern library. Use the HAX guidelines as a heuristic-evaluation checklist for any AI feature; that is how the paper validated them.

Contents: should it be AI · disclosure · input · latency and streaming · output, control and undo · agent actions · trust and overreliance · errors and refusals · feedback, memory and controls · test suite

## Should it be AI at all?

Decide first between automation (the system does it) and augmentation (the person does it, faster). Automate tasks people don't value doing and that the model does reliably; augment tasks people care about, are accountable for, or where errors are costly ([PAIR](https://pair.withgoogle.com/guidebook/)). Keep a non-AI path to finish the task when the model fails or is switched off.

## Disclosure

- **EU AI Act Article 50 applies since 2 August 2026**; it was not deferred. People interacting with an AI system must be told so unless it is obvious, at the latest at the first interaction, in a clear and accessible way. Synthetic audio, image, video and text must be machine-detectably marked by providers (systems already on the market have until 2 December 2026 for that part). Deployers must label deepfakes and AI-generated text published to inform the public, unless a human editorially reviews it ([Commission FAQ](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act), [Article 50](https://artificialintelligenceact.eu/article/50/)). [S]
- Design floor: a persistent, visible AI label on assistant surfaces and on generated content, announced to screen readers, not colour-only. Never let people believe they are talking to a human ([Apple](https://developer.apple.com/design/human-interface-guidelines/generative-ai)). This is a design floor, not legal advice. [S]
- Say what it can do and how well (HAX G1, G2): scope, limits, languages, and the kinds of mistakes it makes. Carbon marks AI-generated content with a consistent AI label ([Carbon for AI](https://carbondesignsystem.com/guidelines/carbon-for-ai/)). [S]

## Input

- Starter suggestions or templates for an empty prompt; show attached context ("Using: ticket #4812, 3 past orders"); state the limits; keep the prompt editable after sending and never lose it on failure. [C]
- Don't ask the model for facts it can't verify; warn where hallucination is likely ([Apple](https://developer.apple.com/design/human-interface-guidelines/generative-ai)). [S]

## Latency and streaming

- Stream text; time to first token matters more than total time. [C]
- Use specific progress text for tool steps ("Checking order 4812 against the refund policy"), not "Processing…" ([Apple](https://developer.apple.com/design/human-interface-guidelines/generative-ai)). [S]
- Stop is always available and keeps the partial output; long jobs run in the background and notify on completion. [C]
- Generated content arriving below the reading position must not shove the text people are reading; reserve space or append below. [S] (CLS, 2.2.2 for auto-updating content)
- Announce completion politely; never announce every streamed token to screen readers. [S]

## Output, control and undo

- Edit, Retry, Undo and alternatives sit next to generated output (HAX G9; Apple). Acknowledge when a correction takes effect. [S]
- Show what changed: a diff for AI edits to existing content, and version history with "revert AI edit". [C]
- Drafts, not sends: anything that leaves the product (to a customer, a repository, a payment) is a draft until a person approves it, unless the user has explicitly delegated that action. [C]

## Agent actions

When the AI acts, tier the actions by consequence and design approval to match:

| Tier | Examples | Pattern |
| --- | --- | --- |
| Read-only | Search, summarise, look up | Automatic; show sources and what was read |
| Reversible | Draft, tag, move, edit with history | Automatic or one click, with visible undo |
| Irreversible, costly or external | Send, pay, delete, merge, publish, contact a person | Show the plan; explicit confirmation naming the consequence and cost (HAX G16); never batched silently |

- Show an action plan before executing a multi-step task, and let people edit or cut steps. Editable plans improved steerability over a chat baseline without hurting ease of use ([Cocoa, CHI 2026](https://doi.org/10.1145/3772318.3791673), n=16; [Magentic-UI](https://arxiv.org/abs/2507.22358)). [E]
- **Approval prompts get rubber-stamped** like any warning: Claude Code users approve 93 % of permission prompts ([Anthropic](https://www.anthropic.com/engineering/claude-code-auto-mode)). Every unnecessary prompt cheapens the necessary ones, so batch approvals for reversible steps, stage changes with snapshots and undo, and keep each irreversible step its own decision. [E]
- **Show the effect, not the command:** the diff, the files touched, the recipients, the amount. [C]
- **Interrupt at task boundaries** (after a run, a save, a finished step), never on idle; idle often means someone is thinking ([Pu et al. 2025](https://arxiv.org/abs/2502.18658)). Stop, pause and redirect stay available throughout ([Horvitz 1999](https://doi.org/10.1145/302979.303030)). [E]
- Show cost estimates where credits or money are spent. [C]
- Log what the agent did, in plain language, where people can find and undo it. [C]

## Trust and overreliance

Microsoft's overreliance framework sets three goals: realistic mental models, signals for when to verify, and cheap verification ([Microsoft Learn](https://learn.microsoft.com/en-us/ai/playbook/technology-guidance/overreliance-on-ai/overreliance-on-ai), [literature review](https://www.microsoft.com/en-us/research/publication/overreliance-on-ai-literature-review/)). [E]

- **Mitigations can backfire.** Explanations raise trust even when wrong, and the mere presence of sources makes people trust outputs more. So make checking cheap: citations scoped to the claim, a hover preview with the quoted passage highlighted, and a visible note when no source supports a claim. [E]
- **Prefer verbal, first-person uncertainty** ("I'm not sure, but…") or highlighting of uncertain spans over raw percentages; model self-reported confidence is poorly calibrated, so show a number only if it is calibrated. [E] ([Kim et al. FAccT 2024](https://doi.org/10.1145/3630106.3658941))
- **Cognitive forcing** (deciding before seeing the AI's answer, or a deliberate review step) reduces overreliance, but people like it least ([Buçinca et al. 2021](https://www.eecs.harvard.edu/~kgajos/papers/2021/bucinca21trust.pdf)). Use it where errors are costly. [E]
- **Put the facts beside the draft.** An AI reply drafted from a ticket sits next to the ticket facts it used, so the reviewer compares rather than trusts. [C]

## Errors and refusals

- Say what failed in plain language and offer the next step, including the non-AI path. [S]
- Refusal copy coaches: "I can't change prices. Try asking for a discount code instead." [S] (Apple)
- A report-a-problem affordance on every output. [C]

## Feedback, memory and controls

- Voluntary, unobtrusive thumbs up/down with optional reason chips, and say what happens to the feedback (is it used for training?) (HAX G15; Apple). [S]
- Memory is visible and editable; offer an incognito mode; say what goes to a server and whether inputs train models. [S]
- A global off switch for AI features (HAX G17), and notice when the model or its behaviour changes (G18). [S]

## Test suite

Build a red-team prompt set as a regression suite: vague, out-of-scope, sensitive, adversarial (prompt injection through user content), very long, non-English, and empty. Measure task accuracy *with* the AI, not only satisfaction, because overreliance shows up as confident wrong answers people accept.
