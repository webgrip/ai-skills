# Ad law and platform lines for provocative dev-tool Shorts (EU, Dutch detail)

**Not legal advice.** Where it says "lawyer", ask a Dutch IE/reclamerecht lawyer
before you publish. Labels: **LAW** statute or case · **REG** regulator or self-regulator ruling/guidance ·
**OFF** platform policy · **ANEC** commentary/press · **GAP** no primary source found.
Every URL below was opened during this research.

## 1. EU and Dutch law

### 1.1 Exaggeration is allowed, false facts are not
- **LAW** UCPD 2005/29/EC Art. 5(3): the directive is "without prejudice to the common and legitimate
  advertising practice of making exaggerated statements or statements which are not meant to be taken
  literally". Art. 6(1): a practice is misleading if it contains false information or deceives the average
  consumer, *even if factually correct*. Art. 7(2): hiding commercial intent is a misleading omission.
  https://eur-lex.europa.eu/eli/dir/2005/29/oj
- **LAW** Dutch implementation, BW 6:193b lid 4 (in the code since the 2008 implementation; the link is the 2026-07-16 consolidated text): "De gangbare en
  rechtmatige reclamepraktijk waarbij overdreven uitspraken worden gedaan of uitspraken die niet letterlijk
  dienen te worden genomen, maken een reclame op zich niet oneerlijk." 6:193c lists misleading points,
  including "van het gebruik te verwachten resultaten" (results to be expected from use).
  https://wetten.overheid.nl/BWBR0005289/2026-07-16/0/Boek6/Titeldeel3/Afdeling4/Artikel194a
- **LAW** Scope: 6:193a defines *consument* as a natural person not acting for a trade. Most dev-tool buyers are
  businesses, so the B2B rule matters: **BW 6:194** makes a misleading public statement unlawful towards
  another business, e.g. about "eigenschappen of gebruiksmogelijkheden" (properties, uses), "technische
  bevindingen of statistische gegevens" (sub f). Same page as above. Solo developers self-hosting for
  hobby use can be consumers, so both regimes can apply to one Short.
- **REG** ACM (Dutch consumer authority): "In reclame mag u overdrijven of spelen met taal. Maar uw claims
  moeten wel kloppen." https://www.acm.nl/nl/verkoop-aan-consumenten/oneerlijke-handelspraktijken
- **ANEC/case** Verkade "Als lekkerste getest" (Vzr. Rb. Amsterdam, reported 2013-10-11): a claim that
  *sounds* factual ("tested as") is not saved by the puffery defence; Verkade admitted no test existed.
  The judge also read it as an implicit comparison with other brands.
  https://www.dirkzwager.nl/kennis/artikelen/reclame-uiting-als-lekkerste-getest-verboden
- Practical reading: "our agents are 10x engineers who never sleep" in an absurd sketch = puffery.
  "Ships 40% more PRs" / "benchmarked faster than X" / "zero bugs" = a factual claim you must be able to prove.

### 1.2 When a joke about "other AI tools" becomes comparative advertising
- **LAW** Directive 2006/114/EC Art. 2(c): comparative advertising = any ad that "explicitly or by
  implication identifies a competitor". Art. 4 conditions are cumulative: (d) no discrediting/denigrating;
  (f) no unfair advantage of a competitor's trade-mark reputation; (g) no presenting your product as an
  imitation or replica. https://eur-lex.europa.eu/eli/dir/2006/114/oj
- **LAW** BW 6:194a mirrors this: "uitdrukkelijk of impliciet worden genoemd" (lid 1); lid 2(e) may not
  "de goede naam schaadt van of zich niet kleinerend uitlaat over" a competitor; (c) must compare objectively
  on verifiable features; (g) no unfair advantage of reputation; (h) no imitation. Same wetten.overheid.nl URL.
- **LAW** CJEU C-381/05 *De Landtsheer* (2007-04-19): referring only to a *type* of product can still be
  comparative advertising if a specific undertaking can be identified; how many competitors are identifiable
  "is of no relevance". https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62005CJ0381
