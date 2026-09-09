export const meta = {
  name: 'ai-tells-dutch-merge',
  description: 'Merge the extracted Dutch AI-writing patterns per category, self-verified against human Dutch, then consolidate into catalog-nl.json',
  phases: [
    { title: 'Merge', detail: 'one agent per category, reads its own raw file' },
    { title: 'Consolidate', detail: 'cross-category dedup into catalog-nl.json' },
  ],
}

const S = '/Users/ryangrippeling/projects/webgrip/webgrip-ai-skills/scripts/humanize'
const CATS = ['vocabulary', 'syntax', 'rhetoric', 'structure', 'punctuation-format', 'content', 'artifacts', 'translationese']

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
    herkomst: { type: 'string', enum: ['nl-bron', 'transfer', 'translationese', 'baseline'] },
    en_id: { type: 'string' },
    bronnen: { type: 'array', items: { type: 'string' } },
    samengevoegd_uit: { type: 'array', items: { type: 'string' } },
    valse_positieven: { type: 'string' },
  },
  required: ['id', 'naam', 'definitie', 'cues', 'regex', 'voorbeelden', 'ernst', 'herkomst', 'en_id', 'bronnen', 'samengevoegd_uit', 'valse_positieven'],
}
const MERGED = {
  type: 'object',
  properties: {
    categorie: { type: 'string' },
    entries: { type: 'array', items: NL_ENTRY },
    rapport: { type: 'string' },
    regex_verwijderd: { type: 'integer' },
    geschrapt: { type: 'array', items: { type: 'string' } },
  },
  required: ['categorie', 'entries', 'rapport', 'regex_verwijderd', 'geschrapt'],
}
const DEDUP = {
  type: 'object',
  properties: {
    merged: { type: 'integer' }, moved: { type: 'integer' }, total: { type: 'integer' },
    per_category: { type: 'object', additionalProperties: { type: 'integer' } },
    en_id_repaired: { type: 'integer' },
    notes: { type: 'string' },
  },
  required: ['merged', 'moved', 'total', 'notes'],
}

const CAT_GUIDE = `Categorieën: vocabulary (losse woorden en vaste frasen) · syntax (zinsconstructies) · rhetoric (argumentatieve zetten en toon) · structure (alinea- en documentvorm) · punctuation-format (interpunctie, emoji, vet, koppen) · content (inhoudelijke gebreken: vage bronnen, reclametaal, verzonnen ervaring) · artifacts (chatbotresten en machinesporen) · translationese (constructies die alleen bestaan omdat Engelsvormige tekst in het Nederlands werd gegenereerd)`

function mergePrompt(cat) {
  return `Je voegt één categorie van de Nederlandse catalogus van AI-schrijfpatronen samen en verifieert je eigen werk. Categorie: "${cat}".
${CAT_GUIDE}

Je invoer staat in ${S}/extracts/nl/nl-raw-${cat}.json: een JSON-array met alle ruwe Nederlandse patronen in deze categorie, uit drie stromen (herkomst-veld): nl-bron (Nederlandse artikelen, Duitse zusterbronnen), transfer (afgeleid van de Engelse catalogus, met en_id) en translationese. Elk item heeft naam, definitie, cues, voorbeelden, ernst, herkomst, en_id, notities en bron.

Lees het bestand met python3 (json.load) en verwerk het in stukken; print nooit het hele bestand in één keer naar je context. Werk met een script waar dat kan.

Lees ook de huisregel in ${S}/baseline/house-copy-rule.md en zorg dat elk punt daaruit dat in deze categorie hoort een entry of een cue is.

Maak canonieke Nederlandse entries:
- Dedupliceer op BETEKENIS. Een transfer-entry en een nl-bron-entry over hetzelfde mechanisme worden één entry; behoud en_id zodat de Nederlandse en Engelse catalogus op elkaar mappen.
- Schrap een transfer-entry die in het Nederlands niet bestaat (bijvoorbeeld een Engelse woordspeling zonder Nederlandse tegenhanger, of een Koreaans patroon dat via de Engelse catalogus is binnengekomen). Zet de naam in "geschrapt" met een reden.
- id: kebab-case, Engels, GELIJK aan en_id waar een Engelse tegenhanger bestaat; anders een nieuw Engels id met achtervoegsel "-nl" (oxford-comma-nl, title-case-nl, calque-dive-in-nl).
- naam en definitie in het Nederlands, 2 tot 4 zinnen, subvormen benoemd.
- cues: unie van alle letterlijke Nederlandse cues, gededupliceerd. Alleen cues die een Nederlands taalmodel echt schrijft; geen letterlijk vertaald Engels dat niemand gebruikt.
- regex: Python re, kleine letters (de scanner zet IGNORECASE aan), strak genoeg om gewoon Nederlands niet te raken. \\b werkt niet naast letters met accenten; gebruik daar (?<![a-zà-ÿ]) en (?![a-zà-ÿ]). Leeg laten voor structurele patronen die een lezer nodig hebben. JSON-escaped backslashes.
- voorbeelden: 1 tot 3 voor/na-paren in natuurlijk Nederlands, kort. Het "na" bevat zelf geen enkele tell: geen gedachtestreepje, geen niet-x-maar-y, geen drieslag, geen holle versterker, geen "Kortom", geen "cruciaal" of "naadloos".
- ernst (always, cluster, context), herkomst (de dominante), en_id, bronnen (alle bron-ids), samengevoegd_uit (alle ruwe namen letterlijk), valse_positieven (wanneer NIET markeren: citaten, code, vakjargon, één losse instantie, formele registers, de komma voor "en" tussen twee hoofdzinnen, enzovoort).

Verifieer daarna, vóór je teruggeeft:
1. Elke ruwe naam heeft een thuis: een eigen entry, een vermelding in samengevoegd_uit, of een regel in "geschrapt".
2. Regex-check: schrijf en draai een Python-script dat elke regex compileert (re.IGNORECASE) en telt hoe vaak hij raakt per 10.000 woorden op menselijk geschreven Nederlands: ${S}/control/nl-wikipedia-rijssen.wikitext en ${S}/control/nl-wikipedia-enschede.wikitext. Strip eerst de wikitext-opmaak (dubbele vierkante haken, dubbele accolades, ref-tags, apostrof-opmaak). Repareer of verwijder wat niet compileert. Scherp aan of verwijder wat vaker dan 2 keer per 10.000 woorden raakt; tel verwijderingen in regex_verwijderd. Elke overgebleven regex moet minstens één eigen cue of het voor-voorbeeld raken.
3. Lees elk "na"-voorbeeld hardop als Nederlander: geen vertaald Engels, geen ambtelijk Nederlands, geen tell.

Schrijf het resultaat als JSON naar ${S}/catalog/nl-verified-${cat}.json (vorm {categorie, entries, rapport, regex_verwijderd, geschrapt}) en geef het terug. Het rapport in twee of drie zinnen: welke regexen te breed waren met hun trefkans, wat je samenvoegde, wat je schrapte.`
}

