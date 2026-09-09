export const meta = {
  name: 'humanize-judge-panel-nl',
  description: 'Native-speaker adversarial review of the Dutch catalog: two independent judges per category, then a verifier that rejects bad proposals before they land',
  phases: [
    { title: 'Judge', detail: 'two lenses per category, independent' },
    { title: 'Verify', detail: 'reject proposals that would make the catalog worse' },
  ],
}

const S = '/Users/ryangrippeling/projects/webgrip/webgrip-ai-skills/scripts/humanize'
const CATS = ['vocabulary', 'syntax', 'rhetoric', 'structure', 'punctuation-format', 'content', 'artifacts', 'translationese']

const LENSES = {
  eindredacteur: `Je bent eindredacteur bij een Nederlandse krant. Je leest al twintig jaar kopij van anderen en je hoort meteen of een zin door een Nederlander is geschreven of uit het Engels is gerold. Je hebt een hekel aan ambtelijk Nederlands en aan zinnen die kloppen maar die niemand zo zegt.`,
  vakschrijver: `Je bent technisch schrijver en developer, Nederlandstalig, en je schrijft dagelijks documentatie, releasenotes en meetup-teksten. Je weet welke Engelse termen in een Nederlandse technische tekst gewoon blijven staan (deploy, commit, pull request) en welke een vertaalfout zijn. Je herkent AI-output omdat je er elke dag mee werkt.`,
}

const FINDING = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    soort: { type: 'string', enum: ['na-onnatuurlijk', 'voor-onnatuurlijk', 'cue-bestaat-niet', 'definitie-onjuist', 'ernst-verkeerd', 'valse-positief-ontbreekt'] },
    probleem: { type: 'string' },
    voorstel: { type: 'string' },
    zekerheid: { type: 'string', enum: ['zeker', 'twijfel'] },
  },
  required: ['id', 'soort', 'probleem', 'voorstel', 'zekerheid'],
}
const MISSING = {
  type: 'object',
  properties: {
    naam: { type: 'string' },
    categorie: { type: 'string', enum: CATS },
    definitie: { type: 'string' },
    cues: { type: 'array', items: { type: 'string' } },
    voorbeeldzin: { type: 'string' },
    waarom_niet_gedekt: { type: 'string' },
  },
  required: ['naam', 'categorie', 'definitie', 'cues', 'voorbeeldzin', 'waarom_niet_gedekt'],
}
const REVIEW = {
  type: 'object',
  properties: {
    categorie: { type: 'string' },
    lens: { type: 'string' },
    beoordeeld: { type: 'integer' },
    bevindingen: { type: 'array', items: FINDING },
    ontbrekend: { type: 'array', items: MISSING },
    oordeel: { type: 'string' },
  },
  required: ['categorie', 'lens', 'beoordeeld', 'bevindingen', 'ontbrekend', 'oordeel'],
}
const VERDICT = {
  type: 'object',
  properties: {
    toegepast: { type: 'array', items: { type: 'string' } },
    afgewezen: { type: 'array', items: { type: 'string' } },
    nieuwe_entries: { type: 'array', items: { type: 'string' } },
    samenvatting: { type: 'string' },
  },
  required: ['toegepast', 'afgewezen', 'nieuwe_entries', 'samenvatting'],
}

function judgePrompt(cat, lens) {
  return `${LENSES[lens]}

Je beoordeelt één categorie van een Nederlandse catalogus van AI-schrijfpatronen. Categorie: "${cat}".

Lees de entries met python3 uit ${S}/catalog/catalog-nl.json, sleutel categories["${cat}"]. Print per entry id, naam, definitie, cues, voorbeelden, ernst en valse_positieven; niet het hele bestand in één keer.

Beoordeel ELKE entry in jouw categorie. Wees streng en concreet. Per entry vier vragen:

1. **Het "na"-voorbeeld**: lees het hardop. Is dit Nederlands zoals een mens het schrijft? Afkeuren als het vertaald Engels is, ambtelijk klinkt, zelf nog een tell draagt, of als het het probleem uit het "voor" niet oplost. Geef altijd een concrete betere zin in je voorstel, niet een aanwijzing.
2. **Het "voor"-voorbeeld**: demonstreert het echt het patroon? Een voor-zin die het patroon niet bevat maakt de entry onbruikbaar.
3. **De cues**: schrijft een Nederlands taalmodel dit echt? Afkeuren wat letterlijk uit het Engels is vertaald en wat geen mens en geen model ooit typt. Twijfel je, zeg dan twijfel; alleen wat je zeker weet krijgt zeker.
4. **Ernst en definitie**: klopt always/cluster/context? Een patroon dat in gewoon Nederlands voorkomt mag geen always zijn. Ontbreekt er een valse positief die je uit ervaring kent?

Meld alleen echte problemen. Een entry die klopt hoeft niet in je bevindingen te staan; ik tel ze via "beoordeeld".

Daarnaast: **welke Nederlandse AI-tells in deze categorie mist de catalogus?** Denk aan wat je zelf tegenkomt in Nederlandse LinkedIn-posts, nieuwsbrieven, bedrijfsblogs en gegenereerde documentatie. Alleen patronen die echt niet gedekt zijn; controleer eerst tegen de bestaande entries.

Geef terug: categorie, lens "${lens}", beoordeeld (het aantal entries dat je las), bevindingen, ontbrekend, en een oordeel van één alinea over de kwaliteit van deze categorie.`
}

