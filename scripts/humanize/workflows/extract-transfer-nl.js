export const meta = {
  name: 'ai-tells-dutch',
  description: 'Build the Dutch catalog: extract Dutch sources, transfer the English catalog, add a translationese layer, merge, verify, consolidate',
  phases: [
    { title: 'Extract', detail: 'Dutch articles, German sister sources, translationese layer' },
    { title: 'Transfer', detail: 'every English entry: transfers, Dutch form, or n/a' },
    { title: 'Merge', detail: 'two halves, in Dutch, self-verified against human Dutch' },
    { title: 'Consolidate', detail: 'catalog-nl.json' },
  ],
}

const S = '/Users/ryangrippeling/projects/webgrip/webgrip-ai-skills/scripts/humanize'
const CATS = ['vocabulary', 'syntax', 'rhetoric', 'structure', 'punctuation-format', 'content', 'artifacts', 'translationese']

const CAT_GUIDE = `Categorieën (precies één per patroon):
- vocabulary: losse woorden of vaste frasen (cruciaal, naadloos, "het is belangrijk om op te merken", "in de snel veranderende wereld van")
- syntax: zinsconstructies (niet X maar Y, "niet alleen ... maar ook", drieslag, deelwoordketens, "fungeert als" in plaats van "is", valse reeksen "van X tot Y", anafoor, retorische zelfvraag, paarsgewijze fragmenten "Snel. Simpel.")
- rhetoric: argumentatieve zetten en toon (dubbelepunt-onthulling, aforistische slotzin, valse spanning "Hier komt het", opgeblazen belang, zelfrangschikking "het belangrijkste", meta-bewegwijzering, reflexief afzwakken, vleierij, oprechtheidsvlag "eerlijk gezegd", correctieve draai, complimentsandwich)
- structure: alinea- en documentvorm (gelijke alinealengte, lijstje-als-proza, fractale samenvattingen, vijfparagrafenopstel, koppen als onderwerp, vetgedrukte bullet-openers, inline-kopjes, "Kortom"-slot, "ondanks uitdagingen"-einde, de LinkedIn-slotvraag)
- punctuation-format: gedachtestreepjes, aanhalingstekens, emoji, vet, hoofdletters in titels, pijltjes, koppen, tabellen, komma voor "en"
- content: inhoudelijke gebreken (vage bronnen "experts zeggen", reclametaal, opgeblazen betekenis, verzonnen eigen ervaring, kennisgrensdisclaimers, geen eerstehands detail, twee-kanten-opvulling, bedachte conceptlabels)
- artifacts: chatbotresten en machinesporen ("Ik hoop dat dit helpt", "als AI", markdown op plekken zonder markdown, citatieresten, utm_source=chatgpt.com, plaatshouders "[naam invullen]", "Interessant perspectief, Piet!")
- translationese: constructies die alleen bestaan omdat Engelsvormige tekst in het Nederlands werd gegenereerd (Engelse woordvolgorde, leenvertalingen van idioom, Engelse interpunctieconventies, Engelse titelhoofdletters, "je" en "u" door elkaar, onvertaalde termen, mechanisch parallellisme uit het Engels)`

