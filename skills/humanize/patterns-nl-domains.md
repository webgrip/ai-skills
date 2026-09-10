# Nederlandse catalogus, domeingebonden entries (Wikipedia, fictie)

Eén entry per patroon: wat het is, de letterlijke signalen, één voor/na, de ernst en wanneer je het niet markeert. Ernst: **always** (één treffer volstaat), **cluster** (alleen een tell bij opeenhoping), **context** (het register beslist). Signalen die een regex kan vangen staan ook in `scripts/patterns.json` onder hetzelfde id; `en_id` koppelt aan de Engelse catalogus.

Inhoud: [Retorische zetten en toon](#retorische-zetten-en-toon) (1) · [Alinea- en documentstructuur](#alinea-en-documentstructuur) (3) · [Interpunctie en opmaak](#interpunctie-en-opmaak) (1) · [Inhoud en bewijs](#inhoud-en-bewijs) (4) · [Machinesporen](#machinesporen) (4)

## Retorische zetten en toon

### Afleiden naar het proces bij kritiek `review-process-deflection`

Ernst: **cluster** · Herkomst: transfer · en: `review-process-deflection`

Als de herkomst of kwaliteit van een bijdrage ter discussie staat, gaat het antwoord over het proces in plaats van over de tekst: de criticus vragen precies aan te wijzen wat er mis is, het bezwaar afdoen als ongefundeerde speculatie, doorverwijzen naar samenwerking (laten we samen het artikel verbeteren), of melden dat de feedback is verwerkt zonder te zeggen wat er veranderde. Beantwoord de inhoud.

Signalen: `geef precies aan welke delen` · `laat me weten wat er precies mis is` · `ongefundeerde speculatie` · `laten we samen het artikel verbeteren` · `zonder te onderbouwen waarom` · `feedback verwerkt zonder te noemen wat er veranderde`

Voor: Laten we samen het artikel verbeteren; geef precies aan welke delen je onjuist vindt.

Na: Twee van de drie bronnen noemen het onderwerp niet. Ik heb ze vervangen door het provinciale register uit 2019.

Niet markeren: Om verduidelijking vragen is legitiem als de kritiek echt vaag was en de vraag concreet is. In moderatie- en overlegpagina's is procesverwijzing soms de juiste route. De tell is de procesbeweging in plaats van een inhoudelijk antwoord dat wel te geven was. In een PR-beschrijving, changelog of commit is 'feedback verwerkt' een statusregel en staat de wijziging in de diff. De tell is de melding in een discussie waarin de inhoudelijke vraag onbeantwoord blijft.

## Alinea- en documentstructuur

### Sjabloon-profielpagina `canned-profile-page`

Ernst: **cluster** · Herkomst: transfer · en: `canned-profile-page`

Een profiel- of biopagina volgens een vast sjabloon: koppen als Over mij, Mijn interesses en Laten we connecten, bullets met een emoji per item, vetgedrukte aantallen en een opgewekte afsluiter. Dezelfde vorm verschijnt op LinkedIn, op GitHub en op een gebruikerspagina. Twee of drie gewone zinnen over wat iemand werkelijk doet vervangen het geheel.

Signalen: `Over mij` · `Wie ben ik` · `Mijn interesses` · `Mijn bijdragen` · `Laten we connecten!` · `Laten we samenwerken` · `Neem gerust contact met mij op` · `Stuur me gerust een bericht` · `Veel plezier!` · `20+ artikelen`

Voor: == Over mij ==
* Ik schrijf graag over Twentse techbedrijven.
== Laten we connecten! ==
Neem gerust contact met mij op als je wilt samenwerken!

Na: Ik schrijf over techbedrijven in Twente, meestal over de maakindustrie. Een stuk of twintig artikelen inmiddels. Vragen of correcties kun je op mijn overlegpagina kwijt.

Niet markeren: 'Over mij' is op een portfolio of een website een gangbare, verwachte kop, en 'neem gerust contact op' hoort in zakelijke copy op een contactpagina. Een sollicitatiebrief mag een opgewekte afsluiter hebben. Het signaal is het hele sjabloon: de vaste koppenreeks met emoji-bullets en aantallen zonder inhoud.

### Verhaaldefaults: vast perspectief, vlak tempo, alles rond `narrative-flatness`

Ernst: **cluster** · Herkomst: transfer · en: `narrative-flatness`

Fictie kiest een verteltrant en houdt die met onnatuurlijke consequentheid vast, zonder drift tussen vrije indirecte rede, innerlijke monoloog en buitenscene. Elke scene loopt op hetzelfde tempo, zonder weglating, samenvatting of versnelling, en het einde knoopt elke draad dicht. Het model vertrouwt de lezer geen dubbelzinnigheid toe tenzij daarom gevraagd wordt.

Signalen: `elke scene op hetzelfde tempo` · `geen wisseling tussen vrije indirecte rede en scene` · `alle vragen aan het eind beantwoord` · `geen tijdsprong of samenvatting`

Voor: (elke scene op dezelfde afstand verteld, met een slot waarin elke vraag beantwoord wordt)

Na: (de reis in één zin, de aankomst in een bladzijde, en één vraag blijft bij de lezer liggen)

Niet markeren: Genres met een eigen belofte sluiten hun draden af: een detective wijst de dader aan, een sprookje eindigt goed, een kinderboek stelt gerust. Een korte scene hoeft geen tempowisseling te hebben. Beoordeel op de lengte van een verhaal of een hoofdstuk, niet op een fragment.

### Standaardvormen in poëzie `verse-form-defaults`

Ernst: **context** · Herkomst: transfer · en: `verse-form-defaults`

Gegenereerde poëzie valt in de standaardinstellingen van het model, wat de opdracht ook was: eindrijm waar niemand erom vroeg, strofen van vier regels, en oppervlakkige trouw aan een vorm. Een sonnet haalt veertien regels, een sestine negenendertig, maar de interne regel klopt niet. In het Nederlands valt de default terug op rijm op -en, op -acht (nacht, kracht, zacht), op -and (hand, land, verstand) en op abstracta op -heid.

Signalen: `eindrijm zonder dat erom gevraagd is` · `elke strofe precies vier regels` · `jambisch metrum waar niemand om vroeg` · `rijmparen op -en, -acht, -and en -heid`

Voor: Een 'sestine' van 39 regels waarvan de zes eindwoorden nooit rouleren, in rijmende jamben.

Na: Laat de zes eindwoorden door alle strofen en de envoi rouleren, of noem het geen sestine.

Niet markeren: Als om een vaste vorm gevraagd is, is die vorm de opdracht en geen signaal. Kinderversjes, liedteksten, sinterklaasgedichten en gelegenheidsrijm horen te rijmen. Ook een dichter met een eigen vaste vorm valt erbuiten. Het signaal is de vorm die niemand vroeg, of de vormnaam zonder de regel die erbij hoort.

## Interpunctie en opmaak

### Regieaanwijzing tussen haakjes in dialoog `parenthetical-stage-directions`

Ernst: **always** · Herkomst: transfer · en: `parenthetical-stage-directions`

Dialoog met een emotie tussen haakjes voor de regel, als in een scenario, in proza dat geen scenario is. Het is een toneelconventie die in verhalend Nederlands het werk van de zin overneemt. Leg de emotie in de woorden zelf of in een handeling.

Signalen: `(geïrriteerd)` · `(zuchtend)` · `(lachend)` · `(aarzelend)` · `Bob: (verdedigend) Waarom zou ik?`

Voor: Bob: (verdedigend) Waarom zou ik?
Tonny: (geïrriteerd) Luister nou.

Na: Bob sloeg zijn armen over elkaar. "Waarom zou ik?" Tonny wreef in zijn ogen. "Luister nou."

Niet markeren: In een scenario, een toneeltekst, een hoorspel, een podcastscript of een interviewtranscriptie is dit de juiste vorm. Ook niet markeren in ondertitelbestanden en in notulen die een reactie noteren.

## Inhoud en bewijs

### Cliché en overdadig proza `cliche-and-purple-prose`

Ernst: **cluster** · Herkomst: transfer · en: `cliche-and-purple-prose`

Standaardformuleringen en overversierde beschrijving zonder iets eronder: alles wat de tekst bedoelt staat op de bladzijde, er zit geen laag onder het beeld, en de versiering vervangt de waarneming. In het Nederlands gaat het om eigen clichés (het hart bonkte in haar keel, een golf van emoties) en om beeldspraak die te groot is voor het onderwerp (een rijk tapijt, een symfonie van, een baken van hoop). Ervaren lezers noemen juist dit cluster als de manier waarop ze machinefictie herkennen.

Signalen: `haar hart bonkte in haar keel` · `een traan gleed over haar wang` · `niets zou ooit nog hetzelfde zijn` · `met een brok in de keel` · `de tijd leek stil te staan` · `een golf van emoties` · `rijk tapijt` · `een symfonie van` · `baken van hoop`

Voor: Haar hart bonkte in haar keel terwijl een traan over haar wang gleed, en ze wist dat niets ooit nog hetzelfde zou zijn.

Na: Ze las het bericht twee keer, legde haar telefoon omgekeerd neer en ruimde de vaatwasser verder in.

Niet markeren: Niet markeren in een citaat, in pastiche of parodie, en niet bij één vaste uitdrukking in een verder sobere tekst. In liedteksten en in gelegenheidspoëzie hoort een deel van dit register bij het genre.

### Vlakke dialoog en uitleg voor de lezer `flat-dialogue-and-exposition`

Ernst: **cluster** · Herkomst: transfer · en: `flat-dialogue-and-exposition`

Personages zijn onderling verwisselbaar: geen eigen woorden, geen tic, geen dialect, geen eigen manier van ontwijken onderscheidt de een van de ander. In de dialoog staat bovendien informatie die de sprekers allang delen, zodat de lezer hem kan horen, en raadsels worden opgelost met uitleg in plaats van met handeling. Geef elke spreker een eigen manier van praten en laat de gebeurtenissen het verhaal dragen.

Signalen: `zoals je weet` · `zoals u weet` · `zoals we allemaal weten` · `alle personages praten hetzelfde` · `uitleg in dialoog voor de lezer`

Voor: Zoals je weet, dokter, is de reactor in 1974 gebouwd en sindsdien nooit nagekeken, zei ze.

Na: "Vierenzeventig," zei ze. "Sindsdien heeft niemand hem opengemaakt." Hij wist het allang en liet het haar toch zeggen.

Niet markeren: 'Zoals je weet' is in gewone correspondentie en in lesmateriaal een normale beleefdheidsformule; de tell is de vorm in dialoog waar de spreker informatie geeft die de ander al heeft. Niet markeren in toneel waar het personage die formule met opzet gebruikt.

### Decor als stemmingsspiegel `pathetic-fallacy-mood-setting`

Ernst: **cluster** · Herkomst: transfer · en: `pathetic-fallacy-mood-setting`

Weer, kamers en voorwerpen bestaan alleen om het gevoel van een personage te spiegelen: regen bij verdriet, een kamer die koud is omdat het huwelijk dat is. Het decor draagt geen zelfstandig feit meer en houdt daarmee op een plek te zijn. Laat het decor zichzelf zijn en laat de emotie uit de gebeurtenis komen.

Signalen: `alsof de regen haar verdriet weerspiegelde` · `tikte zacht tegen het raam` · `de lucht was net zo grauw als haar stemming` · `de kamer voelde koud aan, net als` · `de lucht weerspiegelde haar stemming`

Voor: De regen tikte zacht tegen het raam, alsof hij haar onuitgesproken verdriet weerspiegelde.

Na: Het regende. Ze hield het raam toch open, want de kamer rook naar zijn shag.

Niet markeren: Niet markeren als het weer een rol speelt in de handeling (de wedstrijd ging niet door), en niet in poëzie of in een stijl die het beeld bewust en herkenbaar inzet. Één stemmig decorzinnetje in een verhaal is geen patroon.

### Autoritair gekleurde framing `pro-authoritarian-bias`

Ernst: **context** · Herkomst: transfer · en: `pro-authoritarian-bias`

Bij politieke onderwerpen neigt gegenereerde tekst naar de kadering van staatsmedia: regeringen van vrijere landen krijgen makkelijker kritiek dan repressieve, en soms volgt een weigering op veiligheidsgronden die maar één kant op werkt. In het Nederlands is dit niet gemeten, dus de cues zijn gereconstrueerd en de vondst is een aanleiding om te controleren, geen bewijs. Leg politieke kadering naast onafhankelijke verslaggeving voordat je publiceert.

Signalen: `heeft zich onder de huidige regering stabiel ontwikkeld` · `onder leiding van de autoriteiten` · `de situatie is genormaliseerd` · `westerse media melden daarentegen`

Voor: De regio heeft zich onder leiding van de huidige autoriteiten stabiel ontwikkeld en de situatie is inmiddels genormaliseerd.

Na: Human Rights Watch documenteerde in 2025 340 detenties in de regio. Het bestuur betwist dat aantal.

Niet markeren: Geen regex: elke formulering hier komt ook in gewone verslaggeving en in diplomatieke taal voor, dus een regex zou vooral neutrale nieuwstekst raken. Niet markeren bij een geciteerde regeringsverklaring of een weergave van een standpunt die als zodanig gemarkeerd is.

## Machinesporen

### Verzonnen of kapotte opmaak voor het doelsysteem `broken-target-markup`

Ernst: **always** · Herkomst: transfer · en: `broken-target-markup`

Opmaak die het model niet beheerst komt er verzonnen, verminkt of half toegepast uit. Subvormen: sjabloon- en parameternamen die op het echte schema lijken maar niet bestaan, zodat ze als rode link renderen of niets doen; verhaspelde sjabloonsyntaxis; en verwijzingstags die niet sluiten. Controleer elke sjabloonnaam tegen het doelsysteem voordat je publiceert. Buiten een wiki is de dagelijkse vorm een verzonnen component of shortcode: een <Callout> in een project dat dat component niet heeft, een Hugo-shortcode in een Astro-site, of Jira-opmaak in een issue dat Markdown rendert.

Signalen: `{{Infobox oude bevolking | regio = IJsseldal` · `| archeologische_vindplaatsen =` · `<ref name="bron1">Twentse Courant` · `<sup>[1]</sup>` · `[[Categorie:Nederlandse gemeente]]` · `een sjabloonnaam die op de doelwiki niet bestaat` · `<Callout type="info"> in een repo zonder dat component` · `{{< figure src=... >}} in een site die geen Hugo draait` · `{code:java} of {panel} in een Markdown-issue` · `::: tip in een bestand waarvan de opmaaktaal geen admonitions kent` · `een import-regel voor een component dat nergens bestaat`

Voor: {{Infobox oude bevolking | regio = IJsseldal | archeologische_vindplaatsen = Hunebed D27 }}

Na: {{Infobox archeologische cultuur | regio = IJsseldal | belangrijkstevindplaatsen = Hunebed D27 }}

Niet markeren: Op een wiki zelf zijn categorieregels, infoboxen en ref-tags gewone syntaxis; de regels markeren kandidaten, en alleen het doelsysteem kan zeggen of een sjabloon bestaat. Een ref-tag die verderop in het document sluit valt buiten het venster van de zoekregel en levert dan onterecht een treffer op bij zeer lange citaten.

### Plaatshouder in een gestructureerd veld `placeholder-in-metadata-field`

Ernst: **always** · Herkomst: transfer · en: `placeholder-in-metadata-field`

Een bron-, infobox- of frontmatterveld draagt een stomp in plaats van een waarde: "url=URL", "BRON_URL_HIER", "uitgever=UITGEVER", "datum=onbekend". Datumstompen als "2025-XX-XX" horen hier ook bij; ze duiken vooral op in geraadpleegd-op en veroorzaken gereedschapsfouten. Vul het veld of haal de hele verwijzing weg, want een bron die niet naar iets wijst onderbouwt niets. Het geldt net zo goed voor frontmatter in een statische site of een headless CMS: title: Untitled, description: TODO, author: Your Name, date: 1970-01-01.

Signalen: `geraadpleegd op 2025-XX-XX` · `url=URL` · `BRON_URL_HIER` · `uitgever=UITGEVER` · `titel=Titel` · `datum=onbekend` · `title: Untitled` · `description: TODO` · `author: Your Name` · `date: 1970-01-01` · `slug: mijn-eerste-post` · `tags: [tag1, tag2]`

Voor: {{Citeer web |url=BRON_URL_HIER |uitgever=UITGEVER |datum=2022-11-XX}}

Na: (de verwijzing is weggehaald; er is nooit iets geraadpleegd)

Niet markeren: Documentatie over een sjabloon toont de veldnamen met een voorbeeldwaarde; dat is de bedoeling. Een echte bron met een onbekende datum hoort het veld leeg te laten in plaats van er "onbekend" in te zetten, maar dat is een stijlkeuze, geen machinespoor.

### Verouderde of onmogelijke sjabloonmetadata `stale-boilerplate-metadata`

Ernst: **cluster** · Herkomst: transfer · en: `stale-boilerplate-metadata`

Een nieuw document draagt metadata die het niet verdiend kan hebben: een onderhouds- of stijlsjabloon met een datum van voor het bestaan van het document, een inzendkop die de inzending alvast afwijst, of een geraadpleegd-op-datum die niet kan kloppen. Het model kopieert de vorm inclusief een datum die het uit zijn trainingsmateriaal kent. Zet de datum op de dag van aanmaak of haal het sjabloon weg. Het geldt net zo goed buiten een wiki: een verse pagina met een voettekst, een versieregel of een lastmod-veld dat ouder is dan de pagina zelf, geërfd uit het trainingsmateriaal.

Signalen: `{{Wikify|datum=september 2022}} op een pagina van 2026` · `|bezochtdatum=12 december 2024` · `|datum=februari 2025 op een nieuw artikel` · `{{Meebezig}}` · `{{Wikificatie|datum=september 2022}} op een pagina van 2026` · `Laatst bijgewerkt: januari 2025 op een pagina van 2026` · `© 2023 in de voettekst van een nieuwe site` · `lastmod dat ouder is dan date in dezelfde frontmatter` · `Versie 1.0, februari 2024 boven een net geschreven document`

Voor: Een pagina die in februari 2026 is aangemaakt en opent met {{Wikify|datum=september 2022}}

Na: Een pagina die in februari 2026 is aangemaakt en opent met {{Wikify|datum=februari 2026}}

Niet markeren: Een oud artikel dat al jaren een onderhoudssjabloon draagt hoort die oude datum te hebben. Een geraadpleegd-op-datum in het verleden is normaal bij een bron die eerder is nagekeken; de tell is dat de datum ouder is dan het document zelf. Een beginnetje- of meebezigsjabloon op een kort nieuw artikel is normale wikipraktijk en zegt niets.

### Sjabloonmatige wijzigingsnotitie `templated-change-note`

Ernst: **cluster** · Herkomst: transfer · en: `templated-change-note`

Een wijzigingsbeschrijving (commitbericht, PR-tekst, bewerkingssamenvatting) geschreven als uitputtend procedureel proza in plaats van een korte notitie. Subvormen: de volzin die alles opsomt wat er is gedaan en hoe het aan de regels voldoet, en de mededeling wat er bewust niet is veranderd, die de beperking uit de opdracht terugkaatst. Schrijf op wat er veranderde, in zo min mogelijk woorden.

Signalen: `Verbeterde duidelijkheid, structuur en leesbaarheid` · `Herzien voor betere leesbaarheid` · `met behoud van de oorspronkelijke betekenis` · `Uitgebreide herschrijving:` · `zonder de inhoud te wijzigen` · `Toon en stijl gelijkgetrokken`

Voor: Verbeterde duidelijkheid, structuur en leesbaarheid van de plotsectie; herhaling teruggebracht en toon aangescherpt voor een betere encyclopedische stijl.

Na: plot ingekort

Niet markeren: Een release-aankondiging of changelog voor gebruikers mag uitleggen wat er beter is geworden. In een refactorcommit is "zonder gedragswijziging" een nuttige en precieze mededeling; de tell is de opgestapelde, niet-specifieke opsomming.