phase('Judge')
const jobs = []
for (const cat of CATS) {
  for (const lens of Object.keys(LENSES)) {
    jobs.push(() => agent(judgePrompt(cat, lens), { label: `judge:${cat}/${lens}`, phase: 'Judge', schema: REVIEW }))
  }
}
const reviews = (await parallel(jobs)).filter(Boolean)
const findings = reviews.flatMap(r => r.bevindingen.map(b => ({ ...b, categorie: r.categorie, lens: r.lens })))
const missing = reviews.flatMap(r => r.ontbrekend.map(m => ({ ...m, lens: r.lens })))
log(`${reviews.length} reviews, ${reviews.reduce((n, r) => n + r.beoordeeld, 0)} entry-reads, ${findings.length} findings, ${missing.length} proposed additions`)

phase('Verify')
const verdict = await agent(`Je verwerkt het oordeel van een panel Nederlandse eindredacteuren en vakschrijvers in ${S}/catalog/catalog-nl.json. Elke categorie is door twee onafhankelijke lezers beoordeeld.

BEVINDINGEN (${findings.length}):
${JSON.stringify(findings)}

VOORGESTELDE ONTBREKENDE PATRONEN (${missing.length}):
${JSON.stringify(missing)}

Je bent de laatste zeef. Een panellid kan zich vergissen, een voorstel kan de catalogus slechter maken, en twee lezers kunnen elkaar tegenspreken. Beslis per bevinding:

- **Twee lezers melden hetzelfde probleem** op dezelfde entry: toepassen, tenzij beide voorstellen aantoonbaar fout Nederlands zijn.
- **Eén lezer, zekerheid "zeker"**: toepassen als het voorstel het echt beter maakt. Lees het voorgestelde "na" zelf hardop; is het slechter dan wat er stond, verwerp het en zeg waarom.
- **Eén lezer, zekerheid "twijfel"**: alleen toepassen als je het zelf kunt onderbouwen. Anders afwijzen, of de nuance opnemen in valse_positieven in plaats van de entry te veranderen.
- **Twee lezers spreken elkaar tegen**: kies de lezing die het patroon herkenbaar houdt en noteer de andere in valse_positieven.
- **Een cue die als niet-bestaand wordt gemeld**: verwijder hem alleen als de andere lezer het niet tegenspreekt en de cue ook niet in de bronnen voorkomt. Verwijder nooit een cue die in een regex wordt gebruikt zonder ook die regex aan te passen.
- **Ernst omlaag** (always naar cluster) is bijna altijd terecht als een lezer zegt dat het patroon in gewoon Nederlands voorkomt. Ernst omhoog vraagt twee lezers.

Voor de ontbrekende patronen: voeg er een toe als het echt niet gedekt is (controleer tegen alle entries, niet alleen die categorie), als het een Nederlandse tell is en niet een algemene stijlklacht, en als je er een cue en een voor/na-paar bij kunt schrijven die de toets doorstaan. Geef het een id in kebab-case met achtervoegsel "-nl", herkomst "nl-bron", en en_id "" tenzij er een Engelse tegenhanger bestaat in ${S}/catalog/catalog-en.json.

Regels voor alles wat je schrijft:
- Elk "na"-voorbeeld is natuurlijk Nederlands en draagt zelf geen tell: geen gedachtestreepje, geen niet-x-maar-y, geen drieslag, geen holle versterker, geen "Kortom", geen "cruciaal" of "naadloos".
- Elke nieuwe of gewijzigde regex compileert onder Python re met IGNORECASE, raakt zijn eigen cue of voor-voorbeeld, en raakt hoogstens 2 keer per 10.000 woorden op ${S}/control/nl-wikipedia-rijssen.wikitext en ${S}/control/nl-wikipedia-enschede.wikitext (strip de wikitext-opmaak). Draai dat met een script.
- Verander niets aan de sleutelnamen of de structuur van het JSON-bestand.

Schrijf het bijgewerkte bestand terug naar ${S}/catalog/catalog-nl.json met de count bijgewerkt, en geef terug: toegepast (één regel per wijziging, met id en wat er veranderde), afgewezen (met reden), nieuwe_entries (ids), en een samenvatting van twee of drie zinnen.`, { label: 'verify:apply-panel', phase: 'Verify', schema: VERDICT })

return {
  reviews: reviews.map(r => `${r.categorie}/${r.lens}: ${r.beoordeeld} gelezen, ${r.bevindingen.length} bevindingen, ${r.ontbrekend.length} ontbrekend — ${r.oordeel}`),
  findings_by_kind: findings.reduce((acc, f) => ({ ...acc, [f.soort]: (acc[f.soort] || 0) + 1 }), {}),
  verdict,
}