const NL_ENTRY = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    naam: { type: 'string' },
    definitie: { type: 'string' },
    cues: { type: 'array', items: { type: 'string' } },
    regex: { type: 'array', items: { type: 'string' } },
    voorbeelden: { type: 'array', items: { type: 'object', properties: { voor: { type: 'string' }, na: { type: 'string' } }, required: ['voor', 'na'] } },
    ernst: { type: 'string', enum: ['always', 'cluster', 'context'] },
    herkomst: { type: 'string', enum: ['nl-bron', 'transfer', 'translationese', 'elicitatie', 'baseline'] },
    en_id: { type: 'string' },
    bronnen: { type: 'array', items: { type: 'string' } },
    samengevoegd_uit: { type: 'array', items: { type: 'string' } },
    valse_positieven: { type: 'string' },
  },
  required: ['id', 'naam', 'definitie', 'cues', 'regex', 'voorbeelden', 'ernst', 'herkomst', 'en_id', 'bronnen', 'samengevoegd_uit', 'valse_positieven'],
}
const RAW = {
  type: 'object',
  properties: {
    bron: { type: 'string' },
    patronen: { type: 'array', items: { type: 'object', properties: {
      naam: { type: 'string' }, categorie: { type: 'string', enum: CATS }, definitie: { type: 'string' },
      cues: { type: 'array', items: { type: 'string' } },
      voorbeelden: { type: 'array', items: { type: 'object', properties: { voor: { type: 'string' }, na: { type: 'string' } }, required: ['voor'] } },
      ernst: { type: 'string', enum: ['always', 'cluster', 'context'] },
      herkomst: { type: 'string', enum: ['nl-bron', 'transfer', 'translationese', 'elicitatie', 'baseline'] },
      en_id: { type: 'string' },
      notities: { type: 'string' },
    }, required: ['naam', 'categorie', 'definitie', 'cues', 'voorbeelden', 'ernst', 'herkomst', 'en_id'] } },
    dekking: { type: 'string' },
  },
  required: ['bron', 'patronen', 'dekking'],
}
const MERGED_HALF = { type: 'object', properties: { categories: { type: 'array', items: { type: 'object', properties: { categorie: { type: 'string' }, entries: { type: 'array', items: NL_ENTRY } }, required: ['categorie', 'entries'] } }, rapport: { type: 'string' }, regex_verwijderd: { type: 'integer' } }, required: ['categories', 'rapport', 'regex_verwijderd'] }
const DEDUP = { type: 'object', properties: { merged: { type: 'integer' }, moved: { type: 'integer' }, total: { type: 'integer' }, per_category: { type: 'object', additionalProperties: { type: 'integer' } }, notes: { type: 'string' } }, required: ['merged', 'moved', 'total', 'notes'] }

const NL_GROUPS = [
  { id: 'nl-artikelen', files: ['frankwatching-2024-ai-woorden.txt', 'rhinoz-jeukwoorden.txt', 'somc-20-woorden.txt', 'contentkantoor-ai-woorden.txt', 'hulz-herkennen.txt', 'aikundig-herkennen.txt', 'digiwijzer-herkennen.txt', 'bikkelhart-8-signalen.txt', 'rubens-zonder-technologie.txt', 'b2bmarketeers-herkennen.txt', 'donnavandeven-herkennen.txt', 'opdebeeck-herkennen.txt', 'promptmaster-opschonen.txt', 'aislopchecker.txt', 'aitekstdetector.txt', 'frankwatching-2026-linkedin.txt', 'frankwatching-2023-nederlandse-taal.txt', 'linkai-raakt-niet.txt', 'onzetaal-chatgpt-taalvragen.txt', 'pcactive-denkwerk.txt', 'vu-alp-gids-nl.txt', 'jouwcopiloot-nl.txt'], hint: 'Tweeëntwintig Nederlandse bronnen: AI-woordenlijsten uit de contentmarketing (jeukwoorden, 20 woorden), herkenningsgidsen (Angelsaksische zinsbouw, komma voor "en", gedachtestreepje op zijn Engels, drieslag), LinkedIn-slop (aislopchecker beschrijft zijn eigen patroonlijst), Onze Taal over ChatGPT als vertaald Engels, de VU-gids voor docenten en een Nederlandse vertaling van tien Wikipedia-patronen. De bestanden zijn klein (5 tot 16 KB); lees ze allemaal.' },
]