- **REG** Nederlandse Reclame Code (NRC) art. 13: comparative advertising allowed only under conditions a–h;
  sub e bans disparaging competitors' brands. https://www.reclamecode.nl/nrc/
- Practical test: "AI tools that hallucinate your prod DB away" aimed at the category = fine. A recognisable
  purple logo, a product's UI chrome, its mascot, a sound-alike product name or "that one IDE everyone uses"
  with obvious visual cues = identifiable competitor → every 6:194a condition applies, and mockery is
  close to the "kleinerend" line by definition.

### 1.3 Nederlandse Reclame Code (self-regulation, Stichting Reclame Code)
- **REG** NRC art. 2: advertising must respect "de wet, de waarheid, de goede smaak en het fatsoen";
  art. 4: not "nodeloos kwetsend" (needlessly hurtful); art. 8: misleading; **art. 11: advertising must be
  clearly recognisable as advertising** "door opmaak, presentatie, inhoud of anderszins".
  https://www.reclamecode.nl/nrc/
- **REG** College van Beroep RCC, dossier 2016/00193 CvB (Suitsupply, 2016-05-18): on taste and decency the
  bodies are restrained ("terughoudend"); context, medium and the effect on the public all count. The
  "absurdistische karakter" of the ad weighed in its favour and the complaint was rejected on appeal. The
  College also noted that purely commercial speech gets *less* free-speech margin than political speech.
  https://www.boek9.nl/system/files/B92016/B920160518_CvB_RCC_Suitsupply_00193.pdf
- **REG** RCC rulings are self-regulation (non-binding recommendations), but they are public and get press.
- **GAP** No RCC ruling found on humour in **tech/B2B/software** ads. Search the RCC database
  (reclamecode.nl/uitspraken) for "software", "AI" before a campaign that names anyone.

### 1.4 Disclosure on your own channels (influencer rules)
- **REG** Reclamecode Social Media & Influencer Marketing (RSM): the 2026 revision note (DDMA, June 2026)
  proposes that a disclosure is also required for "reclame voor een eigen merk" and for UGC-creator posts on
  their own channel; no hashtag is needed but the wording must clearly signal advertising; virtual
  influencers' account managers are responsible. The current RSM dates from 2022-07-01; I could not confirm
  the 2026 changes are in force (**GAP**).
  https://www.reclamecode.nl/media/cflhdop3/nota-van-toelichting-wijzigingen-rsm-2026-def.pdf
- **LAW** DSA (Reg. 2022/2065) Art. 26(2): platforms must offer a function to declare that content "is or
  contains commercial communications", and then label it for viewers. Art. 26(1) covers paid ads (who paid,
  why you see it). The duty sits on the platform; the user's part is to tick the box.
  https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32022R2065
- Practical: a company channel's own Shorts are obviously advertising (NRC art. 11 satisfied by context). The
  risk is the *founder's personal* account or a friendly dev creator posting "just a funny clip" about
  the product without saying they built/were asked to post it.

