# Content: words are interface

Most product-UI copy is labels, buttons, errors, empty states and confirmations. Write them as part of the design, not after it, and with real strings, because copy length changes the layout.

Contents: plain language · names and labels · buttons and the verb chain · errors · empty states and confirmations · voice and tone · casing and characters · checks

## Plain language

- Plain English is mandatory on GOV.UK. In their legal-document study 80 % preferred plain sentences, and the preference *grew* with education and expertise ([GOV.UK](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/writing-guidelines/clear-language/), [GDS](https://gds.blog.gov.uk/2014/02/17/guest-post-clarity-is-king-the-evidence-that-reveals-the-desperate-need-to-re-think-the-way-we-write/)). Experts want scannable, jargon-free text too ([NN/g](https://www.nngroup.com/articles/plain-language-experts/)). [E]
- Short common words, active voice, sentences under about 25 words. For Dutch audiences, B1 is the common government target. Readability formulas screen word and sentence length; they don't measure comprehension, so don't target a score. [C]
- plainlanguage.gov now redirects to [digital.gov](https://digital.gov/guides/plain-language); the federal guidelines are kept by the [Center for Plain Language](https://centerforplainlanguage.org/the-federal-plain-language-guidelines-are-missing/).

## Names and labels

- **Name things by the user's goal, not the system's internals.** People manage notifications, not webhook configuration. Enum names, HTTP codes, table names and "null" never leak into the UI. [C]
- **One term per concept, everywhere.** If the product says "workspace" on one screen and "organisation" on the next, people assume they are different things. Keep a glossary; load `domain-language` for a project vocabulary. [C]
- **Labels say what to enter** ("Email address"), hints say why or in what format, placeholders never carry either. [S]
- **Headings describe the area or what can be done in it**, so the page reads as an outline from headings alone. [E] ([NN/g layer-cake scanning](https://www.nngroup.com/articles/layer-cake-pattern-scanning/))

## Buttons and the verb chain

- **Verb + object, predicting the result:** "Send invoice", "Delete 3 files", "Pay €42,00". Never OK, Yes, Submit or Continue when a specific verb exists. GOV.UK uses "Continue" only for moving through question pages. [S]
- **One verb through the flow.** The button that says "Publish" produces "Published" and an item marked "Published", not "Submit" → "Success" → "Live". The dialog title and its primary button use the same verb. [C]
- **Ellipsis for commands that need more input** ("Rename…") and for in-progress states ("Saving…"). [C]
- **Destructive labels name the loss:** "Delete workspace", with the safe option labelled "Keep workspace", not "Cancel" when cancel is ambiguous. [C]

## Errors

An error message answers three questions in the user's words: what happened, why (when it helps), and what to do now ([NN/g error-message guidelines](https://www.nngroup.com/articles/error-message-guidelines/)). [E]

| Bad | Better | Why |
| --- | --- | --- |
| Invalid input | Enter a date in the past, like 27 3 1990 | Says how to fix it |
| This field is required | Enter your email address | Instruction, in the question's words ([GOV.UK](https://design-system.service.gov.uk/components/error-message/)) |
| Something went wrong | We couldn't save your changes because the connection dropped. Your text is still here. Try again. | Cause, reassurance, next step |
| Error 409 | Someone else changed this invoice while you were editing. Review their version; your text is kept below. | Plain cause, data kept |
| You entered the wrong password | That email and password don't match. Reset your password | No blame; a way out |
| Oops! | (omit) | No jokes in failures |

- Put the message next to the field and summarise it at the top on submit, with identical wording ([patterns.md](patterns.md#forms)). [S]
- No "please", "sorry", "invalid", "illegal", "forbidden" or codes alone. [S]
- Never blame the user; keep their input; offer the fix inline where you can (a "Did you mean gmail.com?" suggestion). [E]
- System errors name what still works ("Your other invoices are safe") and how to get help. [C]

## Empty states and confirmations

- **First use:** what this area is for, and one primary action. "No invoices yet. Create your first invoice or import from CSV." [C]
- **No results:** echo the query and the filters, then offer a way out. "No invoices match 'acme' in Paid. Search all statuses." [E]
- **Cleared:** quiet completion. "All caught up." [C]
- **Success:** state what happened and offer the next step or undo. "Invoice sent to finance@client.nl. Undo." [C]
- **Irreversible confirmation:** name the object and consequence in the title, and put the verb on the button. "Delete 'Q3 report'? Its 14 comments will be deleted too. This can't be undone." [Delete report] [Keep report]. [C]

## Voice and tone

Keep one voice and adjust the tone to the reader's state of mind: clear beats entertaining, and errors, failures and money get no jokes ([Mailchimp voice and tone](https://styleguide.mailchimp.com/voice-and-tone/)). In product UI, utility copy beats marketing copy: say what the area is and what can be done there. [C]

## Casing and characters

- **Sentence case** for labels, buttons and headings. This is a convention shared by Material, Apple, Fluent and GOV.UK and easier to apply consistently; the readability evidence over title case is weak ([USAGov](https://www.usa.gov/blog/2023/09/making-the-case-for-sentence-case)). Running text in ALL CAPS is reliably slower to read. [C][E]
- Use the real characters: `…`, curly quotes, en dash for ranges, `×` for dimensions, non-breaking space before units. [C]
- Format numbers, dates, currencies and lists with `Intl`; never concatenate translated fragments, because word order differs by language; pluralise with ICU messages or `Intl.PluralRules` ([MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/PluralRules)). [S]
- Write `translate="no"` on brand names and code tokens. [C]

## Checks

Grep the UI strings (the i18n files are ideal) for: Submit, OK, Click here, Invalid, Oops, "Please", "Something went wrong", raw codes, internal names, `(s)` plurals, Title Case mixed with sentence case, and several words for one concept. Check that every error string has a recovery path and every empty state has a next action. `scripts/ui_scan.py` flags the most common of these.