function nlExtractPrompt(g) {
  const paths = g.files.map(f => `${S}/nl/${f}`).join(' ; ')
  return `Je bent een extractor in een fan-out die een Nederlandse catalogus van AI-schrijfpatronen bouwt. Bron: "${g.id}". ${g.hint}

Lees elk bestand volledig (cat of sed -n in stukken van hoogstens 250 regels): ${paths}

Inventariseer ELK afzonderlijk patroon dat de bron noemt. Vat niet samen, sla niets over. Per patroon:
- naam: de naam die de bron geeft of een korte Nederlandse naam
- categorie: ${CAT_GUIDE}
- definitie: één of twee Nederlandse zinnen, precies genoeg voor een regex-schrijver of herschrijver
- cues: letterlijke Nederlandse woorden of frasen uit de bron, allemaal (bij woordenlijsten: elk woord)
- voorbeelden: de voor/na-voorbeelden van de bron letterlijk; alleen een "voor" als er geen "na" is
- ernst: always (nooit acceptabel), cluster (alleen een tell bij opeenhoping), context (in sommige registers prima)
- herkomst: nl-bron
- en_id: leeg laten ("")
- notities: valse positieven, frequenties, alles wat de bron toevoegt

dekking: wat je las, wat je bewust wegliet en waarom.

Schrijf het volledige resultaat ook als JSON naar ${S}/out/nl-extract-${g.id}.json. Geef het gestructureerde resultaat terug.`
}

const DE_PROMPT = `Je bent een extractor voor een Nederlandse catalogus van AI-schrijfpatronen. Bronnen: de Duitse Wikipedia-pagina "Anzeichen für KI-generierte Inhalte" (wikitext) op ${S}/nl/de-wikipedia-anzeichen-ki.wikitext (161 regels; lees alles) en het overzicht van de 72 patronen van humanizer-de op ${S}/repos/humanizer-de/docs/muster-katalog.md (155 regels; lees alles; de volledige catalogus in references/patterns.md hoef je niet te lezen, raadpleeg hem alleen met grep als een naam onduidelijk is).

Het Duits is de zustertaal: elk Duits patroon heeft meestal een Nederlandse tegenhanger. Inventariseer elk patroon dat de pagina noemt en geef per patroon de NEDERLANDSE vorm: naam in het Nederlands, definitie in het Nederlands, cues als Nederlandse woorden/frasen (vertaal de Duitse cues naar wat een Nederlands taalmodel daadwerkelijk schrijft; laat cues weg die in het Nederlands niet voorkomen en zeg dat in notities), voorbeelden in natuurlijk Nederlands (voor en na). categorie uit: ${CAT_GUIDE}
herkomst: nl-bron. en_id: "". ernst per patroon. Sla de Wikipedia-specifieke onderdelen (Vorlagen, Kategorien, Bearbeitungszusammenfassungen) over tenzij ze een algemeen machinespoor beschrijven; noem dat in dekking.

Schrijf het resultaat ook als JSON naar ${S}/out/nl-extract-duits.json en geef het terug.`

function transferPrompt(cats) {
  return `Je vertaalt de Engelse catalogus van AI-schrijfpatronen naar Nederlandse patronen. Jouw categorieën: ${cats.join(', ')}. Lees de canonieke Engelse entries van die categorieën uit ${S}/out/catalog-en.json (sleutel categories["<categorie>"]; print per categorie alleen id, name, definition, cues, severity, scope en één voorbeeld met python3 -c, zodat je niet verdrinkt). Beslis per entry:
1. Transfereert het mechanisme naar het Nederlands? (De meeste structurele patronen wel: negatief parallellisme, drieslag, dubbelepunt-onthulling, gelijke alinealengtes.)
2. Wat is de NEDERLANDSE vorm? Schrijf Nederlandse cues zoals een Nederlands taalmodel ze echt produceert (niet letterlijk vertaald Engels dat niemand schrijft; "delve" wordt "duiken in", "in today's fast-paced world" wordt "in de snel veranderende wereld van vandaag", "It's not X, it's Y" wordt "Het is geen X, het is Y" / "Niet X, maar Y" / "X, geen Y"). Geef Nederlandse regex (Python re, kleine letters, \\b-grenzen, strak genoeg om gewone Nederlandse proza niet te raken; JSON-escaped backslashes). Schrijf voor/na-voorbeelden in natuurlijk Nederlands (kort, één of twee zinnen; het "na" bevat zelf geen tell).
3. Of: niet van toepassing in het Nederlands (zeg waarom in notities, en geef het patroon toch terug met lege cues zodat de merge het bewust kan schrappen).

Per patroon: naam (Nederlands), categorie (zelfde als Engels tenzij het in het Nederlands ergens anders hoort), definitie (Nederlands), cues, regex, voorbeelden, ernst, herkomst: transfer, en_id: het Engelse id (verplicht), notities.
${CAT_GUIDE}

Schrijf het resultaat ook als JSON naar ${S}/out/nl-transfer-${cats[0]}.json en geef het terug.`
}