### 1.5 Using other brands' names and logos in a joke
- **LAW** Trade Mark Directive (EU) 2015/2436 Art. 10(2)(c): a reputed mark is protected where use "without
  due cause takes unfair advantage of, or is detrimental to" its distinctiveness or repute, even for
  dissimilar goods. Art. 10(3)(f): a mark owner can stop use in comparative ads that break 2006/114.
  Art. 14(1)(c) allows referential use (naming the owner's product), but only (Art. 14(2)) "in accordance
  with honest practices". Recital 27: use "for the purpose of artistic expression should be considered as
  being fair", again subject to honest practices. https://eur-lex.europa.eu/eli/dir/2015/2436/oj
- **LAW** CJEU C-487/07 *L'Oréal v Bellure* (2009-06-18): "riding on the coat-tails" of a reputed mark is
  unfair advantage without any confusion needed; saying your product is an imitation is unlawful.
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62007CJ0487
- Reading: referential naming ("works with GitHub", "runs Claude Code") in a factual line = generally OK.
  A competitor's **logo** in a sketch, especially being mocked, is the most attackable use: artistic/parody
  fair use is untested for *advertising*, where the purpose is commercial. Lawyer before any logo.

### 1.6 Copyright: parody, memes and famous ads
- **LAW** InfoSoc 2001/29/EC Art. 5(3)(k) allows an exception "for the purpose of caricature, parody or
  pastiche", bounded by the Art. 5(5) three-step test. https://eur-lex.europa.eu/eli/dir/2001/29/oj
- **LAW** NL: Auteurswet art. 18b: not infringing "in het kader van een karikatuur, parodie of pastiche
  mits het gebruik in overeenstemming is met hetgeen naar de regels van het maatschappelijk verkeer
  redelijkerwijs geoorloofd is" (version in force from 2026-01-01). https://wetten.overheid.nl/BWBR0001886/
- **LAW** CJEU C-201/13 *Deckmyn* (Grand Chamber, 2014-09-03): parody must "evoke an existing work, while
  being noticeably different from it" and be "an expression of humour or mockery"; national courts must
  strike a fair balance with the rightholder, who may object to association with e.g. a discriminatory message.
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62013CJ0201
- **LAW/REG** CJEU C-590/23 *Pelham II* (Grand Chamber, 2026-04-14): "pastiche" is an autonomous concept
  needing "an objectively recognisable artistic or creative dialogue with the source material"; it is not a
  general licence for appropriation. (Reported by the EU IP Helpdesk.)
  https://intellectual-property-helpdesk.ec.europa.eu/news-events/news/cjeu-grand-chamber-rules-music-sampling-and-pastiche-first-cjeu-hearing-generative-ai-and-copyright-2026-04-24_en
- **ANEC/GAP** Whether parody covers a *commercial* ad parodying another *ad* is not settled by these
  sources. Parodying the *format* (an Apple-keynote cadence, a "Mac vs PC" two-hander) uses no copyrighted
  expression; reusing the original footage, music or exact frames does. Recreate, never rip.
- **LAW** Portrait right, Auteurswet art. 21: publishing a portrait not commissioned by the person is not
  allowed where "een redelijk belang van den geportretteerde" opposes it. Dutch case law treats commercial
  exploitation of a recognisable person as such an interest (**ANEC**, not verified here). Same URL.

### 1.7 EU AI Act Art. 50 (synthetic voices and video)
- **LAW** Reg. 2024/1689 Art. 3(60): a "deep fake" is AI-generated or manipulated image/audio/video that
  "resembles existing persons, objects, places, entities or events and would falsely appear to a person to
  be authentic or truthful". https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=OJ:L_202401689
- **LAW** Art. 50(4): *deployers* of AI that makes a deep fake "shall disclose that the content has been
  artificially generated or manipulated". For "evidently artistic, creative, satirical, fictional or analogous"
  work the duty shrinks to disclosure "in an appropriate manner that does not hamper the display or enjoyment
  of the work". Art. 50(5): disclose "clear and distinguishable", at the latest at first exposure.
  Art. 50(2): *providers* (ElevenLabs, video models) must machine-mark output.
- **LAW** Dates: Art. 113 — applies from **2 August 2026**. The AI Omnibus, **Reg. (EU) 2026/1744**,
  adds only a grace period for Art. 50(2) marking by providers whose systems were on the market before
  2 Aug 2026: comply "by 2 December 2026". Deployer duties in Art. 50(4) are not deferred.
  https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng
- **LAW** Art. 99(4)(g): Art. 50 breaches up to €15M or 3% of turnover; Art. 99(6): for SMEs/start-ups,
  whichever is *lower*. Same AI Act URL.
- Reading: an invented AI narrator voice that does not resemble a real person is not a deep fake under
  Art. 3(60). A cloned or sound-alike voice of a real person (a CEO, a famous YouTuber, a politician) is, and
  must be disclosed even in satire. A one-line "AI voice" credit plus the platform label is the cheap habit.

### 1.8 "AI washing" (claims about AI capabilities)
- **REG (US)** FTC "Operation AI Comply" (2024-09-25): five actions, incl. DoNotPay's "world's first robot
  lawyer" ($193,000); Chair Khan: "there is no AI exemption from the laws on the books".
  https://www.ftc.gov/news-events/news/press-releases/2024/09/ftc-announces-crackdown-deceptive-ai-claims-schemes
- **GAP (EU/NL)** No ACM or EU-level AI-washing enforcement action or guidance found (ACM pages searched).
  The general rule in 1.1 applies: capability claims ("autonomous", "reviews its own PRs", "replaces a
  team") are factual claims about "voornaamste kenmerken" / "te verwachten resultaten" (6:193c, 6:194).
  US FTC enforcement only matters if you target US buyers.

## 2. Platform rules

- **OFF** YouTube spam/deceptive practices: bans "maliciously misleading titles, thumbnails, descriptions, or
  imagery"; applies to unlisted content too; strikes, 3 in 90 days = termination.
  https://support.google.com/youtube/answer/2801973?hl=en
- **ANEC** "Egregious clickbait" crackdown announced 2024-12-18, India first: titles/thumbnails promising
  what the video doesn't deliver ("The president steps down"), especially news; removal without strike at
  first. https://techcrunch.com/2024/12/18/youtube-says-it-will-start-cracking-down-on-videos-with-clickbait-titles-in-india
  **GAP**: no primary source found confirming EU rollout by Oct 2026; assume it can apply anywhere.
- **OFF** YouTube altered/synthetic content: disclose realistic AI content that makes a real person say/do
  something, alters real events, or generates a realistic scene. *No* disclosure for clearly unrealistic or
  animated content, script/title help, or cloning **your own** voice. Repeated non-disclosure → forced label,
  removal or YPP suspension. https://support.google.com/youtube/answer/14328491?hl=en
- **OFF** YouTube harassment: no threats, brigading, "prolonged insults" based on intrinsic attributes;
  exceptions for scripted satire/comedy and for debate about powerful people (e.g. CEOs of major
  multinationals), but "not a pass to harass someone". https://support.google.com/youtube/answer/2802268?hl=en
- **OFF** YouTube paid promotion box: for product placement, sponsorship or endorsement; adds an on-video
  label. https://support.google.com/youtube/answer/154235?hl=en (own-brand channel not addressed: **GAP**).
- **OFF** YouTube Audio Library: tracks can be used in monetised videos and won't get Content ID claims;
  CC tracks need credit in the description; use off YouTube not covered.
  https://support.google.com/youtube/answer/3376882?hl=en
- **OFF** TikTok Community Guidelines (2026-H2 version): "label AI-generated or significantly edited content
  that shows realistic-looking scenes or people"; no AIGC that misleads on public matters or harms
  individuals; likeness includes voice. https://www.tiktok.com/community-guidelines/en/integrity-authenticity
- **OFF** TikTok Commercial Music Library: "Commercial Sounds are the only sounds made available on TikTok
  for Commercial Uses"; business users get no rights to trending non-CML sounds and carry the claims;
  CML tracks may not be used off TikTok ("posting videos on third party digital platforms" needs rightsholder
  licences). https://www.tiktok.com/legal/page/global/commercial-music-library-user-terms/en
- **OFF** LinkedIn Ads Policy (paid ads only): claims "must have factual support"; no "deceptive or
  inaccurate claims about competitive products"; no third-party trademarks "unless express permission has
  been granted"; not "hateful, vulgar, sexually suggestive or violent"; LinkedIn may reject any ad.
  https://www.linkedin.com/legal/ads-policy

## 3. Decisions — provocative dev-tool Shorts made in NL

### GREEN — fine as a default
1. Absurd, obviously-not-literal hype ("we put 400 agents in a swarm and it filed for a union") — puffery
   [LAW 6:193b lid 4, UCPD 5(3); REG ACM].
2. Mocking **buzzwords and the category** ("agentic", "10x", "swarms", "vibe coding") without an
   identifiable company [LAW 6:194a lid 1 read with De Landtsheer — no identifiable competitor = not comparative].
3. Self-mockery of the product, the founder, developers in general, on-call pain [REG NRC art. 2/4; Suitsupply
   CvB on absurdism].
4. Factual referential naming in captions: "works with Forgejo/GitHub", "runs Claude Code" [LAW TMD Art. 14(1)(c)].
5. Original music, YouTube Audio Library tracks on YouTube, TikTok CML tracks on TikTok only [OFF].
6. An invented, clearly fictional AI narrator voice, with an "AI voice" credit in the description anyway [LAW AI Act
   Art. 3(60), 50(4); OFF YouTube synthetic].

### AMBER — allowed, but check before posting
7. Any **number** or capability claim, even inside a joke ("cuts review time 60%", "runs a team for €3/day"):
   keep the evidence (run logs, method) on file before publishing [LAW 6:193c, 6:194 sub f; REG ACM; Verkade].
8. "Other AI tools" jokes with a recognisable visual cue (colour, UI, mascot, sound-alike name): now
   comparative → must be objective, not disparaging, no reputation-riding [LAW 6:194a lid 2(c)(e)(g); 2006/114 Art. 4;
   REG NRC art. 13]. Get a lawyer's read for the first such Short.
9. Parodying a famous ad's *format* or a meme template: recreate it yourself; keep it "noticeably different"
   and humorous [LAW Deckmyn; Auteurswet 18b; Pelham II]. Commercial parody of another ad is untested [GAP].
10. Founder's personal account or a friend's dev channel posting the product Shorts: say plainly it's your/their
    product or a paid/asked post [REG NRC art. 11, RSM 2026 revision; LAW UCPD Art. 7(2), DSA 26(2)].
11. Titles/thumbnails: provocative is fine, but the video must deliver what the title promises [OFF YouTube
    spam policy; ANEC clickbait crackdown].
12. Realistic AI footage (fake office, fake "team") → tick YouTube's altered-content box and TikTok's AIGC label
    [OFF YouTube 14328491; OFF TikTok].
13. Running a Short as a **paid** LinkedIn ad: stricter than organic — no third-party marks without permission,
    claims need support [OFF LinkedIn Ads Policy].

### RED — don't
14. A competitor's **logo**, product footage or UI screenshot being mocked or broken [LAW TMD Art. 10(2)(c), 10(3)(f);
    L'Oréal v Bellure; 6:194a lid 2(e)(g); OFF LinkedIn, TikTok IP rule].
15. A cloned or sound-alike voice/face of a real person (a tech CEO, a famous dev YouTuber) — deep fake under
    the AI Act, platform violation, portrait-right claim; satire narrows the label but does not remove it, and
    the platforms still restrict it [LAW AI Act 3(60), 50(4), 99; Auteurswet 21; OFF YouTube, TikTok].
16. Trending TikTok sounds or chart music in a business-account video, or reusing a CML track on YouTube/LinkedIn
    [OFF TikTok CML terms].
17. Fake factual framing: "benchmarked", "tested", "rated #1", fake testimonials or fake customer logos —
    the puffery defence does not cover them [LAW 6:193c, 6:194 sub f; Verkade; REG FTC AI Comply (Rytr, DoNotPay)].
18. Jokes that target a named individual (not a company or the hype), protected traits, or that encourage
    piling on [OFF YouTube harassment; REG NRC art. 4; Deckmyn on discriminatory association].
19. Clickbait that borrows news ("OpenAI just shut down") to pull views [OFF YouTube spam; ANEC clickbait].

### Lawyer before publishing
- the first Short that makes any competitor identifiable (items 8, 14);
- any campaign with a real person's likeness or voice (15);
- any parody of a specific famous ad (9).

Note: Dutch rules here mostly mirror EU rules, so the same Short is broadly safe across the EU; the RCC and
ACM are the Dutch bodies a competitor or viewer would complain to.