phase('Merge')
const merged = (await parallel(CATS.map(cat => () =>
  agent(mergePrompt(cat), { label: `merge:${cat}`, phase: 'Merge', schema: MERGED })
))).filter(Boolean)
log(`merged ${merged.length}/${CATS.length} categories, ${merged.reduce((n, m) => n + m.entries.length, 0)} entries, ${merged.reduce((n, m) => n + m.geschrapt.length, 0)} dropped`)

phase('Consolidate')
const slim = merged.flatMap(m => m.entries.map(e => ({ id: e.id, en_id: e.en_id, categorie: m.categorie, naam: e.naam, ernst: e.ernst, herkomst: e.herkomst })))
const dedup = await agent(`Consolidatie van de Nederlandse catalogus. Acht categorieën zijn los samengevoegd in ${S}/catalog/nl-verified-<categorie>.json; hetzelfde patroon kan in twee categorieën staan onder verschillende ids, en sommige entries staan in de verkeerde categorie.

Slanke lijst van alle entries (id, en_id, categorie, naam, ernst, herkomst):
${JSON.stringify(slim)}

Doe:
1. Duplicaten over categorieën heen: kies de rijkste entry als overlever, verenig cues, regex, voorbeelden, bronnen en samengevoegd_uit, schrap de ander.
2. Verkeerd ingedeelde entries verplaatsen (${CATS.join(', ')}).
3. Ids uniek maken. id == en_id waar en_id niet leeg is. Controleer met python3 dat elke niet-lege en_id bestaat als id in ${S}/catalog/catalog-en.json; bestaat hij niet, maak en_id dan leeg en geef het id het achtervoegsel "-nl" als het nog geen Nederlands id is. Tel die reparaties in en_id_repaired.
4. Schrijf ${S}/catalog/catalog-nl.json met vorm {"categories": {"<categorie>": [entries...]}, "count": N}.
5. Schrijf ${S}/catalog/catalog-nl-index.md: per categorie één regel per entry "- <id> (<ernst>, <herkomst>): <naam>".

Geef tellingen terug (merged, moved, total, per_category, en_id_repaired) en korte notes over de keuzes.`, { label: 'consolidate:catalog-nl', phase: 'Consolidate', schema: DEDUP })
log(dedup ? `catalog-nl: ${dedup.total} entries` : 'WARNING consolidation returned null')

return {
  merged: merged.map(m => `${m.categorie}: ${m.entries.length} entries, ${m.geschrapt.length} geschrapt, -${m.regex_verwijderd} regex — ${m.rapport}`),
  geschrapt: merged.flatMap(m => m.geschrapt),
  catalogNl: dedup,
}