const TRANSLATIONESE_PROMPT = `Je bouwt de translationese-laag van een Nederlandse catalogus van AI-schrijfpatronen: constructies die alleen bestaan omdat een taalmodel Engelsvormige tekst in het Nederlands genereert. Dit is de laag die geen Engelse bron heeft en die de Nederlandse bronnen maar half dekken.

Lees eerst de methode van im-not-ai voor het Koreaans (translationese als aparte laag, mechanisch parallellisme, post-editese): ${S}/repos/im-not-ai/docs/en/taxonomy.md en ${S}/repos/im-not-ai/docs/en/quick-rules.en.md. Lees dan wat Onze Taal en de Nederlandse gidsen zeggen over ChatGPT als vertaald Engels: ${S}/nl/onzetaal-chatgpt-taalvragen.txt, ${S}/nl/frankwatching-2023-nederlandse-taal.txt, ${S}/nl/opdebeeck-herkennen.txt, ${S}/nl/rubens-zonder-technologie.txt, ${S}/nl/b2bmarketeers-herkennen.txt. Lees de Duitse naturalness-notities als zustertaalmodel: ${S}/repos/humanizer-de/references/de-naturalness.md.

Inventariseer dan zo volledig mogelijk, uit je eigen kennis van Nederlands taalmodel-output plus de bronnen, elk patroon in deze laag. Denk minstens aan:
- interpunctie op zijn Engels: komma voor "en"/"of" in opsommingen (Oxford comma), het ongespatieerde em-dash "—" waar het Nederlands een gespatieerd gedachtestreepje "–" of een komma gebruikt, Engelse aanhalingstekens, dubbele punt gevolgd door hoofdletter, hoofdletters in titels (Elk Woord Een Hoofdletter)
- leenvertalingen van AI-werkwoorden: duiken in, ontketenen, ontsluiten, benutten, navigeren, omarmen, stroomlijnen, verkennen, faciliteren, transformeren, empoweren, superchargen
- leenvertaald idioom: aan het eind van de dag, dat gezegd hebbende, maak geen vergissing, in termen van, het is wat het is, een game-changer, de sleutel tot, een reis, een landschap, de olifant in de kamer, buiten de gebaande paden, op de radar
- Engelse zinsbouw: bijwoord vooraan met komma ("Echter, ..." / "Uiteindelijk, ..." / "Bovendien, ..."), Engelse volgorde in bijzinnen, "Er zijn X die ..." in plaats van een directe zin, nominale stijl ("het bieden van", "het creëren van", "het waarborgen van") waar een werkwoord hoort, passief met "worden" waar het Nederlands actief zegt, "kan/kunnen/zou kunnen" als hedge-cascade
- Engelse aanspreek- en registerdrift: "je" en "u" door elkaar, "Laten we ...", "Ontdek ...", "Klaar om ...?", "Deel je gedachten in de reacties", "Wat denk jij?"
- onvertaalde termen en Engelse spelling waar Nederlands bestaat; Engelse hashtags met hoofdletters; "AI-gedreven", "datagedreven", "-gedreven" als productief suffix
- mechanisch parallellisme (elke zin dezelfde opbouw, gelijk lange bullets, "X. Y. Z."-fragmenten)
- vormresten: "In dit artikel verkennen we", "Samenvattend", "Kortom" als slotformule, "Conclusie" als kopje in een kort stuk

Per patroon: naam (Nederlands), categorie (translationese, of een andere categorie als het daar echt hoort), definitie, cues (letterlijk Nederlands), voorbeelden (voor: de Engelsvormige zin; na: hoe een Nederlander het schrijft), ernst, herkomst: translationese, en_id: "" tenzij er een Engelse tegenhanger is, notities (wanneer het GEEN tell is: bijv. de komma voor "en" is correct bij twee volledige hoofdzinnen).
${CAT_GUIDE}

Schrijf het resultaat ook als JSON naar ${S}/out/nl-extract-translationese.json en geef het terug.`

function mergePrompt(cats, rawByCatSubset) {
  return `Je voegt de helft van de Nederlandse catalogus van AI-schrijfpatronen samen en verifieert je eigen werk. Jouw categorieën: ${cats.join(', ')}.
${CAT_GUIDE}

Hieronder staan per categorie alle ruwe Nederlandse patronen, uit drie stromen: nl-bron (Nederlandse artikelen, Duitse zusterbronnen), transfer (afgeleid van de Engelse catalogus, met en_id) en translationese. Lees ook de huisregel in ${S}/baseline/house-copy-rule.md (geen em dashes, geen "niet x maar y", geen "X, geen Y"-slogan als opener, dubbelepunt-onthulling, drieslag, keelschrapers, aforistische slotzin, holle versterkers, meta-bewegwijzering) en zorg dat elk punt daaruit een entry of een cue is.

Maak per categorie canonieke Nederlandse entries:
- Dedupliceer op BETEKENIS. Een transfer-entry en een nl-bron-entry over hetzelfde mechanisme worden één entry; behoud en_id zodat de Engelse en Nederlandse catalogus op elkaar mappen.
- Schrap transfer-entries met lege cues (niet van toepassing in het Nederlands) tenzij een nl-bron ze bevestigt; noem ze in het rapport.
- id: kebab-case, Engels, GELIJK aan en_id waar een Engelse tegenhanger bestaat; anders een nieuw Engels id met achtervoegsel "-nl" (oxford-comma-nl, title-case-nl, calque-dive-in-nl).
- naam en definitie in het Nederlands, 2-4 zinnen, subvormen benoemd.
- cues: unie van alle letterlijke Nederlandse cues, gededupliceerd.
- regex: Python re, kleine letters, \\b-grenzen waar dat kan (\\b werkt niet naast tekens met accenten; gebruik dan (?<![a-zà-ÿ]) en (?![a-zà-ÿ])), strak genoeg om gewoon Nederlands niet te raken. Leeg voor structurele patronen. JSON-escaped backslashes.
- voorbeelden: 1-3 voor/na-paren in natuurlijk Nederlands, kort; het "na" bevat geen enkele tell (geen gedachtestreepje, geen niet-x-maar-y, geen drieslag, geen holle versterker, geen "Kortom").
- ernst, herkomst (dominant), en_id, bronnen (alle bron-ids), samengevoegd_uit (alle ruwe namen letterlijk), valse_positieven (wanneer NIET markeren: citaten, code, vakjargon, één losse instantie, formele registers, de komma voor "en" tussen twee hoofdzinnen, enz.).

Verifieer daarna, vóór je teruggeeft:
1. Elke ruwe naam heeft een thuis (eigen entry of samengevoegd_uit).
2. Regex-check: schrijf en draai een Python-script dat elke regex compileert (re.IGNORECASE) en per 10.000 woorden telt op menselijk geschreven Nederlands: ${S}/control/nl-wikipedia-rijssen.wikitext en ${S}/control/nl-wikipedia-enschede.wikitext (strip eerst de wikitext-markup: dubbele vierkante haken, dubbele accolades, ref-tags en de apostrof-opmaak). Repareer of verwijder wat niet compileert; scherp aan of verwijder wat meer dan 2 keer per 10.000 woorden raakt. Elke regex moet minstens één eigen cue of het voor-voorbeeld raken.
3. Lees elk "na" hardop als Nederlander: geen vertaald Engels, geen ambtelijk Nederlands, geen tell.

Schrijf het resultaat als JSON naar ${S}/out/nl-verified-${cats[0]}.json met vorm {"categories": [{"categorie": "...", "entries": [...]}, ...], "rapport": "...", "regex_verwijderd": N} en geef het terug.

RUWE ENTRIES PER CATEGORIE:
${JSON.stringify(rawByCatSubset)}`
}

phase('Extract')

const extractJobs = [
  ...NL_GROUPS.map(g => () => agent(nlExtractPrompt(g), { label: `extract:${g.id}`, phase: 'Extract', schema: RAW })),
  () => agent(DE_PROMPT, { label: 'extract:duits', phase: 'Extract', schema: RAW }),
  () => agent(TRANSLATIONESE_PROMPT, { label: 'extract:translationese', phase: 'Extract', schema: RAW }),
]
const HALVES = [['vocabulary', 'syntax', 'rhetoric', 'translationese'], ['structure', 'punctuation-format', 'content', 'artifacts']]
const transferJobs = HALVES.map((cats, i) => () =>
  agent(transferPrompt(cats), { label: `transfer:${i + 1}`, phase: 'Transfer', schema: RAW }))
const [extracted, transferred] = await Promise.all([
  parallel(extractJobs).then(r => r.filter(Boolean)),
  parallel(transferJobs).then(r => r.filter(Boolean)),
])
log(`extracted ${extracted.length} NL sources (${extracted.reduce((n, e) => n + e.patronen.length, 0)} raw), transferred ${transferred.length} halves (${transferred.reduce((n, e) => n + e.patronen.length, 0)} raw)`)

const rawByCat = Object.fromEntries(CATS.map(c => [c, []]))
for (const e of [...extracted, ...transferred]) {
  for (const p of e.patronen) {
    const cat = CATS.includes(p.categorie) ? p.categorie : 'rhetoric'
    rawByCat[cat].push({ ...p, bron: e.bron })
  }
}
log(`per categorie: ${CATS.map(c => `${c}=${rawByCat[c].length}`).join(' ')}`)

phase('Merge')
const verified = (await parallel(HALVES.map((cats, i) => () =>
  agent(mergePrompt(cats, Object.fromEntries(cats.map(c => [c, rawByCat[c]]))), { label: `merge:${i + 1}`, phase: 'Merge', schema: MERGED_HALF })
))).filter(Boolean)
log(`merged ${verified.length} halves, ${verified.reduce((n, v) => n + v.categories.reduce((m, c) => m + c.entries.length, 0), 0)} entries`)

phase('Consolidate')
const slim = verified.flatMap(v => v.categories.flatMap(c => c.entries.map(e => ({ id: e.id, en_id: e.en_id, categorie: c.categorie, naam: e.naam, ernst: e.ernst, herkomst: e.herkomst }))))
const dedup = await agent(`Consolidatie van de Nederlandse catalogus. Twee helften zijn los samengevoegd (${S}/out/nl-verified-vocabulary.json en ${S}/out/nl-verified-structure.json); hetzelfde patroon kan in twee categorieën staan onder verschillende ids.

Slanke lijst (id, en_id, categorie, naam, ernst, herkomst):
${JSON.stringify(slim)}

Doe:
1. Duplicaten over categorieën: kies de rijkste als overlever, verenig cues/regex/voorbeelden/bronnen/samengevoegd_uit, schrap de ander.
2. Verkeerd ingedeelde entries verplaatsen (${CATS.join(', ')}).
3. Ids uniek; id == en_id waar en_id bestaat; controleer met python3 dat elke niet-lege en_id bestaat als id in ${S}/out/catalog-en.json en maak hem leeg als dat niet zo is.
4. Schrijf ${S}/out/catalog-nl.json met vorm {"categories": {"<categorie>": [entries...]}, "count": N}.
5. Schrijf ${S}/out/catalog-nl-index.md: per categorie één regel per entry "- <id> (<ernst>, <herkomst>): <naam>".

Geef tellingen terug (merged, moved, total, per_category) en korte notes.`, { label: 'consolidate:catalog-nl', phase: 'Consolidate', schema: DEDUP })
log(dedup ? `catalog-nl: ${dedup.total} entries` : 'WARNING consolidation returned null')

return {
  extracted: extracted.map(e => `${e.bron}: ${e.patronen.length} raw; ${e.dekking}`),
  transferred: transferred.map(t => `${t.bron}: ${t.patronen.length}`),
  merged: verified.map(v => v.rapport),
  catalogNl: dedup,
}
