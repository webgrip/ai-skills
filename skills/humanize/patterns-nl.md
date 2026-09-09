# Nederlandse catalogus: de tells, per categorie

Eén entry per patroon: wat het is, de letterlijke signalen, één voor/na, de ernst en wanneer je het niet markeert. Ernst: **always** (één treffer volstaat), **cluster** (alleen een tell bij opeenhoping), **context** (het register beslist). Signalen die een regex kan vangen staan ook in `scripts/patterns.json` onder hetzelfde id; `en_id` koppelt aan de Engelse catalogus.

Inhoud: [Zinsconstructies](#zinsconstructies) (25) · [Retorische zetten en toon](#retorische-zetten-en-toon) (37) · [Woordkeus](#woordkeus) (32) · [Alinea- en documentstructuur](#alinea-en-documentstructuur) (27) · [Interpunctie en opmaak](#interpunctie-en-opmaak) (23) · [Inhoud en bewijs](#inhoud-en-bewijs) (35) · [Machinesporen](#machinesporen) (27) · [Translationese: Engelsvormig Nederlands](#translationese-engelsvormig-nederlands) (45)

## Zinsconstructies

### Valse reeks (van X tot Y) `false-range`

Ernst: **always** · Herkomst: nl-bron · en: `false-range`

Twee voorbeelden uit een verzameling worden gepresenteerd als de uiteinden van een spectrum, terwijl er geen spectrum is: van startups tot multinationals, van de oerknal tot donkere materie. De toets: vraag wat er tussen X en Y ligt, of vervang X en Y door een willekeurig ander paar; blijft de zin overeind, dan is de reeks leeg. Noem de echte onderwerpen of kies er één.

Signalen: `van startups tot multinationals` · `van beginners tot experts` · `van klein tot groot` · `variërend van ... tot ...` · `uiteenlopend van ... tot ...` · `van de oerknal tot donkere materie` · `van A tot Z`

Voor: De meetup trekt bezoekers van studenten tot doorgewinterde architecten.

Na: Bij de laatste editie kwamen achttien studenten en vierentwintig werkende ontwikkelaars.

Niet markeren: Letterlijke reeksen in tijd, ruimte, maat of alfabet zijn geen tell: van 2019 tot 2023, van Enschede tot Almelo, van maandag tot vrijdag, van A tot Z als vaste uitdrukking voor volledigheid. Behandel treffers als kandidaten en pas de tussenruimte-toets toe voor je markeert.

### Levenloos onderwerp met een menselijk werkwoord `inanimate-agent`

Ernst: **always** · Herkomst: transfer · en: `inanimate-agent`

Een abstractie of een ding wordt onderwerp van een werkwoord dat alleen mensen uitvoeren: de data vertelt ons, het rapport laat ons zien, de techniek vraagt om, het besluit ontstond. De handelende persoon verdwijnt en het ding krijgt een wil. Herschrijf met de persoon of organisatie die handelde, of kies een zwakker werkwoord.

Signalen: `de data vertelt ons` · `de cijfers zeggen` · `het rapport laat ons zien` · `de techniek vraagt om` · `de tijd roept om` · `de code nodigt je uit` · `het besluit ontstond`

Voor: Het besluit ontstond na weken van overleg.

Na: Het team besloot het na weken van overleg.

Niet markeren: Vaste metonymie is gewoon Nederlands: het kabinet besloot, de gemeente meldt, de wet bepaalt, het contract zegt. Ook: een bewust literair beeld, en vakjargon waarin een systeem echt een handeling uitvoert ('de scheduler kiest de volgende taak'). Markeer waar het werkwoord bewustzijn onderstelt.

### Ontkenningsaftelling (Geen X. Geen Y. Gewoon Z.) `negation-countdown`

Ernst: **always** · Herkomst: transfer · en: `negation-countdown`

Twee of meer ontkende zaken worden opgestapeld voor het bevestigde antwoord, zodat daadkracht wordt gespeeld door opties weg te vegen die niemand voorstelde. Vormen: het fragmentaftellen (Geen gedoe. Geen kosten. Gewoon werken.), de komma-keten (geen gedoe, geen gezeur, geen kleine lettertjes), de hele-zinvariant (Het is niet de prijs. Het is niet de functie. Het is het vertrouwen.) en de drieslag met tegenstelling (Niet links, niet rechts, maar recht door zee). Eén ontkenning verdient haar plek alleen als de lezer anders het tegendeel aanneemt.

Signalen: `Geen X. Geen Y. Gewoon Z.` · `geen gedoe, geen gezeur, geen kleine lettertjes` · `Niet X. Niet Y. Wel Z.` · `Het is niet A. Het is niet B. Het is C.` · `Noem het geen X. Noem het Y.` · `Niet links, niet rechts maar recht door zee` · `Niet Copilot, niet Claude, maar jijzelf`

Voor: Geen gedoe, geen opvulling, geen jargon.

Na: In elk hoofdstuk staat iets wat je kunt nakijken.

Niet markeren: Een opsomming van dingen die echt ontbreken en die de lezer moet weten (een productpagina die 'geen abonnement, geen account' meldt omdat concurrenten die wel eisen) is informatie. Ook overslaan: opsommingen in contracten en voorwaarden, en citaten van bestaande leuzen.

### Negatief parallellisme (het is geen X, het is Y) `negative-parallelism`

Ernst: **always** · Herkomst: nl-bron · en: `negative-parallelism`

Een punt wordt gebracht als correctie op een bewering die niemand deed: de zwakkere lezing wordt ontkend en de echte in dezelfde adem gegeven. Vormen: het scharnier binnen één zin (het is niet X, het is Y), de optellende variant (niet alleen X, maar ook Y), de gesplitste variant (Dat is geen X. Dat is Y. / De vraag is niet X. De vraag is Y.), de oorzaakvariant (niet omdat X, maar omdat Y), de omgekeerde slogan (X, geen Y) en de opwaardering meer dan alleen X. In gewoon Nederlands is een enkele maar-tegenstelling normaal; de tell is het geënsceneerde sjabloon met herhaald koppelwerkwoord, en de herhaling ervan door de tekst.

Signalen: `het is niet X, het is Y` · `het is geen X, het is Y` · `dat is geen X, dat is Y` · `dit is geen tool, dit is een manier van denken` · `niet X, maar Y` · `X, geen Y` · `niet alleen ..., maar ook` · `het gaat niet alleen om ..., maar` · `het gaat niet om X, het gaat om Y` · `dit gaat niet over X, maar over Y` · `de vraag is niet X, de vraag is Y` · `niet omdat X, maar omdat Y` · `niet zomaar een ..., maar` · `meer dan alleen` · `het draait niet om` · `niet ..., maar juist` · `eerder X dan Y`

Voor: Het gaat niet om efficiëntie, het gaat om transformatie.

Na: De winst zit in een andere manier van werken. Sneller gaat het ook, dat is bijvangst.

Niet markeren: Een gewone correctie waarin het ontkende deel echt in de lucht hing ('Hij kwam niet uit Hengelo, maar uit Borne') is geen tell. Ook niet: citaten, juridische of contracttekst waarin een afbakening telt, en een enkele maar-tegenstelling zonder herhaald koppelwerkwoord. Markeer pas bij het gesloten sjabloon of bij twee of meer gevallen in één stuk.

### Duidingsstaart (wat het belang onderstreept) `participial-tail`

Ernst: **always** · Herkomst: nl-bron · en: `participial-tail`

Aan een gewoon feit wordt een staart geplakt die er een betekenis aan geeft die de bron niet levert: belang (wat het belang onderstreept, wat de noodzaak benadrukt), een trend (wat past in een bredere trend), symboliek (waarmee het bedrijf laat zien dat) of een doel (en zo een bijdrage levert aan). Het Engels doet dit met een tegenwoordig deelwoord, het Nederlands met een bijzin op wat of waarmee. Schrap de staart, of maak er een aparte zin van met een bron en een concreet gevolg. Dezelfde staart vat ook het gevolg samen, overgezet uit het Engelse resulting in, leading to en allowing you to: wat resulteert in kortere wachttijden, waardoor je tijd bespaart.

Signalen: `, wat het belang onderstreept` · `, wat de noodzaak benadrukt` · `, waarmee wordt benadrukt dat` · `, wat aantoont dat` · `, wat bijdraagt aan` · `, wat past in een bredere trend` · `, waarmee het bedrijf laat zien dat` · `, wat de veelzijdigheid illustreert` · `, waardoor wordt gewaarborgd dat` · `daarmee benadrukkend` · `, wat resulteert in` · `, wat leidt tot` · `, waardoor je` · `, wat betekent dat` · `, waardoor het team` · `, wat zorgt voor`

Voor: De meetup vindt maandelijks plaats, wat het belang van regelmaat voor de gemeenschap onderstreept.

Na: De meetup vindt elke derde donderdag van de maand plaats.

Niet markeren: Een bijzin die echt nieuwe informatie draagt ('wat de gemeente 40.000 euro kostte') is geen duidingsstaart. Ook overslaan: een geciteerd oordeel met bron ('wat volgens de rekenkamer het toezicht ondermijnt'), en juridische of normatieve tekst waarin 'waardoor wordt gewaarborgd dat' de norm zelf is. Een gevolgzin met 'waardoor' is gewoon Nederlands en vaak de beste formulering, zeker als het gevolg concreet is. Het signaal is de herhaling, elke alinea dezelfde staart, en een staart die niets nieuws zegt.

### Retorische zelfvraag (Het resultaat? Verwoestend.) `rhetorical-self-question`

Ernst: **always** · Herkomst: nl-bron · en: `rhetorical-self-question`

De schrijver stelt zichzelf een vraag en beantwoordt hem meteen, of vuurt vragen af als uitstel: de beantwoorde zelfvraag (Het resultaat? Verwoestend.), de overgangsvraag (Wat betekent dit voor jou?), het nagespeelde vraaggesprek (Is het snel? Ja. Is het goedkoop? Ook.) en de vragenketen. Het trucje zelf is prima; de frequentie verraadt de machine, en de antwoorden slaan soms niet eens terug op de vraag. Maak er een mededeling van; weet je het antwoord, zeg het dan.

Signalen: `Het resultaat?` · `Het mooiste?` · `Het ergste?` · `Zou ik het opnieuw doen? Zeker.` · `Wat betekent dit voor jou?` · `Waarom? Omdat` · `Klinkt goed, toch?` · `Is het snel? Ja.` · `Herkenbaar?`

Voor: Het resultaat? Verwoestend.

Na: De storing kostte het bedrijf twee dagen omzet.

Niet markeren: Een echte vraag aan de lezer die onbeantwoord blijft, een FAQ, een interview, een quiz of een didactische opbouw waarin de vraag de stof structureert. Ook: één zelfvraag in een lang stuk. Markeer bij herhaling, bij een vraag die geen lezer stelt, of waar het antwoord in de volgende halve zin al staat.

### Staccato-fragmenten (Snel. Simpel.) `staccato-fragments`

Ernst: **always** · Herkomst: transfer · en: `staccato-fragments`

Twee of meer korte zinnen zonder werkwoord staan achter elkaar als dramatische tikken: het paar (Snel. Simpel.), de reeks, en het slotduo (Dat is het. Meer is het niet.). Eén kort fragment kan nadruk dragen; een rij fragmenten die allemaal als quote bedoeld zijn is de tell. Houd het ene fragment dat de nadruk verdient en maak van de rest hele zinnen.

Signalen: `Snel. Simpel.` · `Geen gedoe. Gewoon antwoord.` · `Punt.` · `Klaar.` · `Dat is het. Meer is het niet.` · `En dat werkt.` · `Zo simpel is het.`

Voor: Snel. Simpel.

Na: Het is snel, en je hebt het in vijf minuten draaien.

Niet markeren: Fragmenten horen bij ondertitels, dialoog, notulen, changelogs en spreektaal. Eén los fragment als nadruk in een verder lopende tekst is stijl. Markeer bij twee of meer op rij die als klapper bedoeld zijn, en in zakelijke of encyclopedische tekst eerder dan in copy.

### Sjabloonzin (Of je nu X bent of Y) `template-phrase`

Ernst: **always** · Herkomst: translationese · en: `template-phrase`

Een invulzin met verwisselbare zelfstandige naamwoorden: het valse-breedtepaar (Of je nu starter bent of doorgewinterd architect), de vage stap (een belangrijke stap richting, een mooie stap vooruit) en de aforismeformule (de Uber van de hondenuitlaatbranche). De zin dekt iedereen af en zegt daarmee niets over deze lezer of deze verandering. Kies het publiek dat je echt aanspreekt, of noem de concrete verandering. De invulzin komt uit het Engelse Whether you're X or Y en heeft vaste Nederlandse varianten: of het nu gaat om X of Y, ongeacht of je, voor zowel starters als gevorderden.

Signalen: `Of je nu X bent of Y` · `Of het nu gaat om X of Y` · `voor iedereen die` · `een belangrijke stap richting` · `een mooie stap vooruit` · `de Uber van` · `de X van de Y-wereld` · `Of je nu beginner bent of expert` · `Ongeacht of je` · `Voor zowel starters als gevorderden`

Voor: Of je nu starter bent of doorgewinterd architect, deze gids is voor jou.

Na: Deze gids is voor engineers die hun eigen deploypijplijn beheren.

Niet markeren: Een echte tweedeling die de tekst daarna ook bedient ('Of je nu op Windows of macOS werkt, de stappen hieronder verschillen') is inhoud. Ook overslaan: citaten uit marketing van derden die je bespreekt, en vergelijkingen met een bedrijf die echt worden uitgewerkt. De constructie is correct Nederlands als de twee genoemde gevallen echt verschillen en de zin daarna voor allebei iets anders zegt. Het signaal is de alomvattende doelgroep in de openingszin.

### Cleft en loze kernwoorden (waar het om gaat is, het punt is dat) `cleft-dummy-noun`

Ernst: **cluster** · Herkomst: transfer · en: `cleft-dummy-noun`

Een bewering wordt naar voren geschoven via een cleft of een loos kernwoord in plaats van gewoon gezegd: Waar het om gaat is, Het punt is dat, Het feit is dat, De kern is dat, Wat opvalt is dat. De aanloop belooft nadruk die de mededeling zelf moet dragen. Schrijf de directe zin.

Signalen: `Waar het om gaat is` · `Het punt is dat` · `Wat belangrijk is, is dat` · `Het feit is dat` · `De kern is dat` · `Wat opvalt is dat` · `Belangrijk hierbij is` · `Het is zo dat`

Voor: Waar het om gaat is dat de cache warm is. Het punt is dat niemand hem met de hand warm houdt.

Na: De cache is warm, en niemand houdt hem met de hand warm.

Niet markeren: Een cleft die echt contrasteert met iets wat eerder stond ('Wat opvalt is niet de omzet, maar het aantal klachten' in een tekst die de omzet net besprak) doet werk. Ook overslaan: spreektaal, interviews en debatverslagen, waar de aanloop de beurt markeert.

### Koppelwerkwoord vermijden (fungeert als, beschikt over, herbergt) `copula-avoidance`

Ernst: **cluster** · Herkomst: transfer · en: `copula-avoidance`

Het gewone is, zijn of heeft wordt vervangen door een zwaardere stand-in die precies hetzelfde zegt: fungeert als, dient als, geldt als, vormt, staat symbool voor, kenmerkt zich door, beschikt over, herbergt, huisvest, is gelegen. Dezelfde opwaardering treft gewone werkwoorden: gebruikte wordt hanteerde, gaf wordt verstrekte, hielp wordt ondersteunde. Zet het koppelwerkwoord of hebben terug, tenzij een specifieker werkwoord echt betekenis toevoegt.

Signalen: `fungeert als` · `dient als` · `geldt als` · `vormt een belangrijk onderdeel van` · `staat symbool voor` · `kenmerkt zich door` · `wordt gekenmerkt door` · `beschikt over` · `herbergt` · `huisvest` · `biedt onderdak aan` · `is gelegen` · `vertegenwoordigt`

Voor: Het pand fungeert als ontmoetingsplek en beschikt over een zaal voor tachtig personen.

Na: In het pand komt de meetup samen. De zaal heeft tachtig stoelen.

Niet markeren: In encyclopedische en juridische tekst zijn 'is gelegen', 'geldt als' en 'beschikt over' gangbaar Nederlands; 'herbergt' en 'huisvest' zeggen bij gebouwen iets specifieks. Markeer alleen waar is of heeft hetzelfde zou zeggen, en bij dichtheid: drie of meer stand-ins in één alinea. Vakjargon en vaste juridische formules blijven staan.

### Gespiegelde zinnen en herhaalde zinsvormen `mirrored-clause-symmetry`

Ernst: **cluster** · Herkomst: transfer · en: `mirrored-clause-symmetry`

Twee of meer zinnen staan op hetzelfde grammaticale frame met alleen andere invulling, naast elkaar gezet voor contrast of een tweede geval. Daarnaast keert dezelfde zinsopbouw door de hele tekst terug, vaak met dezelfde woorden erin, wat langere stukken vlak maakt. Eén gespiegeld paar kan werken; de herhaling is de tell. Voeg de gevallen samen in één zin, of laat de helften in lengte en vorm verschillen.

Signalen: `Een winkelwagen is een object. Een chatruimte is een object.` · `Producten maken indruk; platforms geven ruimte.` · `De eerste fout kost tijd, de tweede kost vertrouwen.` · `twee zinnen met hetzelfde skelet naast elkaar` · `herhalende zinsstructuren` · `steeds terugkerende woorden`

Voor: Een winkelwagen is een object in het systeem. Een chatruimte is een object in het systeem.

Na: Winkelwagens en chatruimtes zijn allebei objecten in het systeem.

Niet markeren: Bewuste parallellie in een slotalinea, een gedicht, een spreuk of een juridische opsomming waarin de vorm de gelijkwaardigheid draagt. Ook: technische documentatie waarin elke regel per opzet dezelfde vorm heeft (API-beschrijvingen, changelogs). Geen regex: dit is een vormvergelijking tussen naburige zinnen, geen woordpatroon.

### Alle twijfel als kan `modal-flattening`

Ernst: **cluster** · Herkomst: transfer · en: `modal-flattening`

Elke schakering van onzekerheid wordt met hetzelfde hulpwerkwoord uitgedrukt, in het Nederlands vrijwel altijd kan of zou kunnen, zodat de hele tekst één toon van voorbehoud krijgt. Ook de mate verdwijnt: wat vrijwel zeker is en wat hoogst onwaarschijnlijk is krijgen dezelfde vorm. De oplossing is de twijfel variëren, niet weghalen: waarschijnlijk, vermoedelijk, naar verwachting, in de meeste gevallen, het is de vraag of.

Signalen: `zou kunnen` · `kan leiden tot` · `kan zorgen voor` · `kan bijdragen aan` · `kan helpen bij`

Voor: Deze aanpak kan mislukken. De kosten kunnen oplopen. De planning kan uitlopen.

Na: Deze aanpak mislukt waarschijnlijk. De kosten lopen op, en de planning schuift vermoedelijk een maand.

Niet markeren: Losse gevallen zijn gewoon Nederlands; 'kan' betekent daarnaast ook mogen en in staat zijn, en die betekenissen tellen niet mee. Poort op dichtheid: vier of meer voorbehoudsvormen met kan in één passage. In wetenschappelijke en juridische tekst is voorbehoud verplicht en zegt de dichtheid niets.

### Naamwoordstijl (het nemen van een besluit, overgaan tot) `nominalization-inflation`

Ernst: **cluster** · Herkomst: nl-bron · en: `nominalization-inflation`

Eén direct werkwoord wordt vervangen door een werkwoord plus abstract zelfstandig naamwoord: overgaan tot invoering voor invoeren, het nemen van een besluit voor besluiten, een bijdrage leveren aan voor helpen. De zin wordt langer en de handelende persoon verdwijnt vaak mee. Zet de werkwoordstam terug en noem wie wat doet. De vorm die in het Nederlands het hardst opvalt is het naamwoord met het en van, overgezet uit een Engelse -ing-vorm of een -tion-woord: helpen met het groeien van, bijdragen aan het waarborgen van.

Signalen: `het nemen van een besluit` · `tot stand brengen` · `een bijdrage leveren aan` · `in staat zijn om` · `de uitvoering van` · `de realisatie van` · `de implementatie van` · `overgaan tot invoering` · `het bieden van` · `het creëren van` · `het waarborgen van` · `het verbeteren van` · `bij het optimaliseren van` · `helpen met het groeien van` · `het navigeren van`

Voor: Het team is overgegaan tot uitstel van de lancering.

Na: Het team stelde de lancering uit.

Niet markeren: Naamwoordstijl is in ambtelijk en juridisch Nederlands zo dominant dat een treffer daar niets over de herkomst zegt; gebruik het patroon dan als schrijfregel, niet als machinebewijs. Ook overslaan: vaste vaktermen (de uitvoering van een vonnis, de realisatie van een bouwproject als projectterm) en citaten. Vaste vaktermen blijven staan: 'de implementatie van de AVG', 'het beheer van de infrastructuur', 'het bieden van eerste hulp' als benoemde taak. In juridische en procedurele tekst is de nominale vorm vaak de precieze. Het signaal is de nominalisatie terwijl handelende partij en handeling al in de zin staan.

### Verweesd aanwijzend voornaamwoord (Dit onderstreept ...) `orphaned-demonstrative`

Ernst: **cluster** · Herkomst: transfer · en: `orphaned-demonstrative`

Dit, dat of deze opent een zin als onderwerp zonder duidelijke verwijzing, meestal in de vorm Dit onderstreept of Dit laat zien na een alinea met meerdere beweringen. De lezer moet raden waar het naar terugslaat, en meestal slaat het nergens precies op terug. Noem waar het naar verwijst, of maak het echte onderwerp ook het grammaticale onderwerp.

Signalen: `Dit onderstreept` · `Dit laat zien dat` · `Dit betekent dat` · `Dat maakt duidelijk` · `Hiermee wordt` · `Dit alles` · `Dit toont aan dat`

Voor: Lezers volgen een tekst beter als het onderwerp klopt. Dit onderstreept het belang van de onderwerpskeuze.

Na: Wie het juiste onderwerp kiest, houdt de tekst helder.

Niet markeren: Een aanwijzend voornaamwoord dat onmiskenbaar naar de vorige zin verwijst is gewoon goed Nederlands en houdt alinea's aan elkaar. Ook overslaan: notulen en verslagen waarin 'dit' naar een genoemd besluit wijst. Markeer waar de vorige alinea meerdere kandidaten bevat, of waar de zin alleen betekenis toekent.

### Voorschrift zonder handelende persoon (er moet worden gekeken naar) `prescriptive-agentless-necessity`

Ernst: **cluster** · Herkomst: transfer · en: `prescriptive-agentless-necessity`

Verplichtingen stapelen zich op zonder dat iemand wordt genoemd: er moet worden gekeken naar, er is behoefte aan, het is noodzakelijk dat, verandering is nodig, hier valt winst te behalen. Niemand is aanspreekbaar, dus er verandert niets. Zet de handelende persoon en de handeling als onderwerp en gezegde, en wissel af met voorwaardelijke zinnen.

Signalen: `er moet worden gekeken naar` · `er dient te worden` · `er is behoefte aan` · `het is noodzakelijk dat` · `verandering is nodig` · `innovatie is nodig` · `hier valt winst te behalen`

Voor: Er moet worden gekeken naar het proces, en verandering is nodig.

Na: Het ontwikkelteam past de deployprocedure aan voor 1 oktober.

Niet markeren: In wetteksten, normen, bestekken en procedures is 'dient te worden' de conventie en staat de handelende persoon elders in het document. Ook overslaan: citaten uit beleidsstukken die je juist bespreekt. Markeer in gewoon proza, en vooral bij twee of meer verplichtingen zonder eigenaar in één alinea.

### Drieslag `rule-of-three`

Ernst: **cluster** · Herkomst: nl-bron · en: `rule-of-three`

Opsommingen komen stelselmatig in drieën, ook waar de werkelijkheid er twee of vier heeft: drie bijvoeglijke naamwoorden (snel, eenvoudig en betrouwbaar), drie abstracte zelfstandige naamwoorden (innovatie, inspiratie en inzicht), drie parallelle woordgroepen, een dubbele punt gevolgd door precies drie leden, of drie eenwoordzinnen met een punt ertussen (Snel. Simpel. Slim.). Een enkele drieslag is gewoon stijl; de tell is dat het aantal in de intro, de tussenkop en de slotzin drie blijft, en dat het derde lid niets toevoegt.

Signalen: `snel, eenvoudig en betrouwbaar` · `sneller, goedkoper, slimmer` · `helder, concreet en meetbaar` · `Helder, krachtig, overtuigend.` · `innovatie, inspiratie en inzicht` · `lezingen, panels en netwerkmogelijkheden` · `Snel. Simpel. Slim.` · `razendsnel, foutloos en verrassend goed opgebouwd` · `drie leden in elke opsomming in het stuk` · `X, Y én Z`

Voor: Het platform is snel, eenvoudig en betrouwbaar.

Na: Het platform laadt binnen 200 ms en draait sinds mei zonder storing.

Niet markeren: Een drieslag is een oud en legitiem Nederlands stijlmiddel, en Nederlandse tekstschrijvers gebruiken er zonder blikken of blozen één per stuk. Ook overslaan: echte opsommingen van precies drie dingen, vaste uitdrukkingen (Zon, zee, strand), slogans van derden en citaten. Markeer op dichtheid, en toets of het derde lid iets toevoegt.

### Zinnen op rij met dezelfde eindgroep `same-ending-runs`

Ernst: **cluster** · Herkomst: transfer · en: `same-ending-runs`

Drie of meer opeenvolgende zinnen sluiten op dezelfde werkwoordelijke eindgroep: kan worden verlaagd, moet worden aangepast, wordt mogelijk gemaakt. Het Nederlands zet het werkwoord toch al achteraan, dus zo'n reeks maakt het einde van elke zin identiek. Varieer de zinseinden en zet de lijdende vorm terug naar een bedrijvende zin met een handelende persoon.

Signalen: `kan worden ... / kan worden ... / kan worden ...` · `... mogelijk maakt. ... mogelijk maakt.` · `... wordt gedaan. ... wordt gedaan.` · `vier zinnen die op hetzelfde werkwoord eindigen` · `... te worden gerealiseerd. ... te worden gerealiseerd.`

Voor: Het proces kan worden versneld. De kosten kunnen worden verlaagd. De invoering kan worden vereenvoudigd.

Na: Het proces gaat sneller, kost minder en is makkelijker in te voeren.

Niet markeren: Beleidsstukken, normen en handleidingen herhalen de vorm soms met opzet, omdat elke regel dezelfde verplichting draagt. Ook overslaan: opsommingen, en twee zinnen achter elkaar. Het Koreaanse origineel gaat over zinseindmorfemen; in het Nederlands telt alleen de herhaalde werkwoordelijke eindgroep.

### Elliptische omslag (de data niet.) `stranded-auxiliary-contrast`

Ernst: **cluster** · Herkomst: transfer · en: `stranded-auxiliary-contrast`

Een omkering landt op een kaal ontkennend restje: De tool verdween, de data niet. Lezen ging goed. Schrijven niet. Het Engels strandt een hulpwerkwoord, het Nederlands laat het hele gezegde weg en houdt alleen niet over. Eén keer is prima; als terugkerend ritme gaat de afgeknipte tegenstelling voor verdiend inzicht door. Staat er al een in het stuk, schrijf de volgende dan voluit.

Signalen: `De tool verdween, de data niet.` · `Lezen ging goed. Schrijven niet.` · `Het team bleef. De afdeling niet.` · `, de rest niet.`

Voor: De tool verdween, de data niet.

Na: De tool verdween en de data bleef staan.

Niet markeren: Ellips is normaal in spreektaal, dialoog en ondertitels, en één keer in een stuk is stijl. Ook overslaan: een antwoord op een vraag ('Werkte de back-up? De database niet.') en citaten. Markeer bij een tweede geval in dezelfde tekst.

### Synoniemenverdubbeling (een belangrijke en cruciale rol) `synonym-doubling`

Ernst: **cluster** · Herkomst: transfer · en: `synonym-doubling`

Twee bijna-synonieme bepalingen of abstracte zelfstandige naamwoorden worden op één kern gekoppeld, zodat de woordgroep hetzelfde twee keer zegt: een belangrijke en cruciale rol, nieuw en innovatief, snel en efficiënt, de rol en functie van, kennis en kunde. De verdubbeling voelt als nadruk maar voegt geen betekenis toe. Houd er één.

Signalen: `een belangrijke en cruciale rol` · `nieuw en innovatief` · `duidelijk en helder` · `snel en efficiënt` · `veilig en betrouwbaar` · `de rol en functie van` · `de betekenis en waarde van` · `kennis en kunde`

Voor: Het team speelt een belangrijke en cruciale rol in het project.

Na: Het team bouwt de betaalmodule en beslist over de planning.

Niet markeren: Vaste woordparen en juridische tweelingen zijn geen verdubbeling maar idioom of vakterm: kennis en kunde in een cao, 'goed en deugdelijk werk' in een bestek, 'baat en schade'. Ook overslaan als de twee woorden echt verschillen (veilig gaat over de gebruiker, betrouwbaar over de uptime) en dat verschil in de tekst wordt gebruikt.

### Ontkennend staartje (, geen gedoe) `tailing-negation`

Ernst: **cluster** · Herkomst: transfer · en: `tailing-negation`

Een zin eindigt op een komma en een kort ontkennend staartje in plaats van een volledige bijzin: , geen gedoe, , geen giswerk, , zonder gedoe, , en niets meer. Het staartje voegt niets toe aan de mededeling en leest als slotslag uit reclametekst. Schrijf de beperking als echte bijzin of laat hem weg.

Signalen: `, geen gedoe` · `, geen giswerk` · `, geen verrassingen` · `, zonder gedoe` · `, en niets meer` · `, niet meer dan dat` · `, geen kleine lettertjes` · `, geen poespas`

Voor: De opties komen uit het geselecteerde item, geen giswerk.

Na: De opties komen uit het geselecteerde item, dus de gebruiker hoeft niets te raden.

Niet markeren: Een staartje dat een echte beperking noemt die de lezer nodig heeft ('werkt in de browser, geen app nodig') is inhoud. Ook overslaan in gesproken taal, ondertitels en citaten, en bij één enkel geval in een lange tekst.

### Lijdende vorm zonder handelende persoon en zinnen zonder onderwerp `agentless-passive-subjectless-fragment`

Ernst: **context** · Herkomst: transfer · en: `agentless-passive-subjectless-fragment`

De handelende persoon wordt verstopt of het onderwerp weggelaten: lijdende vormen zonder door-bepaling (De resultaten worden automatisch bewaard, Ondersteuning is toegevoegd) en zinnen zonder onderwerp of werkwoord (Geen configuratiebestand nodig). Vaak staat de constructie er om te vermijden dat gezegd moet worden wie iets deed. Noem wie het doet en schrijf bedrijvend.

Signalen: `wordt automatisch bewaard` · `is toegevoegd` · `er wordt gewerkt aan` · `er wordt gekeken naar` · `Geen configuratiebestand nodig.` · `Zonder installatie te gebruiken.` · `wordt ondersteund`

Voor: Geen configuratiebestand nodig. De resultaten worden automatisch bewaard.

Na: Je hebt geen configuratiebestand nodig. De cli bewaart de resultaten zelf.

Niet markeren: De lijdende vorm is gewoon Nederlands en soms de enige juiste keuze: als de handelende persoon onbekend is, niet ter zake doet, of als het lijdend voorwerp het onderwerp van de alinea is. Vakteksten, wetgeving en wetenschappelijk proza gebruiken hem per conventie. Markeer op dichtheid, niet op de losse zin.

### Eén zinsvorm door de hele tekst (te glad, even lang) `hypotactic-smoothness`

Ernst: **context** · Herkomst: nl-bron · en: `hypotactic-smoothness`

Elke zin loopt netjes af en is ongeveer even lang: geen fragment, geen zin die met En, Maar of Dus begint, geen afgebroken constructie, en bijzinnen die met komma's en 'en' aan elkaar worden geplakt tot een keten zonder duidelijk doel. Menselijke tekst is grillig: een korte zin, dan een lange die afdwaalt. Dit is vooral een bewaarregel, laat de ruige vormen staan waar de stem ze zou gebruiken, en repareer de vlakheid nooit met opzettelijke fouten.

Signalen: `geen zin begint met En` · `geen zin begint met Maar` · `geen zin begint met Dus` · `geen enkel fragment` · `zinnen van 15 tot 25 woorden` · `weinig variatie in zinslengte` · `onnatuurlijk lange zinnen aan elkaar geplakt met ', en'`

Voor: De build faalde; daarom is de commit teruggedraaid, waarna deze alsnog slaagde.

Na: De build faalde. Dus draaiden we de commit terug. En toen ging hij wel door.

Niet markeren: Formele registers vragen om gelijkmatige, afgeronde zinnen: wetgeving, normen, wetenschappelijke artikelen, jaarverslagen. Ook: vertaald werk en tekst die door een redacteur is gladgestreken. De komma voor 'en' tussen twee hoofdzinnen is correct Nederlands en op zichzelf geen signaal. Geen regex: dit is een afwezigheidspatroon dat een lezer moet vaststellen over een hele tekst.

### Zekerheid via dubbele ontkenning (niet onbelangrijk, niet optioneel) `litotes-confidence`

Ernst: **context** · Herkomst: transfer · en: `litotes-confidence`

Een bewering wordt gedaan door haar tegendeel te ontkennen: niet onbelangrijk, niet ongewoon, niet optioneel, niet te onderschatten. De claim wordt zo verondersteld in plaats van beweerd, en komt daarmee buiten discussie te staan. Waar een gewoon bevestigend woord bestaat, gebruik dat en geef de reden.

Signalen: `niet onbelangrijk` · `niet ongewoon` · `niet onlogisch` · `niet optioneel` · `niet te onderschatten` · `niet zonder reden` · `geen onverstandige keuze` · `niet onverdienstelijk`

Voor: Blind taggen is niet optioneel.

Na: Iedereen tagt blind, want anders wordt de steekproef scheef.

Niet markeren: Litotes is een oud stijlmiddel en in ironie of understatement precies de bedoeling. Ook overslaan: vaste uitdrukkingen ('niet voor niets', 'niet zonder slag of stoot'), citaten, en één enkel geval. Markeer bij twee of meer in dezelfde passage, of waar een gewoon bijvoeglijk naamwoord voorhanden was.

### Perfectum waar de verleden tijd hoort `past-tense-avoidance`

Ernst: **context** · Herkomst: transfer · en: `past-tense-avoidance`

Gebeurtenissen worden verteld in de voltooid tegenwoordige tijd (heeft besloten, is gestegen, hebben gekeken) waar verhalend of rapporterend Nederlands de onvoltooid verleden tijd gebruikt (besloot, steeg, keken). Het is de Engelse present perfect die één op één is overgezet. Drie of meer opeenvolgende zinnen in het perfectum is de tell; zet de verleden tijd terug waar de tekst vertelt wat er gebeurd is.

Signalen: `heeft besloten` · `hebben gekeken naar` · `is gestegen` · `zijn overgestapt` · `heeft ervoor gezorgd dat` · `drie zinnen op rij in het perfectum`

Voor: De vergadering heeft lang geduurd. We hebben geen besluit genomen.

Na: De vergadering duurde lang. We namen geen besluit.

Niet markeren: In spreektaal, in nieuwsberichten over iets wat net gebeurde en bij een resultaat dat nu nog geldt is het perfectum juist de goede tijd. Eén of twee perfecta zeggen niets. Geen regex: alleen de dichtheid over drie of meer opeenvolgende verhalende zinnen telt, en die moet een lezer wegen.

### Anafoor: drie zinnen met dezelfde opening `same-opener-runs`

Ernst: **context** · Herkomst: transfer · en: `same-opener-runs`

Drie of meer opeenvolgende zinnen beginnen met hetzelfde woord of dezelfde woordgroep (Misschien ... Misschien ... Misschien ...; Het is ... Het is ...). Bewuste anafoor is een stijlfiguur, maar een reeks die geen overtuigingswerk doet is een machinepatroon. Houd de eerste zin, voeg de rest samen of begin bij de handeling.

Signalen: `Misschien ... Misschien ... Misschien ...` · `Ze gaan ervan uit dat ... Ze gaan ervan uit dat ...` · `Het is ... Het is ... Het is ...` · `Wij geloven ... Wij geloven ...` · `Elke ... Elke ... Elke ...`

Voor: Misschien had niemand het nodig. Misschien loste het het verkeerde probleem op. Misschien klopte de timing niet.

Na: Misschien had niemand het nodig, of loste het het verkeerde probleem op. De timing hielp ook niet mee.

Niet markeren: Anafoor in een toespraak, een gedicht of een bewust ritmische passage doet echt werk. Ook overslaan: opsommingen en bullets die per opzet gelijk beginnen, notulen en changelogs, en twee zinnen achter elkaar (pas vanaf drie is het een reeks).

## Retorische zetten en toon

### Aangekondigde interesse `announced-interest`

Ernst: **always** · Herkomst: transfer · en: `announced-interest`

Een aankondiging claimt een reactie die de tekst nog niet heeft verdiend: Wat mij opviel, Wat me verbaasde, Hier wordt het interessant, Ik was verrast te zien dat. Bijvorm: het deelbericht dat opent met de claim dat het onderwerp de schrijver al dagen bezighoudt (de zin die bij me blijft hangen, hier denk ik al de hele week over na) voordat de lezer een reden heeft om te kijken. Het werkt alleen als er echt verrassende gegevens volgen; begin anders bij het ding zelf.

Signalen: `Wat mij opviel` · `Wat me verbaasde` · `Wat me raakte` · `Dit vond ik interessant` · `Hier wordt het interessant` · `Ik was verrast te zien dat` · `Het interessantste deel` · `de zin die bij me blijft hangen` · `ik moet hier steeds aan denken` · `hier denk ik al de hele week over na` · `dit blijft door mijn hoofd spelen`

Voor: Wat mij opviel: de helft van de aanmeldingen kwam uit Hengelo. Ik moet hier steeds aan denken.

Na: De helft van de aanmeldingen kwam uit Hengelo.

Niet markeren: In een persoonlijk verslag of een leeslog is de eigen reactie het onderwerp; daar hoort ze. Niet markeren als er meteen een cijfer of feit volgt dat de verbazing rechtvaardigt en de lezer die deelt.

### Aforismesjabloon `aphorism-formula`

Ernst: **always** · Herkomst: transfer · en: `aphorism-formula`

Een gewone bewering wordt omgegoten tot citeerbare wetmatigheid door een invulmetafoor: X is de taal van Y, de munt van Z, de architectuur van vertrouwen, X is de Excel van de agents. Bijvorm: het transformatieframe dat een verschuiving dramatiseert (van X naar Y, voorbij X richting Y). De vorm doet het overtuigingswerk in plaats van bewijs.

Signalen: `is de taal van` · `is de munt van` · `de architectuur van vertrouwen` · `wordt een valkuil` · `is geen tool maar een spiegel` · `de Excel van` · `van X naar Y` · `voorbij X richting Y`

Voor: Documentatie is de munt van vertrouwen in een open source-project.

Na: Wie de documentatie bijhoudt, krijgt bruikbare bugmeldingen terug.

Niet markeren: Een gevestigde vakterm die toevallig deze vorm heeft ('de taal van het web' over HTML) is geen sjabloon. Citaten en boektitels blijven staan. In poëzie en reclame is de vorm het doel.

### Aforistische slotzin `aphoristic-ender`

Ernst: **always** · Herkomst: transfer · en: `aphoristic-ender`

Een alinea of stuk landt op een compacte spreuk die het punt als wijsheid herhaalt in plaats van iets toe te voegen: En dat telt. Zo simpel is het. De toekomst is al begonnen. Daar begint het pas. Bijvormen zijn het contrastslot (X, geen Y) en de oproep tot actie. Schrap hem in plaats van hem te herschrijven naar een betere beeldspraak, en eindig op de helderste concrete zin die al in het stuk staat.

Signalen: `En dat telt.` · `Zo simpel is het.` · `De toekomst is al begonnen.` · `Daar begint het pas.` · `Nu is het moment om` · `En dat is precies het punt.`

Voor: De zaal zat vol en de talks liepen uit. En dat telt.

Na: De zaal zat vol en de talks liepen uit.

Niet markeren: Een spreekwoord in een citaat of een slogan die het onderwerp van het stuk is, blijft staan. Een column mag op een grap eindigen; de tell is de spreuk die alleen herhaalt wat er al stond.

### Slot dat de lezer om een reactie of een handeling vraagt `call-to-action-closer`

Ernst: **always** · Herkomst: nl-bron · en: `call-to-action-closer`

De post eindigt met een vraag aan de lezer die op elke post zou passen en niets over het onderwerp vraagt. Nederlandse vormen zijn vaak letterlijke vertalingen van 'What do you think? Share your thoughts in the comments'. Vaak volgt er een even voorspelbare reactie onder: 'Interessant perspectief, dank voor het delen'. Naast de vraag staan de instructie en de uitnodiging: Bewaar deze post, Doe jezelf een plezier en lees dit, Laten we connecten, Volg mij voor meer, en het beleidsstuk dat elke alinea op een oproep laat eindigen.

Signalen: `Wat denk jij?` · `Wat is jouw ervaring?` · `Deel je gedachten in de reacties` · `Laat het weten in de comments` · `Herkenbaar?` · `Ben jij het ermee eens?` · `Thoughts?` · `Agree?` · `Hoe zie jij dat?` · `Zeker de moeite waard:` · `Bewaar deze post.` · `Doe jezelf een plezier en lees dit.` · `Laten we connecten!` · `Stuur me gerust een bericht` · `Volg mij voor meer` · `Deel het in de reacties` · `er moet iets gebeuren`

Voor: Wat denk jij? Deel je gedachten in de reacties!

Na: Als je dit anders aanpakt, hoor ik graag welke stap je overslaat.

Niet markeren: Een echte vraag aan een specifiek publiek die de schrijver zelf niet kan beantwoorden is geen signaal: 'wie heeft er een zaal voor zestig man in Hengelo?' Een enquête, een oproep om hulp of een vraag met een deadline hoort er ook bij. Ook een forum- of communitypost die om ervaringen vraagt omdat dat het doel van de post is. Een handleiding hoort de lezer op te dragen wat te doen. Een aanmeldknop of nieuwsbrieffooter is functioneel. De tell is de oproep die niets toevoegt aan een informatieve tekst, of die alleen de schrijver dient.

### Oprechtheidsvlag `candor-flag-opener`

Ernst: **always** · Herkomst: transfer · en: `candor-flag-opener`

Een geënsceneerde pauze of aangekondigde openhartigheid gaat vooraf aan een gewoon punt: Eerlijk?, Even eerlijk, Kijk, Laten we eerlijk zijn, De harde waarheid is. Bijvorm: de schrijver kondigt zijn openheid aan in plaats van open te zijn (Ik wil vooraf eerlijk zijn:, Volledige transparantie:, Ik had dit kunnen weglaten, maar). Het frame suggereert dat de rest minder eerlijk was en is los te knippen van de inhoud: haal het weg en de zin verliest geen informatie.

Signalen: `Eerlijk?` · `Eerlijk gezegd` · `Even eerlijk` · `Kijk,` · `Laten we eerlijk zijn` · `Ik zal eerlijk zijn` · `De harde waarheid is` · `Om maar meteen met de deur in huis te vallen` · `Het zit zo:` · `Het eerlijke antwoord is` · `Ik wil vooraf eerlijk zijn:` · `Voor de volledigheid:` · `Volledige transparantie:` · `die ik liever nu noem dan dat je ze later ontdekt` · `Ik had dit kunnen weglaten, maar` · `En ja, ik ben`

Voor: Eerlijk? De eerste editie liep niet lekker. Volledige transparantie: we hadden te weinig stoelen.

Na: De eerste editie liep niet lekker. We hadden te weinig stoelen.

Niet markeren: In gesproken taal en in een interviewcitaat is 'eerlijk gezegd' gewoon spreektaal; laat citaten staan. Als de zin daarna echt iets toegeeft dat de schrijver schaadt, doet de vlag werk. 'Voor de volledigheid' in een notulen of changelog waar echt een ontbrekend punt volgt is functioneel.

### Contrastslogan als opening of kop `contrast-slogan-opener`

Ernst: **always** · Herkomst: nl-bron · en: `contrast-slogan-opener`

Een tweedelige contrastslogan staat als eerste regel of kop van een tekst en bepaalt het ding door te zeggen wat het niet is: Eén avond, geen verkooppraatje. De opening hoort te zeggen wat er gebeurt; wat het niet is hoort verderop in een eigen blok, als het al ergens hoort. De constructie zelf staat onder syntax; deze regel gaat over het gebruik op de kopregel.

Signalen: `X, geen Y` · `Eén avond, geen verkooppraatje.` · `Gewoon code, geen praatjes.` · `Geen praatjes, wel werkende software.`

Voor: Eén avond, geen verkooppraatje.

Na: Twee talks, wat te eten, en daarna tijd om bij te praten.

Niet markeren: Middenin een tekst is een contrast gewoon een contrast; deze regel geldt voor de eerste regel, de kop of de ondertitel. Een opsommingsregel in een lijst met kenmerken is geen slogan. Bestaande, geratificeerde slogans van een merk blijven staan.

### Schijndiepzinnigheid `false-profundity-truism`

Ernst: **always** · Herkomst: transfer · en: `false-profundity-truism`

Een zin heeft de vorm van inzicht, een tegenstelling of een omkering, maar bevat niets waar een lezer iets mee kan of het mee oneens kan zijn: Verandering is de enige constante. Uiteindelijk zijn we allemaal mensen. Niets is zwart-wit. Het zijn de veiligst mogelijke zinnen, waar van iedereen en dus van niemand. Vervang door de concrete bewering, of schrap.

Signalen: `Verandering is de enige constante.` · `Uiteindelijk zijn we allemaal mensen.` · `Iedereen twijfelt weleens.` · `Het begint bij jezelf.` · `Niets is zwart-wit.`

Voor: Bij het organiseren van een meetup komt veel kijken. Niets is zwart-wit.

Na: Bij een meetup gaat de meeste tijd naar de zaal en de sprekers.

Niet markeren: Als citaat of als aangehaalde dooddoener die de schrijver vervolgens afbreekt, blijft de zin staan. In troostende of ceremoniële teksten (condoleance, toespraak) is de open deur het genre.

### Valse spanning en uitgestelde clou `false-suspense-hook`

Ernst: **always** · Herkomst: transfer · en: `false-suspense-hook`

Een kort zinsdeel maakt spanning rond informatie die dat niet nodig had: Het addertje?, Hier komt het:, En nu wordt het interessant, Het mooiste?, En dan komt de clou. Bijvorm: de tekst praat om het onderwerp heen en bouwt op naar een punt dat pas laat of nooit komt, met achtergrond die niemand vroeg. Schrap de haak en zeg het.

Signalen: `Het addertje?` · `Hier komt het:` · `En nu wordt het interessant` · `Het mooiste?` · `Het gekke?` · `En dan komt de clou` · `Wat de meeste mensen missen` · `En dan dit:` · `eerst wat achtergrond` · `een opbouw creëren` · `om het onderwerp heen praten`

Voor: We probeerden van alles. Het addertje? De DNS stond nog op de oude server.

Na: We probeerden van alles. De DNS stond nog op de oude server.

Niet markeren: Verhalende journalistiek en column mogen spanning opbouwen als er ook echt een onthulling volgt. Niet markeren in een tekst die per genre op suspense draait (recensie van een thriller, reportage). Eén haak in een lang stuk is stijl; drie is een sjabloon.

### Nietszeggend slot `generic-conclusion`

Ernst: **always** · Herkomst: transfer · en: `generic-conclusion`

Een slotzin wijst naar de toekomst of naar zekerheid zonder een bewering die iemand kan nakijken: De toekomst ziet er rooskleurig uit, De tijd zal het leren, Eén ding is zeker, We kijken uit naar wat komt. De toekomstvariant heeft een vaste vorm: hulpwerkwoord plus worden plus een vaag kernwoord (wordt misschien wel hét verhaal van de komende jaren, belooft de standaard te worden). Vervang door een toetsbare versie of schrap.

Signalen: `De toekomst ziet er rooskleurig uit` · `De tijd zal het leren` · `De toekomst zal het uitwijzen` · `Eén ding is zeker` · `We kijken uit naar wat komt` · `wordt misschien wel hét verhaal van` · `belooft de standaard te worden` · `Wordt ongetwijfeld vervolgd`

Voor: Of dit werkt, de tijd zal het leren. Eén ding is zeker: de vraag is er.

Na: Of dit werkt, weten we na de derde editie. We tellen de aanmeldingen per keer.

Niet markeren: In een nieuwsbericht over een lopende zaak mag een slot open blijven als de onzekerheid het onderwerp is en de tekst benoemt wat er beslist gaat worden. Citaten blijven staan.

### De tekst aankondigen in plaats van schrijven `meta-signposting`

Ernst: **always** · Herkomst: transfer · en: `meta-signposting`

De tekst vertelt wat hij gaat doen in plaats van het te doen. Subvormen: de openingsaankondiging (In dit artikel verkennen we, In deze gids behandelen we, We behandelen achtereenvolgens), de gezamenlijke overgang (Laten we beginnen, Nu naar het volgende punt), de structuurpraat in de tekst zelf (zoals eerder genoemd, hieronder een overzicht, dit valt uiteen in drie delen), en het antwoord dat de vraag eerst parafraseert en daarna samenvat wat er net stond (Kortom, Samengevat). Begin gewoon.

Signalen: `In dit artikel verkennen we` · `Dit artikel verkent` · `In dit artikel bespreken we` · `In deze gids behandelen we` · `In dit blog leer je` · `In deze blog neem ik je mee` · `In deze blog vertel ik` · `Hieronder bespreken we` · `We behandelen achtereenvolgens` · `Hieronder een overzicht` · `Zoals eerder genoemd` · `Dit valt uiteen in drie delen` · `Laten we beginnen` · `Allereerst kijken we naar` · `Vier kanttekeningen vooraf` · `Kortom` · `Samengevat` · `Je vraagt je af of`

Voor: In dit artikel verkennen we hoe je een meetup organiseert. We behandelen achtereenvolgens locatie, sprekers en catering. Laten we beginnen.

Na: Een meetup vraagt om een zaal en twee sprekers; de broodjes bestel je een week vooraf.

Niet markeren: Een inhoudsopgave, een leeswijzer in een rapport of een abstract is bewegwijzering met een functie. Wetenschappelijke artikelen kondigen hun opzet af in de inleiding; dat is genrenorm. Een terugverwijzing die de lezer echt nodig heeft ('de tabel in hoofdstuk 2') is geen tell.

### Reflexmatige AI-bescheidenheid `reflexive-ai-humility`

Ernst: **always** · Herkomst: transfer · en: `reflexive-ai-humility`

De schrijver meldt dat hij zelf een taalmodel is, of dat zijn beweringen wel eens onjuist kunnen zijn, als gebaar van bescheidenheid in plaats van als grens om een concrete bewering: als taalmodel, dit stuk is geschreven door een van de systemen die het beschrijft, het meeste hierboven is een indruk en kan onjuist zijn. Zelfidentificatie hoort nooit in een tekst met een menselijke stem; vervang de tweede vorm door de bewering die onzeker is, met de reden.

Signalen: `als taalmodel` · `als AI` · `geschreven door een taalmodel` · `dit is een indruk en kan onjuist zijn` · `ik kan me hierin vergissen`

Voor: Als taalmodel kan ik me hierin vergissen, maar de meetup is op 7 oktober.

Na: De meetup is op 7 oktober. De datum staat in de aankondiging van 2 september.

Niet markeren: Een tekst die over taalmodellen gaat mag 'als taalmodel' citeren of bespreken. Een expliciete AI-disclosure onderaan een document is beleid, geen tell; het gaat om de bescheidenheidsfrase midden in de lopende tekst.

### Claim van verzwegen kennis `scarcity-of-knowledge-claim`

Ernst: **always** · Herkomst: transfer · en: `scarcity-of-knowledge-claim`

De tekst beweert dat haar punt onopgemerkt, verborgen of weggemoffeld is terwijl daar geen sprake van is: wat niemand je vertelt, waar niemand het over heeft, het punt dat iedereen mist, wat de meeste mensen fout doen, dit slaat bijna iedereen over. Het vleit de schrijver als enige kenner en blaast de nieuwswaarde op.

Signalen: `wat niemand je vertelt` · `waar niemand het over heeft` · `het punt dat iedereen mist` · `wat de meeste mensen fout doen` · `dit slaat bijna iedereen over` · `het stuk dat vaak vergeten wordt`

Voor: Wat niemand je vertelt over meetups: de catering is het lastigste.

Na: De catering kost de meeste tijd bij het organiseren van een meetup.

Niet markeren: Bij echt weinig gedocumenteerde kennis mag de schrijver dat zeggen, als hij erbij zet waar hij het wél vandaan heeft. Onderzoeksjournalistiek die aantoont dat iets verzwegen werd, doet precies dat.

### Betekenis aankondigen en eigen punten rangschikken `significance-signaling`

Ernst: **always** · Herkomst: transfer · en: `significance-signaling`

De tekst vertelt de lezer dat iets opmerkelijk of belangrijk is in plaats van het te laten zien. Subvormen: het redactionele commentaar dat aankondigt dat iets vermeld gaat worden (het is belangrijk om op te merken dat, het is vermeldenswaard dat), de rechtvaardiging die vóór de bewering komt die ze moet dragen (dit is belangrijk, omdat, zoals je ziet) en de zelfrangschikking waarin de schrijver aanwijst welk van zijn eigen punten het slimme of verrassende is (het belangrijkste punt is, dat is precies het punt, en dat telt). Zet de bewering vooraan en schrap de aankondiging.

Signalen: `het is belangrijk om op te merken dat` · `het is belangrijk te beseffen dat` · `het is vermeldenswaard dat` · `opmerkelijk genoeg` · `het is goed om te bedenken dat` · `geen bespreking is compleet zonder` · `men mag niet vergeten dat` · `het valt niet te ontkennen dat` · `dit is belangrijk, omdat` · `dat laatste is belangrijker dan het klinkt` · `zoals je ziet` · `het belangrijkste punt is` · `dit onderscheid doet ertoe` · `en dat doet ertoe` · `dit is het interessantste stuk` · `dat laatste is het verrassende` · `dat is precies het punt` · `en dat telt` (+2)

Voor: Het is belangrijk om op te merken dat de meetup gratis is. Dit is belangrijk, omdat drempels mensen weghouden.

Na: De meetup is gratis en aanmelden hoeft niet.

Niet markeren: Handleidingen en juridische teksten mogen aandacht vestigen op een uitzondering die de lezer anders mist. In lesmateriaal is 'let hier op' functioneel als het echt om een valkuil gaat. Niet markeren waar de aankondiging informatie draagt die de zin zonder haar verliest.

### Gestapelde slagen om de arm `stacked-hedges`

Ernst: **always** · Herkomst: transfer · en: `stacked-hedges`

Twee of meer voorbehouden op één gezegde tot het niets meer zegt: het zou mogelijk kunnen zijn dat, er is wellicht een kans dat het misschien, hoewel dit kan verschillen is het over het algemeen in de meeste gevallen goed om op te merken. Bijvormen: de gestapelde voorspelling (zou uiteindelijk kunnen), het terzijde tussen haakjes (en, in toenemende mate, Z) en het etiket dit is een aanname. Houd precies één voorbehoud dat de bron ondersteunt.

Signalen: `zou mogelijk kunnen` · `er is wellicht een kans dat` · `hoewel dit kan verschillen` · `over het algemeen, in de meeste gevallen` · `zou uiteindelijk kunnen` · `(en, in toenemende mate, ...)` · `dit is een aanname`

Voor: Het zou mogelijk kunnen dat de opkomst wellicht iets lager uitvalt.

Na: De opkomst valt misschien lager uit; in oktober kwamen er minder aanmeldingen binnen.

Niet markeren: Wetenschappelijke en medische teksten stapelen soms terecht: onzekerheid over de meting én over het effect zijn twee dingen. Juridische teksten hedgen per conventie. Markeer alleen als de voorbehouden dezelfde onzekerheid herhalen.

### Opgeblazen inzet `stakes-inflation`

Ernst: **always** · Herkomst: transfer · en: `stakes-inflation`

Het belang van het onderwerp wordt opgeblazen tot ver voorbij wat de inhoud draagt: een kleine wijziging verandert alles, een stuk over prijzen wordt een beschouwing over de toekomst van de samenleving. Subvormen: de wereldschaalclaim (zet de wereld op zijn kop, bepaalt het komende decennium, fundamenteel veranderen hoe we), de urgentiestempel (nu meer dan ooit, de inzet was nog nooit zo hoog) en de alledaagse blunder als levensdrama. De belofte wordt nooit ingelost in de rest van de tekst.

Signalen: `verandert alles` · `veranderde alles` · `zet de wereld op zijn kop` · `bepaalt het komende decennium` · `de inzet was nog nooit zo hoog` · `nu meer dan ooit` · `fundamenteel veranderen hoe we` · `in een wereld waarin alles` · `ongekend` · `drastisch veranderen` · `superkrachten` · `Wat. Een. DRAMA.`

Voor: Deze update verandert alles aan hoe we software bouwen. De inzet was nog nooit zo hoog.

Na: Na deze update draait de build in vier minuten in plaats van elf.

Niet markeren: Niet markeren bij een gebeurtenis die aantoonbaar van schaal veranderde en waar het stuk dat ook laat zien met cijfers. Citaten uit marketingmateriaal die je aanhaalt blijven staan. In fictie en column is overdrijving een stijlmiddel; daar telt alleen de herhaling.

### Vleierij vooraf `sycophancy`

Ernst: **always** · Herkomst: transfer · en: `sycophancy`

Lof voor de vrager, zijn vraag of zijn gevoel gaat vooraf aan het antwoord: Goede vraag, Wat een mooie vraag, Je hebt helemaal gelijk, Dat is een scherpe observatie. Bijvormen: de gespeelde inleving (Ik begrijp helemaal hoe je je voelt) en het stempel dat een correctie bevestigt en meteen een betere versie belooft. Schrap de lof en geef antwoord.

Signalen: `Goede vraag!` · `Goede en terechte vraag` · `Wat een goede vraag` · `Wat een mooie vraag` · `Je hebt helemaal gelijk` · `Dat is een scherpe observatie` · `Terecht punt` · `Goed dat je dit aankaart` · `fijn dat je dat kritisch vraagt` · `Ik begrijp helemaal hoe je je voelt` · `Interessant perspectief`

Voor: Goede vraag! Je hebt helemaal gelijk dat dit vaak misgaat. De oorzaak zit in de cache.

Na: De oorzaak zit in de cache.

Niet markeren: In een echt gesprek mag iemand instemmen: 'je hebt gelijk' na een aangewezen fout is gewoon toegeven. De tell is de lof vóór de inhoud, als opening, zonder dat er iets mee gebeurt. Citaten uit een chatlog die je analyseert blijven staan.

### Stellige toon zonder grond `booster-density-nl`

Ernst: **cluster** · Herkomst: nl-bron

Beweringen worden versterkt met zekerheidswoorden waar geen bewijs bij staat, en zelden voorzichtig geformuleerd, waardoor de tekst overmoedig klinkt: ongetwijfeld, zonder twijfel, absoluut, uiteraard, zeker weten. Verwant zijn de holle versterkers die alleen als vulling staan (echt, gewoon, simpelweg). De tell is de dichtheid en het ontbreken van de onderbouwing waar het versterkte woord om vraagt.

Signalen: `ongetwijfeld` · `zonder twijfel` · `zonder enige twijfel` · `zeker weten` · `absoluut` · `uiteraard` · `echt` · `gewoon` · `simpelweg`

Voor: Dit is ongetwijfeld de beste aanpak en zonder twijfel de snelste route.

Na: Deze aanpak was in onze test de snelste. We hebben er twee vergeleken.

Niet markeren: Een stellige uitspraak met bewijs in dezelfde alinea is gewoon een bewering; stelligheid op zich is eerder een menselijke tegenindicator. 'Gewoon' en 'echt' zijn in spreektaal normale partikels. Markeer op dichtheid en op het ontbreken van grond.

### Gespeelde balans `both-sides-hedge`

Ernst: **cluster** · Herkomst: transfer · en: `both-sides-hedge`

De symmetrische beweging critici zeggen X, voorstanders zeggen Y, de waarheid ligt in het midden speelt nuance zonder iets te beweren, samen met de veilige woordenschat van niet-kiezen (beide kanten, voor- en nadelen, het is een kwestie van balans) vanaf vier keer per document. Bijvorm: de tekst mijdt elke controverse en blijft afstandelijk objectief, ook waar een standpunt het interessant zou maken, en maakt voor- en nadelenlijstjes even lang terwijl het bewijs scheef ligt. Kies een kant, geef een concrete vergelijking, of maak de bewering afhankelijk van iets wat de lezer kan nakijken.

Signalen: `de waarheid ligt in het midden` · `beide kanten hebben een punt` · `aan de ene kant ... aan de andere kant` · `voor- en nadelen` · `critici stellen ... voorstanders wijzen op` · `het is een kwestie van balans` · `neutraal en objectief van toon` · `zelden een controversieel standpunt`

Voor: Critici stellen dat het te duur is, voorstanders wijzen op de voordelen. De waarheid ligt in het midden.

Na: Het kost 400 euro per editie. Voor dat bedrag heb je de zaal en het eten.

Niet markeren: Encyclopedische en journalistieke neutraliteit is een norm, geen tell: hoor en wederhoor met bronnen blijft staan. Een echte afweging met twee onderbouwde kanten is een argument. Markeer de symmetrie die geen bron heeft en niets kiest.

### Gladde gevolgtrekking `clean-consequence-connector`

Ernst: **cluster** · Herkomst: transfer · en: `clean-consequence-connector`

Een verbindingswoord beweert dat de conclusie vanzelf uit het voorgaande volgt en leent daarmee onvermijdelijkheid die het betoog niet heeft verdiend: volgt direct uit, komt hier rechtstreeks uit voort, leidt uiteindelijk tot, daarmee is het duidelijk. Laat de redenering zien, of vervang het verbindingswoord door de stap die de conclusie oplevert.

Signalen: `volgt direct uit` · `komt hier rechtstreeks uit voort` · `vloeit voort uit` · `leidt uiteindelijk tot` · `daarmee is het duidelijk` · `en dus is`

Voor: Uit de cijfers volgt direct dat de campagne werkte. Daarmee is het duidelijk.

Na: Na de campagne kwamen er 40 aanmeldingen bij, tegen 12 in de maand ervoor.

Niet markeren: In wiskunde, logica en juridische redeneringen volgt iets soms echt direct uit het voorgaande; daar is de formulering vakjargon. Niet markeren als de tussenstap in dezelfde alinea staat.

### Aanloop, dubbele punt, clou `colon-reveal`

Ernst: **cluster** · Herkomst: transfer · en: `colon-reveal`

Een aanloopzin, een dubbele punt en dan een keurig ingepakte onthulling in kleine letters. De dubbele punt wordt gebruikt voor spanning in plaats van om een lijst, een label of een citaat in te leiden, en het patroon herhaalt zich alinea na alinea. Schrijf het als een gewone zin.

Signalen: `Het detail dat het laat werken:` · `Wat het verschil maakt:` · `De reden dat het werkt:` · `En dat brengt ons bij het echte punt:` · `zelfstandig naamwoord plus dubbele punt plus onthulling in kleine letters`

Voor: Wat het verschil maakt: de zaal is gratis.

Na: De zaal is gratis.

Niet markeren: Een dubbele punt vóór een opsomming, een citaat, een definitie of een label (Datum: 7 oktober) is normale interpunctie. Koppen met een ondertitel na de dubbele punt zijn genrenorm. Eén onthullende dubbele punt in een stuk is geen patroon; tel ze per duizend woorden.

### Diepere-waarheidsframe `deeper-truth-framing`

Ernst: **cluster** · Herkomst: transfer · en: `deeper-truth-framing`

Een vaste frase presenteert een gewoon punt als verborgen of fundamenteel inzicht, of beweert dat de zaak duidelijk is in plaats van het te laten zien: De echte vraag is, Waar het werkelijk om draait, Vergis je niet, De waarheid is, Het echte verhaal is, De kern van de zaak is. Laat het frame vallen en zeg het punt.

Signalen: `De echte vraag is` · `Waar het werkelijk om draait` · `In werkelijkheid` · `Vergis je niet` · `De waarheid is` · `De realiteit is simpeler` · `Het echte verhaal is` · `De kern van de zaak is`

Voor: De echte vraag is niet welke tool je kiest. Waar het werkelijk om draait, is wie hem onderhoudt.

Na: Welke tool je kiest maakt minder uit dan wie hem onderhoudt.

Niet markeren: In een betoog dat een aangewezen misverstand corrigeert, doet 'in werkelijkheid' echt werk; laat het staan als er een concrete tegenspraak volgt. Niet markeren in citaten of in polemiek waar de schrijver een genoemde tegenstander weerlegt.

### Nagespeelde spreektaal `fake-casual-register`

Ernst: **cluster** · Herkomst: transfer · en: `fake-casual-register`

Het kostuum dat een model aantrekt als om een losse toon wordt gevraagd: een kist met rekwisieten die het drama uitbesteden aan de rekwisiet. Terugkerende vormen zijn het eenwoordoordeel als slot (bizar., waanzinnig.), de regieaanwijzing tussen sterretjes (*checkt notities*), het knipoogje tussen haakjes (ja, echt), de labelopening (hot take:, leuk weetje:, pro tip:) en het nagespeelde vraaggesprek. Vervang de rekwisiet door de concrete verrassing.

Signalen: `bizar.` · `waanzinnig.` · `*checkt notities*` · `*mic drop*` · `(ja, echt)` · `(nee, serieus)` · `hot take:` · `leuk weetje:` · `pro tip:` · `onpopulaire mening:` · `want natuurlijk`

Voor: Pro tip: zet de aanmelding open voordat je de sprekers rond hebt. (Ja, echt.) Bizar.

Na: Zet de aanmelding open voordat de sprekers rond zijn. Dan weet je of er animo is.

Niet markeren: In chatlogs, forumcitaten en ondertitels is dit gewoon hoe mensen schrijven; laat citaten staan. Markdown-nadruk met sterretjes in broncode of documentatie is opmaak, geen regieaanwijzing. Eén losse 'bizar' na een echt bizar cijfer is stem, geen rekwisiet.

### Vlak affect `flat-affect`

Ernst: **cluster** · Herkomst: transfer · en: `flat-affect`

Eén toon wordt een heel stuk lang vastgehouden zonder verschuiving van analytisch naar boos naar zacht, de cadans varieert nooit, en de tekenen van een sprekende stem worden dunner: minder vragen, minder terzijdes, minder directe aanspraak. Naast menselijk schrijven in hetzelfde genre leest het tegelijk gelijkmatig warm en gelijkmatig afstandelijk. Laat het register meebewegen met het onderwerp.

Signalen: `geen registerwissel` · `cadans varieert nooit` · `weinig terzijdes` · `geen directe aanspraak` · `overal dezelfde zinslengte`

Voor: De storing duurde drie uur. Wij betreuren het ongemak. De oorzaak lag in de databaselaag. Wij nemen maatregelen.

Na: De storing duurde drie uur en het was onze eigen schuld. We hadden de back-up nooit getest. Sinds vorige week gebeurt dat elke maandag.

Niet markeren: Structureel patroon over een hele tekst; nooit op één zin te markeren. Handleidingen, normen en juridische teksten horen vlak te zijn. Vergelijk met menselijk schrijven in hetzelfde genre voordat je dit noteert.

### Stapel historische vergelijkingen `historical-analogy-stacking`

Ernst: **cluster** · Herkomst: transfer · en: `historical-analogy-stacking`

Een snelle opsomming van vroegere technieken, bedrijven of omwentelingen wordt aangehaald om hun gewicht te lenen: net als de boekdrukkunst, de telegraaf en het internet, elke grote technologische omwenteling, denk aan Spotify, of aan Uber. De montage vervangt het argument en geen enkele parallel wordt onderzocht. Noem de ene vergelijking die werk doet en zeg wat ze verklaart.

Signalen: `net als de boekdrukkunst` · `de telegraaf` · `de stoommachine` · `elke grote technologische omwenteling` · `volgde hetzelfde patroon` · `denk aan Spotify` · `net zoals Uber`

Voor: Net als de boekdrukkunst en de stoommachine verandert dit alles; elke grote technologische omwenteling volgde hetzelfde patroon.

Na: Redacteuren gebruiken het nu vooral om ruwe transcripties op te schonen.

Niet markeren: Historische en technologiehistorische artikelen noemen de boekdrukkunst en de stoommachine als onderwerp; dat is geen vergelijking. Eén uitgewerkte parallel met bron is een argument. De tell is de reeks zonder analyse.

### Belang en symboliek aanplakken `importance-labelling`

Ernst: **cluster** · Herkomst: nl-bron · en: `importance-labelling`

Een etiket beweert dat het onderwerp belangrijk, cruciaal of symbolisch is, in plaats van te laten zien waarom. Subvormen: het gewichtwoord op de bewering geplakt (van cruciaal belang, essentieel, van onschatbare waarde), de rolzin (speelt een cruciale rol, onderstreept het belang van, kan niet genoeg benadrukt worden) en de symboolzin die een gewoon feit tot teken van iets groters maakt (staat symbool voor, is tekenend voor, getuigt van een rijke traditie). Het repertoire is klein: dezelfde tien frasen keren terug over totaal verschillende onderwerpen. Schrap het etiket en houd het feit met het gevolg dat het gewicht geeft.

Signalen: `van cruciaal belang` · `essentieel` · `belangrijker dan ooit` · `speelt een cruciale rol` · `speelt een belangrijke rol` · `onderstreept het belang van` · `kan niet genoeg benadrukt worden` · `van onschatbare waarde` · `niet te onderschatten belang` · `een van de belangrijkste` · `past in een bredere trend` · `staat symbool voor` · `geldt als een symbool van` · `is tekenend voor` · `getuigt van` · `diepgeworteld` · `rijke traditie` · `onwrikbare toewijding` (+6)

Voor: De meetup speelt een cruciale rol in de regio en onderstreept het belang van kennisdeling.

Na: Op de meetup staan twee talks. De vorige keer kwamen er 38 mensen.

Niet markeren: Niet markeren als het gewicht wordt onderbouwd in dezelfde alinea (een cijfer, een gevolg, een besluit dat eruit volgde). Vakteksten mogen iets cruciaal noemen als het uitvalsrisico dat aantoont. Eén losse instantie in een lang stuk is geen patroon; de tell is de herhaling. Historische artikelen mogen een gebeurtenis een keerpunt noemen als de bron dat doet.

### Doorgevoerde metafoor `metaphor-overuse`

Ernst: **cluster** · Herkomst: transfer · en: `metaphor-overuse`

Eén beeld wordt geïntroduceerd en daarna nooit meer losgelaten: hetzelfde figuurlijke woord keert vijf tot tien keer terug in een stuk (ecosysteem, reis, kompas, fundament, motor, bouwstenen, rode draad, stip op de horizon), waar een mens het één keer gebruikt en doorloopt. Gebruik het beeld één keer en zeg het daarna gewoon.

Signalen: `ecosysteem` · `reis` · `kompas` · `fundament` · `motor` · `bouwstenen` · `rode draad` · `kruispunt` · `paraplu` · `stip op de horizon`

Voor: De community is een ecosysteem waarin elke bijdrage een bouwsteen is; wie de reis meemaakt, vindt zijn kompas.

Na: Wie een keer komt spreken, brengt meestal de volgende spreker mee.

Niet markeren: Dichtheidspatroon: een enkel figuurlijk woord is normaal Nederlands en mag nooit op zichzelf gemarkeerd worden. In vakteksten zijn ecosysteem, motor en fundament letterlijke termen (biologie, techniek, bouw). Tel het aantal keren dat hetzelfde beeld terugkeert in één stuk.

### Gespeeld inzicht `performed-insight-phrase`

Ernst: **cluster** · Herkomst: transfer · en: `performed-insight-phrase`

Essayistische tics die diepzinnigheid aankondigen in plaats van leveren: laat dat even bezinken, en dat is niet niks, je weet het antwoord al, geloof me niet op mijn woord, blijkt maar weer. Elk ensceneert een onthulling en voegt geen feit toe. Zeg de bewering waar de frase naar wijst: en dat is niet niks wordt de werkelijke omvang van het ding.

Signalen: `laat dat even bezinken` · `en dat is niet niks` · `je weet het antwoord al` · `de clou is` · `geloof me niet op mijn woord` · `blijkt maar weer`

Voor: De helft haakte af na de eerste mail. Laat dat even bezinken.

Na: De helft haakte af na de eerste mail.

Niet markeren: In gesproken presentaties is een pauzezin een retorisch middel dat werkt; in geschreven tekst zelden. Citaten blijven staan. Eén keer in een lang essay is stijl.

### Schijntegenwerping `phantom-rebuttal`

Ernst: **cluster** · Herkomst: transfer · en: `phantom-rebuttal`

De tekst discussieert met een gesprekspartner die hij zelf verzon: het ontkennen van een standpunt dat niemand innam (Begrijp me niet verkeerd, Om duidelijk te zijn, Ik zeg niet dat), de stroman die in één bijzin wordt opgeworpen en weggezet (Een voor de hand liggende aanpak zou zijn ..., maar) en het geënsceneerde zelfgesprek. Meestal een restant van een eerdere versie. Haal de verzonnen tegenwerping weg en noem de echte beperking.

Signalen: `Begrijp me niet verkeerd` · `Om duidelijk te zijn` · `Dit gaat niet zozeer over` · `Ik zeg niet dat` · `Je zou kunnen tegenwerpen dat` · `Een voor de hand liggende aanpak zou zijn` · `Sommigen zullen zeggen`

Voor: Begrijp me niet verkeerd, ik zeg niet dat frameworks slecht zijn. Om duidelijk te zijn: het gaat om onderhoud.

Na: Het framework kost ons twee dagen onderhoud per maand.

Niet markeren: In een discussie waar iemand het standpunt echt innam, is de weerlegging terecht; noem dan wie het zei. Academische teksten mogen een bekende tegenwerping benoemen met bron. De tell is de tegenstander zonder naam.

### Elke zin een quote `pull-quote-density`

Ernst: **cluster** · Herkomst: transfer · en: `pull-quote-density`

Regel na regel is geschreven om eruit geknipt te worden: overgepolijste citeerbare zinnen in elke alinea, gestapelde spreuken zonder verbindend weefsel, en losse regels als alinea voor het effect. De tell is de dichtheid, niet die ene goede regel. Houd de sterkste en laat de rest gewone zinnen zijn die het betoog dragen.

Signalen: `elke regel citeerbaar` · `gestapelde spreuken` · `losse regel als alinea` · `geen verbindende zinnen tussen de uitsmijters`

Voor: Code veroudert. Documentatie liegt. Alleen tests vertellen de waarheid. Daar begint alles.

Na: Tests zeggen wat de code nu doet. De documentatie in deze repo is van twee jaar geleden.

Niet markeren: Structureel patroon, geen frase: alleen te zien over een hele tekst. Aforismenbundels, LinkedIn-posts en reclame draaien hier per genre op. Eén sterke losse regel als alinea is een keuze, geen tell.

### Reflexmatig relativeren `reflexive-hedging`

Ernst: **cluster** · Herkomst: transfer · en: `reflexive-hedging`

Kalibratiewoorden (vrijwel, grotendeels, veelal, doorgaans, ruwweg, op enkele uitzonderingen na) en getuigenisvormen (lijkt, blijkt, wordt geacht, naar het zich laat aanzien) worden op elke bewering geplakt, zodat ze een reflex worden in plaats van echte onzekerheid te volgen. Ook de modale slag om de arm (kan, mag, zou kunnen) op uitspraken die de bron gewoon doet. Meet de dichtheid per zin en de herhaling van hetzelfde woord. Het spiegelbeeld is een menselijke tegenindicator: stellige uitspraken (de enige, de eerste, de beste) komen juist vaker van mensen, dus relativeer die niet weg.

Signalen: `blijkt` · `wordt geacht` · `grotendeels` · `veelal` · `doorgaans` · `in grote lijnen` · `op het eerste gezicht` · `naar het zich laat aanzien` · `vrijwel altijd` · `op enkele uitzonderingen na` · `zou kunnen` · `mogelijk` · `wellicht`

Voor: De opkomst lijkt doorgaans grotendeels stabiel, al blijkt dat op het eerste gezicht per editie te verschillen.

Na: De opkomst schommelt tussen de 25 en 40 mensen per editie.

Niet markeren: Losse kalibratie is gewoon Nederlands: 'doorgaans' in één zin is geen tell. Encyclopedische en wetenschappelijke teksten relativeren per conventie waar de bron dat doet. Markeer op dichtheid, niet op één woord, en nooit een voorbehoud dat een echte onzekerheid dekt die in de bron staat.

### Afleiden naar het proces bij kritiek `review-process-deflection`

Ernst: **cluster** · Herkomst: transfer · en: `review-process-deflection`

Als de herkomst of kwaliteit van een bijdrage ter discussie staat, gaat het antwoord over het proces in plaats van over de tekst: de criticus vragen precies aan te wijzen wat er mis is, het bezwaar afdoen als ongefundeerde speculatie, doorverwijzen naar samenwerking (laten we samen het artikel verbeteren), of melden dat de feedback is verwerkt zonder te zeggen wat er veranderde. Beantwoord de inhoud.

Signalen: `geef precies aan welke delen` · `laat me weten wat er precies mis is` · `ongefundeerde speculatie` · `laten we samen het artikel verbeteren` · `zonder te onderbouwen waarom` · `feedback verwerkt`

Voor: Laten we samen het artikel verbeteren; geef precies aan welke delen je onjuist vindt.

Na: Twee van de drie bronnen noemen het onderwerp niet. Ik heb ze vervangen door het provinciale register uit 2019.

Niet markeren: Om verduidelijking vragen is legitiem als de kritiek echt vaag was en de vraag concreet is. In moderatie- en overlegpagina's is procesverwijzing soms de juiste route. De tell is de procesbeweging in plaats van een inhoudelijk antwoord dat wel te geven was.

### Hypothetische opening `speculative-scenario-opener`

Ernst: **cluster** · Herkomst: transfer · en: `speculative-scenario-opener`

Een betoog opent met een verzonnen wereld die wenselijke uitkomsten opsomt in plaats van een bewering te doen: Stel je een wereld voor waarin, Stel je voor dat, Beeld je in dat, Wat als. Het scenario doet het overtuigingswerk en er volgt geen bewijs. Schrap de hypothese en zeg de echte bewering.

Signalen: `Stel je een wereld voor waarin` · `Stel je voor dat` · `Beeld je in dat` · `Wat als je` · `In die wereld`

Voor: Stel je een wereld voor waarin iedere ontwikkelaar in Twente elkaar kent.

Na: Ontwikkelaars in Twente werken vaak bij kleine bedrijven en komen elkaar zelden tegen.

Niet markeren: Een gedachte-experiment in een wetenschappelijke of filosofische tekst is een methode, geen tell. Fictie en scenarioplanning openen zo per definitie. Niet markeren als de hypothese daarna wordt doorgerekend.

### Belerende voorbehouden `didactic-disclaimers`

Ernst: **context** · Herkomst: transfer · en: `didactic-disclaimers`

Waarschuwingen aan de lezer in een tekst die gewoon feiten zou moeten melden: het is belangrijk om te onthouden, houd er rekening mee dat, dit kan per situatie verschillen, raadpleeg altijd een deskundige, controleer dit altijd zelf. Haal voorbehouden weg die de lezer niet vroeg en die de bewering niet nodig heeft; houd er één als het verandert wat de lezer moet doen.

Signalen: `het is belangrijk om te onthouden` · `houd er rekening mee dat` · `dit kan per situatie verschillen` · `raadpleeg altijd een deskundige` · `controleer dit altijd zelf` · `Let op:` · `ter voorkoming van verwarring`

Voor: Houd er rekening mee dat dit per situatie kan verschillen. Raadpleeg altijd een deskundige.

Na: Voor bedrijven met meer dan 50 werknemers gelden andere regels. Die staan in artikel 7.

Niet markeren: Medische, juridische en financiële teksten hebben verplichte disclaimers; die blijven. In een handleiding is een waarschuwing bij een onomkeerbare stap functioneel. De tell is het voorbehoud dat niets verandert aan wat de lezer doet.

### Verzonnen massa als contrast `invented-crowd-contrast`

Ernst: **context** · Herkomst: transfer · en: `invented-crowd-contrast`

Een bewering leunt op een achterblijvende menigte die niemand benoemt: Iedereen zegt X, maar, de gangbare wijsheid klopt niet, terwijl de rest nog vergaderde, terwijl de markt nog nadacht. De tegenstander is verzonnen, dus het contrast kost niets. Noem het feit en schrap de menigte, of noem de echte concurrent en wat die deed.

Signalen: `terwijl de rest nog vergaderde` · `terwijl anderen nog discussieerden` · `terwijl de markt nog nadacht` · `Iedereen zegt X, maar` · `de gangbare wijsheid` · `men denkt vaak dat`

Voor: Terwijl de rest nog vergaderde, hadden wij de zaal al geboekt.

Na: We boekten de zaal in juni, vier maanden voor de datum.

Niet markeren: Als de menigte benoembaar is en de tekst haar benoemt (een aangehaald rapport, een concurrent met naam), is het contrast gewoon een vergelijking. In wetenschapsjournalistiek is 'lang werd gedacht dat' correct als er een bron bij staat.

### Lanceringsintro `launch-copy-introduction`

Ernst: **context** · Herkomst: transfer · en: `launch-copy-introduction`

Een product wordt aangekondigd als een deelnemer aan een spelshow in plaats van beschreven: Maak kennis met X, Zeg hallo tegen X, je nieuwe favoriete Y, Denk aan Notion, maar dan voor teams, dé nieuwe standaard. Bijna vaste vorm in korte lanceringscopy. Zeg wat het ding doet en voor wie.

Signalen: `Maak kennis met` · `Zeg hallo tegen` · `je nieuwe favoriete` · `Denk aan Notion, maar dan voor` · `dé nieuwe standaard` · `dé nieuwe manier om`

Voor: Maak kennis met devmeetup.nl, je nieuwe favoriete plek voor developers in de regio.

Na: Op devmeetup.nl staan de meetups en de vacatures uit de regio.

Niet markeren: In reclame is dit het genre; markeer het alleen als de tekst informatief hoort te zijn (documentatie, release notes, een nieuwsbericht). Een kennismakingszin in een handleiding die daarna uitlegt wat het ding doet is bruikbaar.

### Betuttelende vergelijking `patronizing-analogy`

Ernst: **context** · Herkomst: transfer · en: `patronizing-analogy`

Een ongevraagde vergelijking komt in de plaats van de bewering of de instructie: Zie het als een zakmes voor je workflow, Het is een beetje als een snelweg voor data, Minder een hamer, meer een scalpel. De lezer krijgt twee plaatjes en geen advies. Zeg wat het ding doet, of wat je moet doen.

Signalen: `Zie het als` · `Het is een beetje als` · `Vergelijk het met` · `Minder een hamer, meer een scalpel` · `Stel je een X voor die`

Voor: Zie het als een zakmes voor je workflow. Het is een beetje als een snelweg voor data.

Na: De tool haalt de logs op en zet ze in één tabel.

Niet markeren: In lesmateriaal voor beginners is een vergelijking vaak het snelste pad naar begrip; markeer alleen als ze de uitleg vervangt in plaats van voorbereidt. Eén analogie die daarna wordt uitgewerkt is didactiek.

### Register dat niet bij de tekst past `register-mismatch`

Ernst: **context** · Herkomst: transfer · en: `register-mismatch`

Het register komt uit gewoonte en niet uit de context. Subvormen: het gepolijste bedrijfsantwoord op een losse vraag, zinnen die hardop gelezen als persbericht klinken (Wij zijn verheugd te kunnen aankondigen, Met trots presenteren wij, Hierbij delen wij u mede), en de registerwissel binnen één tekst, waarbij de toon van spreektaal naar ambtelijk springt of de spelling plotseling foutloos is na eerdere fouten. Lees het hardop; klinkt een zin als communicatie in plaats van als een mens, schrijf hem zoals je het zou zeggen.

Signalen: `Wij zijn verheugd te kunnen aankondigen` · `Met trots presenteren wij` · `Hierbij delen wij u mede` · `In het kader van onze doorlopende inspanningen` · `Wij streven ernaar om` · `dient te worden opgemerkt` · `spreektalige tussenwerpsels in verder formele tekst` · `plotseling foutloze spelling na eerdere fouten`

Voor: Wij zijn verheugd te kunnen aankondigen dat de inschrijving is geopend. Vet trouwens.

Na: De inschrijving is open.

Niet markeren: Een persbericht mag als persbericht klinken en een notariële akte als akte; het gaat om register dat niet bij de plek past. Meertalige of geciteerde passages verklaren een wissel. Bij een tekst met meerdere auteurs is toonverschil normaal.

## Woordkeus

### Kant-en-klare standaardzin (ik hoop dat dit bericht je goed bereikt) `canned-stock-sentence`

Ernst: **always** · Herkomst: transfer · en: `canned-stock-sentence`

Een hele voorgebakken zin die niets specifieks erkent: Ik hoop dat dit bericht je goed bereikt, Ik hoop dat het goed met je gaat, Ik had onlangs het genoegen om, Bedankt voor je interesse in, X is actief op sociale media en deelt regelmatig updates. Begin bij de echte reden van het bericht, of noem wat er gebeurd is.

Signalen: `ik hoop dat dit bericht je goed bereikt` · `ik hoop dat deze mail je in goede gezondheid bereikt` · `ik hoop dat het goed met je gaat` · `ik had onlangs het genoegen` · `is actief op sociale media` · `deelt regelmatig updates` · `bedankt voor je interesse in`

Voor: Ik hoop dat dit bericht je goed bereikt. Ik had onlangs het genoegen jullie meetup bij te wonen.

Na: Ik was donderdag bij jullie meetup en heb daar een vraag over.

Niet markeren: In formele correspondentie met een onbekende geadresseerde is een korte beleefdheidsopening gebruikelijk; de tell is de lange voorgebakken variant die geen enkel detail bevat. Bedankt voor je interesse in als bevestigingsmail na een aanmelding is functioneel.

### Holle openingszin over de veranderende wereld `generic-scene-setting-opener`

Ernst: **always** · Herkomst: transfer · en: `generic-scene-setting-opener`

Een openingszin die het onderwerp in een algemeen heden of een ongenoemde trend plaatst in plaats van de concrete aanleiding te noemen: In de snel veranderende wereld van vandaag, In de huidige digitale wereld, In een tijd waarin, Anno nu, Steeds meer organisaties, Het is geen geheim dat. Vaak gevolgd door de staarten is niet meer weg te denken en wordt steeds belangrijker. Nederlandse redacteuren maken er een stijlregel van: nooit meer een tekst zo beginnen. Noem de aanleiding die dit stuk nodig maakte, of begin bij het voorbeeld.

Signalen: `In de snel veranderende wereld van vandaag` · `In de huidige digitale wereld` · `In ons huidige dynamische tijdperk` · `In de hedendaagse maatschappij` · `In een tijd waarin` · `In een wereld waarin` · `Anno nu` · `Steeds meer organisaties` · `Steeds meer bedrijven` · `is niet meer weg te denken` · `wordt steeds belangrijker` · `Het is geen geheim dat` · `Het is algemeen bekend dat` · `Belangrijker dan ooit`

Voor: In de snel veranderende wereld van vandaag is goede tooling niet meer weg te denken.

Na: Onze release duurde vrijdag vier uur, dus hebben we de pijplijn opnieuw gebouwd.

Niet markeren: In een historisch overzicht kan in een tijd waarin een echte periode aanwijzen die daarna wordt ingevuld. Steeds meer bedrijven met een bronvermelding en een getal erachter is een bewering, geen sfeerzin. De frase midden in een stuk, na de aanleiding, weegt lichter dan als eerste zin.

### Holle nadruk (oprecht, daadwerkelijk, eerlijk gezegd) `hollow-intensifier`

Ernst: **always** · Herkomst: transfer · en: `hollow-intensifier`

Woorden die overtuiging beweren in plaats van een feit te leveren: oprecht, werkelijk, daadwerkelijk, eerlijk gezegd, om eerlijk te zijn, laten we eerlijk zijn, in feite, feitelijk, plus echt en gewoon zodra ze als versterker op een bewering staan. Schrap het woord en noem het feit; de standaardoplossing is weglaten, niet vervangen.

Signalen: `oprecht` · `daadwerkelijk` · `eerlijk gezegd` · `om eerlijk te zijn` · `laten we eerlijk zijn` · `in feite` · `feitelijk` · `gewoon`

Voor: Dit maakt het proces eigenlijk gewoon echt eenvoudiger.

Na: Dit scheelt twee handelingen per bestelling.

Niet markeren: Echt en gewoon staan bewust niet in de regex: als modaal partikel zijn ze juist een teken van natuurlijk Nederlands (doe maar gewoon, dat is echt zo). Daadwerkelijk in een juridische of onderzoekscontext zet een gemeten waarde tegenover een geraamde en is dan inhoudelijk. In feite dat een echte tegenstelling met de schijn markeert, blijft staan.

### Aankondigingsframe (het is belangrijk om op te merken) `it-is-worth-noting-frame`

Ernst: **always** · Herkomst: translationese · en: `it-is-worth-noting-frame`

Een bijzin die aankondigt dat het volgende ertoe doet, in plaats van het gewoon te zeggen: het is belangrijk om op te merken dat, het is goed om te weten dat, het is vermeldenswaard dat, opgemerkt dient te worden dat, daarom is het essentieel dat, de realiteit is dat. Nederlandse tellingen noemen dit de meest voorkomende AI-zinsopening. Schrap het frame en houd de inhoud; verliest de zin niets, dan zat er niets in het frame. De formulering is meestal een letterlijke overzetting van It is important to note that of It is worth mentioning.

Signalen: `het is belangrijk om op te merken dat` · `het is belangrijk om te overwegen` · `het is belangrijk om te benadrukken dat` · `het is goed om te weten dat` · `het is vermeldenswaard dat` · `opgemerkt dient te worden dat` · `hierbij is van belang dat` · `wat opvalt is dat` · `de realiteit is dat` · `daarom is het essentieel dat` · `het loont de moeite om te onthouden dat` · `het is de moeite waard om te vermelden` · `het is essentieel om` · `het is cruciaal om` · `dit doet ertoe omdat` · `dit is belangrijk omdat`

Voor: Het is belangrijk om op te merken dat de bouwtijd is gehalveerd.

Na: De bouwtijd is gehalveerd.

Niet markeren: In een handleiding of veiligheidsinstructie kan het frame een echte waarschuwing markeren die de lezer anders overslaat. Wat opvalt is dat hoort in een analyse waar de schrijver daadwerkelijk observeert. Citaten uit interviews blijven staan. Een aankondiging is legitiem als hij een uitzondering markeert die de lezer anders mist, bijvoorbeeld een waarschuwing in een handleiding of een voorbehoud in een rapport. Het signaal is de aankondiging voor een gewone bewering.

### Uitnodigende opening (laten we erin duiken) `lets-invitation-opener`

Ernst: **always** · Herkomst: translationese · en: `lets-invitation-opener`

Een alinea of hoofdstuk geopend met een uitnodiging tot een gezamenlijke reis: laten we erin duiken, laten we dit uitpakken, laten we eens kijken naar, laten we het opsplitsen, we nemen je mee, we duiken erin. Het ensceneert samenwerking en stelt het punt één zin uit. Schrap de opening en begin bij de bewering. De opening komt uit het Engelse Let's en staat net zo goed aan het begin van een sectie: laten we beginnen met, laten we samen ontdekken.

Signalen: `laten we erin duiken` · `laten we duiken in` · `laten we dit uitpakken` · `laten we eens kijken naar` · `laten we het opsplitsen` · `we duiken erin` · `we nemen je mee` · `laten we beginnen bij` · `laten we samen ontdekken` · `Laten we beginnen met`

Voor: Laten we erin duiken hoe de scheduler werkt.

Na: De scheduler kijkt elke 200 milliseconde en gooit alles ouder dan een minuut weg.

Niet markeren: In een workshopscript of een presentatie waar de spreker het publiek echt meeneemt naar de volgende oefening, is de uitnodiging functioneel. Laten we beginnen bij in een uitgeschreven college markeert een echte volgorde. 'Laten we' is gewoon Nederlands in een echt voorstel aan een groep ('Laten we dat volgende week bespreken') en in notulen en gespreksverslagen. Het signaal is het gebruik als vaste sectieopener, twee keer of vaker per tekst.

### Onderwerpsaanloop (als het gaat om, in de kern) `topic-framing-filler`

Ernst: **always** · Herkomst: transfer · en: `topic-framing-filler`

Uitdrukkingen die een onderwerp inleiden of een samenvatting aankondigen zonder zelf informatie te dragen: als het gaat om, wanneer het aankomt op, in de kern, in essentie, in de basis, aan het eind van de dag, uiteindelijk draait het om, de waarheid is dat, in dit artikel, in de wereld van. Schrap de frase en begin de zin bij het onderwerp.

Signalen: `als het gaat om` · `wanneer het aankomt op` · `in de kern` · `in essentie` · `in de basis` · `aan het eind van de dag` · `uiteindelijk draait het om` · `waar het om draait is` · `de waarheid is dat` · `in dit artikel` · `in deze blog` · `in de wereld van`

Voor: Als het gaat om caching is het grootste risico verouderde data.

Na: Het grootste risico bij caching is verouderde data.

Niet markeren: In de kern van kan letterlijk over een kern gaan (de kern van een reactor, de kern van een dorp). In dit artikel is functioneel in een wetenschappelijke abstract die de opzet aankondigt. Aan het eind van de dag in de letterlijke tijdsbetekenis blijft staan.

### Vage aanbeveling (de moeite waard) `vague-endorsement-worth-verbing`

Ernst: **always** · Herkomst: transfer · en: `vague-endorsement-worth-verbing`

Een algemene duim omhoog die in de plaats komt van een concrete reden: de moeite waard, het lezen waard, zeker een aanrader, een must-read, het bekijken waard, zeker aan te raden, houd dit in de gaten. Schrap hem, of zeg wat de lezer er precies aan heeft.

Signalen: `de moeite waard` · `het lezen waard` · `zeker een aanrader` · `een must-read` · `het bekijken waard` · `zeker aan te raden` · `houd dit in de gaten`

Voor: Hun changelog is zeker de moeite waard.

Na: In hun changelog staat precies welke standaardwaarden in v3 zijn veranderd.

Niet markeren: In een recensie is een aanbeveling het genre; daar telt alleen of de reden erbij staat. De moeite waard in de letterlijke afweging van kosten tegen baten (de omweg was de moeite waard, want) blijft staan.

### Omhaal van woorden (teneinde, vanwege het feit dat) `wordy-circumlocution`

Ernst: **always** · Herkomst: transfer · en: `wordy-circumlocution`

Een constructie van meerdere woorden op de plek van één: teneinde voor om, vanwege het feit dat voor omdat, op dit moment in de tijd voor nu, in het geval dat voor als, de mogelijkheid hebben om voor kunnen, overgaan tot voor doen. De correctie is mechanisch en de zin wordt er alleen korter van. Een treffer is een breedsprakigheidsfout, niet op zichzelf bewijs van een machine.

Signalen: `teneinde` · `vanwege het feit dat` · `op dit moment in de tijd` · `in het geval dat` · `de mogelijkheid hebben om` · `overgaan tot` · `tot uitvoering brengen` · `met betrekking tot` · `ten aanzien van` · `in termen van`

Voor: Teneinde dit doel te bereiken gaan wij over tot een herziening van het proces.

Na: Om dit te halen herzien we het proces.

Niet markeren: Met betrekking tot en ten aanzien van zijn in juridische en bestuurlijke stukken de vaste formule en staan daarom niet in de regex. In het kader van kan een echt kader aanwijzen (in het kader van de subsidieregeling). Overgaan tot is in een verslag van een vergadering een letterlijke handeling.

### Opeenstapeling van voegwoorden (Daarnaast, Bovendien, Tevens) `additive-transition-pileup`

Ernst: **cluster** · Herkomst: nl-bron · en: `additive-transition-pileup`

Formele verbindingswoorden als alinealijm, vooraan bijna elke zin, waardoor een redenering wordt gesuggereerd die er niet is: Daarnaast, Bovendien, Tevens, Voorts, Eveneens, Verder, Daarenboven, Anderzijds, en de tegenstellende Echter met komma. Dezelfde reflex aan het eind van een tekst levert de samenvattende signaalwoorden Kortom, Samenvattend, Al met al, Concluderend en Tot slot. Een mens gebruikt deze woorden ook, maar niet vier keer achter elkaar: de eenheid is de alinea, en drie treffers in één tekst is een rode vlag. Herschrijf zo dat het verband vanzelf blijkt.

Signalen: `Bovendien` · `Daarnaast` · `Verder` · `Tevens` · `Voorts` · `Eveneens` · `Daarenboven` · `Anderzijds` · `Aan de andere kant` · `Daarbij komt dat` · `Desalniettemin` · `Echter,` · `Sterker nog` · `Kortom` · `Samenvattend` · `Al met al` · `Concluderend` · `Tot slot` (+1)

Voor: Daarnaast groeit het aantal deelnemers. Bovendien is de zaal groter. Tevens is er koffie.

Na: Het aantal deelnemers groeit, de zaal is groter en er is koffie.

Niet markeren: Eén los daarnaast of echter is normaal Nederlands en telt niet; alleen de opeenvolging of de dichtheid. In een opsommend naslagwerk (encyclopedie, jaarverslag, notulen) staan deze woorden functioneel op hun plek. Kortom aan het eind van een lange uiteenzetting die echt wordt samengevat, mag blijven. Echter aan het zinsbegin met komma is bovendien een anglicisme en hoort onder translationese.

### Machinepoëzieregister (fluisteren, echo, breekbaar) `ai-poetry-register`

Ernst: **cluster** · Herkomst: transfer · en: `ai-poetry-register`

De smalle woordenschat waar gegenereerde Nederlandse verzen dwangmatig naar terugkeren: een vaste set (hart, omarmen, echo, weerklank, fluisteren, stilte) en een emotioneel-broze set die in de plaats komt van een beeld (breekbaar, gebroken, verlangen, schaduw, adem, sluier, as, bloeien, wiegen). Twee registers in elkaar geschoven: Instagrampoëzie en de meest gedeelde bloemlezingpagina's. Zet er één concreet, zintuiglijk detail voor in de plaats.

Signalen: `fluistert` · `echo` · `weerklank` · `stilte` · `breekbaar` · `gebroken` · `verlangen` · `omarmen` · `schaduw` · `adem` · `sluier` · `bloeien` · `wiegen`

Voor: een breekbare stilte fluistert door de schaduw van de ochtend

Na: de waterkoker tikt terwijl hij afkoelt, het raam is nog koud

Niet markeren: In gepubliceerde poëzie en songteksten van mensen komen deze woorden ook voor; de tell is dat ze samen de hele beeldtaal vormen en er geen concreet ding in het gedicht staat. Echo en weerklank in een natuurkundige of muzikale context zijn vaktermen. Citaten uit bestaande gedichten blijven staan.

### AI-woordenlijst (cruciaal, naadloos, duiken in) `ai-vocabulary-lexicon`

Ernst: **cluster** · Herkomst: transfer · en: `ai-vocabulary-lexicon`

Een kleine gesloten woordenschat waar taalmodellen in het Nederlands naar grijpen ongeacht het onderwerp. Drie subvormen: opwaarderende bijvoeglijke naamwoorden (cruciaal, essentieel, naadloos, robuust, moeiteloos, baanbrekend, toonaangevend), figuurlijke werkwoorden op de plek van een concreet werkwoord (duiken in, ontsluiten, onderstrepen, getuigen van, in kaart brengen) en grote abstracte zelfstandige naamwoorden die gewicht moeten geven (hoeksteen, kantelpunt, mijlpaal, palet, ecosysteem). De toets is de vervangproef: staat het woord er nog steeds als je het onderwerp vervangt, dan draagt het niets.

Signalen: `cruciaal` · `essentieel` · `naadloos` · `naadloze` · `moeiteloos` · `robuust` · `baanbrekend` · `toonaangevend` · `ongekend` · `nauwgezet` · `veelzijdig` · `impactvol` · `toekomstbestendig` · `hoeksteen` · `kantelpunt` · `mijlpaal` · `een rijk palet` · `een schat aan` (+31)

Voor: Deze naadloze oplossing speelt een cruciale rol in het digitale landschap en getuigt van jarenlange innovatie.

Na: De koppeling scheelt de klantenservice ongeveer twee uur per dag. We bouwen eraan sinds 2019.

Niet markeren: Cruciaal en essentieel zijn gewone Nederlandse woorden; markeer ze pas vanaf twee treffers per alinea of samen met een tweede woord uit de lijst. In kaart brengen is in onderzoek- en beleidscontext de vakterm voor wat er letterlijk gebeurt. Mijlpaal in een projectplanning en hoeksteen in een bouwkundige tekst zijn letterlijk bedoeld. Citaten, productnamen en aangehaalde reclametekst blijven staan.

### Stapel standaardfrasen en consultancyjargon `boilerplate-phrase-stack`

Ernst: **cluster** · Herkomst: transfer · en: `boilerplate-phrase-stack`

Vaste combinaties van twee of drie woorden uit het advies-, offerte- en fondsenregister die los onschuldig zijn maar in gegenereerde tekst opstapelen: het snijvlak van, duurzame groei, langetermijnwaarde, community-gedreven, van A tot Z ontzorgd, korte lijnen, no-nonsense. Daarnaast de zelfstandige naamwoorden uit dezelfde familie, die intelligent ogen en niets dragen: synergie, holistische benadering, stakeholders, waardepropositie, randvoorwaarden, digitale transformatie, een breed scala aan. Markeer één frase die twee keer terugkomt, of drie verschillende uit deze familie in één tekst; vervang ze door de opsomming die ze samenvatten.

Signalen: `het snijvlak van` · `de integratie van` · `opkomende sector` · `community-gedreven` · `duurzame groei` · `langetermijnwaarde` · `breed gedragen` · `van A tot Z ontzorgd` · `met oog voor detail` · `korte lijnen` · `no-nonsense` · `gebruikersbetrokkenheid` · `synergie` · `holistische benadering` · `datagedreven` · `data-gedreven` · `relevante stakeholders` · `waardepropositie` (+11)

Voor: Een community-gedreven project op het snijvlak van AI en infrastructuur, gebouwd voor duurzame groei.

Na: De knooppunten stemmen zelf over de kostenverdeling, en de vergoeding komt uit de transactiekosten.

Niet markeren: Stakeholder, randvoorwaarde en ecosysteem zijn in een projectplan, een aanbesteding of de biologie gewone vaktermen. Best practices in een technische standaard verwijst naar een echt document. Eén frase in een verder concrete tekst is geen treffer; de drempel is herhaling of stapeling.

### Sturende zinsbijwoorden (opvallend genoeg, nog belangrijker) `confidence-calibration-adverb`

Ernst: **cluster** · Herkomst: transfer · en: `confidence-calibration-adverb`

Zinsbijwoorden die de lezer vertellen hoe zwaar hij een feit moet wegen, in plaats van het feit voor zichzelf te laten spreken: opvallend genoeg, interessant genoeg, verrassend genoeg, nog belangrijker, belangrijker nog, cruciaal hierbij, bovenal, en de zekerheidsversterkers ongetwijfeld en zonder twijfel. De tell is het stapelen aan het begin van opeenvolgende zinnen, niet het losse woord.

Signalen: `opvallend genoeg` · `interessant genoeg` · `verrassend genoeg` · `nog belangrijker` · `belangrijker nog` · `cruciaal hierbij` · `bovenal` · `ongetwijfeld` · `zonder twijfel` · `met name`

Voor: Opvallend genoeg halveerde de bouwtijd. Nog belangrijker: ook het geheugengebruik daalde.

Na: De bouwtijd halveerde en het geheugengebruik daalde mee.

Niet markeren: Eén opvallend genoeg in een lang stuk waar de schrijver echt verbaasd was, is geen tell. Met name is in gewoon Nederlands een normale afbakening en staat daarom niet in de regex. In wetenschappelijke tekst markeert opmerkelijk genoeg soms een echt onverwacht resultaat.

### Dichte AI-woordenschat (bevestiger) `dense-ai-vocabulary-composite`

Ernst: **cluster** · Herkomst: transfer · en: `dense-ai-vocabulary-composite`

Een samengestelde drempel, geen frase: minstens 150 woorden, minstens vijf verschillende treffers uit de altijd-lijst, minstens twee alinea's met een cluster opgepoetste werkwoorden, en minstens één standaardovergang, alles in dezelfde tekst. De combinatie geldt als sterke bevestiger. Geen enkele laag is op zichzelf genoeg, omdat elke laag overlapt met gewoon Nederlands vakjargon.

Voor: Een stuk van 400 woorden met duiken in, naadloos, robuust, cruciaal en hoeksteen, twee alinea's met borgen plus ecosysteem, en een alinea die met Daarnaast opent.

Na: Herschrijf het stuk rond de twee of drie dingen die het meldt, met het gewone woord voor elk.

Niet markeren: Onder de 150 woorden is de drempel betekenisloos. Een beleidsnota, een subsidieaanvraag of een offerte haalt hem soms zonder machine: kijk dan of de tekst ook concrete getallen, namen en gevallen bevat. Vertaalde marketingtekst van een mens haalt hem eveneens.

### Opgepoetste en beleidswerkwoorden (twee of meer in één alinea) `elevated-vocabulary-cluster`

Ernst: **cluster** · Herkomst: transfer · en: `elevated-vocabulary-cluster`

Werkwoorden die een duurdere variant zijn van een gewoon werkwoord en die in AI-output stelselmatig opduiken: benutten, ontsluiten, faciliteren, stroomlijnen, optimaliseren, revolutioneren, identificeren, in staat stellen. De Nederlandse subvorm is de beleids- en subsidietaal, waarin elke handeling wordt ingevuld met versterken, borgen, waarborgen, verankeren, vormgeven, stimuleren, ontzorgen of inzetten op, steeds met een abstract lijdend voorwerp. De eenheid is de alinea, niet het woord: vanaf twee treffers in één alinea herschrijf je hem rond de concrete handeling en degene die hem uitvoert.

Signalen: `ontsluiten` · `faciliteren` · `stroomlijnen` · `optimaliseren` · `revolutioneren` · `identificeren` · `opereren` · `transformeren` · `maximaliseren` · `navigeren` · `leveragen` · `in staat stellen` · `meenemen in` · `versterken` · `waarborgen` · `verankeren` · `vormgeven` · `stimuleren` (+10)

Voor: Het platform stelt teams in staat om het ecosysteem te benutten en de samenwerking te versterken.

Na: Teams kunnen elkaars plug-ins hergebruiken en met z'n tweeën in hetzelfde document werken.

Niet markeren: In een subsidieaanvraag, een bestek of een beleidsnota zijn borgen, waarborgen en verankeren de gevraagde vaktermen; daar telt alleen de dichtheid. Optimaliseren en identificeren zijn in techniek en onderzoek gewone werkwoorden met een precieze betekenis. Eén los werkwoord is nooit genoeg: de regel is twee in dezelfde alinea.

### Vlakke woordstatistiek (lage TTR, uniforme n-grammen) `flat-lexical-statistics`

Ernst: **cluster** · Herkomst: transfer · en: `flat-lexical-statistics`

Gemeten, niet gelezen. De tekst is op vijf assen vlakker dan menselijk proza: type-tokenratio, lexicale dichtheid, variatie in zinseinden, uniformiteit van woordtripletovergangen en perplexiteit per token. De volgende woordkeuze is steeds de verwachte. Dit is een bevestiger bij een leesoordeel, geen zelfstandig bewijs.

Signalen: `lage TTR` · `lage lexicale dichtheid` · `weinig variatie in zinseinden` · `uniforme woordtripletovergangen` · `lage en vlakke perplexiteit` · `tokens >= 200 && ttr < 0.40`

Voor: Een stuk van 900 woorden met een TTR van 0,36 dat in elke alinea hetzelfde abstracte zelfstandig naamwoord hergebruikt.

Na: Vervang dat hergebruikte abstracte woord per alinea door het geval waar het voor staat.

Niet markeren: Nederlandse samenstellingen worden aan elkaar geschreven en verhogen daarmee het aantal types: meet op lemma's en houd een lagere drempel aan dan de Engelse 0,50 tot 0,65. Korte teksten, handleidingen, juridische stukken en teksten in eenvoudige taal zijn van nature vlak. Onder de 200 tokens zegt de maat niets.

### Deftige en ambtelijke woordkeus (dienen te, alvorens, derhalve) `latinate-inflation`

Ernst: **cluster** · Herkomst: transfer · en: `latinate-inflation`

Het langere, formeel-schriftelijke woord kiezen waar een kort gewoon woord hetzelfde zegt: dienen te voor moeten, alvorens voor voordat, aanvangen voor beginnen, vervaardigen voor maken, initiëren voor starten, verrichten voor doen, aanschaffen voor kopen. Daar hoort de juridisch-ambtelijke set bij die vrijwel niemand meer spreekt: derhalve, zodoende, desalniettemin, aldus, bijgevolg, aangaande, voornoemd, verheugd. Toets zoals Nederlandse redacteuren doen: gebruikt deze schrijver dit woord ook als hij het vertelt? Meestal niet.

Signalen: `dienen te` · `dient te` · `alvorens` · `aanvangen` · `vervaardigen` · `initiëren` · `verrichten` · `aanschaffen` · `talrijke` · `betreffende` · `beschikt over` · `derhalve` · `zodoende` · `desalniettemin` · `aldus` · `bijgevolg` · `aangaande` · `in acht nemende` (+3)

Voor: Het team dient de pijplijn te benutten alvorens men aanvangt met testen.

Na: Het team gebruikt de nieuwe pijplijn en begint dan met testen.

Niet markeren: In wetteksten, notariële akten, statuten en vonnissen zijn derhalve, voornoemd en dienen te het voorgeschreven register; markeer daar niets. Beschikt over, is gelegen, diverse en talrijke zijn in encyclopedische en journalistieke tekst gewoon Nederlands en staan daarom niet in de regex. Citaten uit oudere bronnen blijven staan.

### Bespiegelend slotbijwoord (misschien is dat wel, langzaam maar zeker) `reflective-adverb-formula`

Ernst: **cluster** · Herkomst: transfer · en: `reflective-adverb-formula`

De vaste bijwoordformule van essayeindes en inzichtmomenten: misschien is dat wel, misschien is dat precies, en misschien is dat maar goed ook, langzaam maar zeker, pas toen werd duidelijk. De formule kondigt een inzicht aan zonder er een te leveren. Schrap het bijwoord en laat het laatste concrete detail het einde dragen.

Signalen: `misschien is dat wel` · `misschien is dat precies` · `en misschien is dat maar goed ook` · `langzaam maar zeker` · `pas toen werd duidelijk` · `uiteindelijk bleek`

Voor: Misschien is dat wel het echte antwoord.

Na: Daarom kozen we voor die aanpak.

Niet markeren: Langzaam maar zeker en uiteindelijk bleek zijn gewoon Nederlands over een proces dat echt langzaam ging en staan daarom niet in de regex. In een persoonlijk essay mag één bespiegeling staan; de tell is de formule aan het eind van elke sectie.

### Herhaling met aankondiging (met andere woorden, oftewel) `restatement-gloss`

Ernst: **cluster** · Herkomst: transfer · en: `restatement-gloss`

Een vaste frase kondigt een parafrase aan van wat er net stond, zodat hetzelfde punt twee keer wordt geleverd: met andere woorden, anders gezegd, oftewel, dat wil zeggen, ter verduidelijking. Kijk of de tweede versie iets toevoegt; zo niet, schrap er één en houd de duidelijkste.

Signalen: `met andere woorden` · `anders gezegd` · `oftewel` · `dat wil zeggen` · `ofwel` · `ter verduidelijking`

Voor: De wachtrij loopt langzaam leeg. Met andere woorden: berichten stapelen zich op.

Na: De wachtrij loopt langzamer leeg dan hij volloopt, dus berichten stapelen zich op.

Niet markeren: Oftewel en dat wil zeggen introduceren vaak een echte vertaling of definitie (de OR, oftewel de ondernemingsraad) en staan daarom niet in de regex. In lesmateriaal is een tweede formulering soms de bedoeling. Eén keer per stuk is geen patroon.

### Wervende socialtaal en LinkedIn-clichés `social-ad-boilerplate`

Ernst: **cluster** · Herkomst: nl-bron · en: `social-ad-boilerplate`

Versleten advertentie- en podiumtaal van sociale media en bedrijfsblogs, in de plaats van iets wat je kunt laten zien: ontgrendel het potentieel, haal het maximale eruit, til je X naar een hoger niveau, link in bio, volg voor meer, trots om te delen, ongekende kansen. Verwante subvorm is de wervende opening of afsluiting van een artikel: De sleutel tot, Ontdek nu zelf, In dit artikel onthullen we, Bij [merknaam] begrijpen we, Ben je klaar om. Zeg wat de lezer krijgt en waar hij het vindt. Dezelfde taal levert de koppen en de knoppen: een gebiedende wijs of een klaar-om-vraag uit Amerikaanse advertentietaal (ontdek nu, klaar om te transformeren, start vandaag nog, mis het niet), plus de SEO-titelformule Van X naar Y: Hoe Z.

Signalen: `ontgrendel het potentieel` · `haal het maximale uit` · `naar een hoger niveau tillen` · `naar the next level` · `link in bio` · `stuur me een DM` · `volg voor meer` · `trots om te delen` · `het verschil maken` · `ongekende kansen` · `De sleutel tot` · `Ontdek nu zelf` · `geheimen ontdekken` · `In dit artikel onthullen we` · `Naar nieuwe hoogten tillen` · `Ben je klaar om` · `Bij [merknaam] begrijpen we` · `Dit artikel verkent` (+10)

Voor: Til je data naar een hoger niveau. Link in bio.

Na: De export staat op /rapporten/csv.

Niet markeren: In een echte advertentie of een socialpost met een echte link is link in bio een functionele aanwijzing, geen tell. Aangehaalde marketingtekst in een analyse blijft staan. Naar een hoger niveau in een sportverslag (promotie naar de eerste divisie) is letterlijk bedoeld. Een gebiedende wijs op een knop is normaal en vaak het duidelijkst ('Meld je aan', 'Download het rapport'). Het signaal is de reeks: elke tussenkop een aansporing, en de klaar-om-vraag die niets concreets belooft. In advertentiecopy die bewust luid is, weegt dit lichter.

### Synoniemenroulatie (elegante variatie) `synonym-cycling`

Ernst: **cluster** · Herkomst: transfer · en: `synonym-cycling`

Dezelfde persoon of zaak krijgt bij elke herhaling een nieuw synoniem, alleen om het woord niet te herhalen: hoofdpersoon, centrale figuur, held; ontwikkelaars, engineers, programmeurs, bouwers; het bedrijf, de organisatie, de onderneming, de partij. Het is een spoor van de herhalingsstraf in het model, geen keuze van de schrijver. Als het heldere woord het juiste is, herhaal je het gewoon.

Signalen: `hoofdpersoon / centrale figuur / held` · `ontwikkelaars / engineers / programmeurs / bouwers` · `het bedrijf / de organisatie / de onderneming` · `de tool / de oplossing / het platform` · `de bezoeker / de deelnemer / de gast`

Voor: De hoofdpersoon krijgt tegenslagen. De centrale figuur moet obstakels overwinnen. De held keert terug.

Na: De hoofdpersoon krijgt tegenslagen, maar keert uiteindelijk terug.

Niet markeren: Geen regex mogelijk: dit is een leesregel over één referent binnen één alinea. In het Nederlands doen ook redacteuren dit vanwege de schoolregel dat je een woord niet twee keer mag gebruiken, dus het bewijst op zichzelf niets. Waar de synoniemen een echt onderscheid maken (de gemeente tegenover de provincie), is het geen roulatie.

### Bijwoord van stille betekenis (stilletjes, diepgeworteld) `understated-significance-adverb`

Ernst: **cluster** · Herkomst: transfer · en: `understated-significance-adverb`

Een bijwoord of bijvoeglijk naamwoord dat subtiel belang beweert in plaats van het te tonen, waardoor een gewone beschrijving zwaar aanvoelt: stilletjes, in stilte, ongemerkt, diepgeworteld, diep verankerd, fundamenteel anders, wezenlijk anders. Schrap het, of noem het concrete contrast dat het ding stil of diep maakt.

Signalen: `stilletjes` · `in stilte` · `ongemerkt` · `diepgeworteld` · `diep verankerd` · `diep menselijk` · `fundamenteel anders` · `wezenlijk anders`

Voor: Het heeft stilletjes veranderd hoe teams werken.

Na: Vier van de zes teams zijn er vorig kwartaal op overgestapt, zonder aankondiging.

Niet markeren: In stilte en ongemerkt kunnen letterlijk zijn (in stilte herdacht, ongemerkt langs de douane) en staan daarom niet allebei in de regex. Diepgeworteld over een traditie die aantoonbaar eeuwenoud is, met de eeuwen erbij, is een bewering.

### Vage lofadjectieven (jeukwoorden) `vague-praise-adjectives`

Ernst: **cluster** · Herkomst: transfer · en: `vague-praise-adjectives`

Waarderende bijvoeglijke naamwoorden die kwaliteit, nieuwheid of belang beweren zonder meetbaar aanknopingspunt: krachtig, innovatief, geavanceerd, dynamisch, hoogwaardig, uniek, ongekend, impactvol. Twee subvormen erbovenop: de reclamesuperlatieven (wereldklasse, state-of-the-art, revolutionair, van topkwaliteit) en het vage superlatief als vaste frase (een krachtige manier om, een cruciale stap in het proces, een effectieve aanpak). Los is elk woord verdedigbaar; de opeenhoping in één tekst is de tell. Vervang door een getal, een vergelijking of de concrete eigenschap.

Signalen: `innovatief` · `geavanceerd` · `dynamisch` · `hoogwaardig` · `uniek` · `ongekend` · `uitzonderlijk` · `opmerkelijk` · `schaalbaar` · `indrukwekkend` · `adembenemend` · `revolutionair` · `wereldklasse` · `state-of-the-art` · `van topkwaliteit` · `bevlogen` · `gedreven` · `met passie` (+6)

Voor: Een innovatief platform van wereldklasse met indrukwekkende resultaten.

Na: Het platform verwerkte in de test van maart 40.000 verzoeken per seconde, vier keer zoveel als het oude.

Niet markeren: Uniek, gedreven en efficiënt zijn in Nederlandse bedrijfscopy zo gewoon dat ze pas bij verzadiging tellen. In een productspecificatie is hoogwaardig soms een gedefinieerde kwaliteitsklasse. Eén los adjectief in een verder concrete tekst is geen treffer; citaten en aangehaalde slogans blijven staan.

### Graadbijwoorden als vulling (ontzettend, simpelweg, uiterst) `degree-adverb-padding`

Ernst: **context** · Herkomst: transfer · en: `degree-adverb-padding`

Versterkende graadbijwoorden op gezegdes die ze niet nodig hebben: ontzettend, ongelooflijk, simpelweg, uiterst, bijzonder, heel erg, best wel, volledig, compleet, enorm. Meestal schrappen; waar nadruk echt nodig is, zet je er een getal of een sterker werkwoord neer.

Signalen: `ontzettend` · `ongelooflijk` · `simpelweg` · `letterlijk` · `uiterst` · `bijzonder` · `heel erg` · `best wel` · `volledig` · `compleet` · `enorm`

Voor: Het is eigenlijk heel erg simpel, echt waar.

Na: Het kost één commando.

Niet markeren: Heel, erg, zeer, uiterst en bijzonder los zijn te gewoon voor een regex; poort ze op dichtheid per alinea. Letterlijk dat echt letterlijk betekent (hij vertaalde het letterlijk) is inhoudelijk. In gesproken en informele registers hoort een graadbijwoord bij de stem: markeer daar alleen de stapeling.

### Ontwikkelaarsslogans (het werkt gewoon, zonder gedoe) `dev-blog-boilerplate`

Ernst: **context** · Herkomst: transfer · en: `dev-blog-boilerplate`

Vaste eenvoudsslogans uit developermarketing die in de plaats komen van een eigenschap die je kunt laten zien: het werkt gewoon, out of the box, zonder gedoe, zonder configuratie, plug-and-play, in een handomdraai, binnen no-time, zo geregeld. Noem het concrete gedrag: hoeveel stappen, welk bestand, hoeveel functies.

Signalen: `het werkt gewoon` · `out of the box` · `zonder gedoe` · `zonder configuratie` · `plug-and-play` · `in een handomdraai` · `binnen no-time` · `zo geregeld` · `in vijf minuten draaiend`

Voor: Plug-and-play, zonder gedoe, en het werkt gewoon.

Na: Je installeert het zonder configuratiebestand, en de hele API is zes functies.

Niet markeren: Out of the box en plug-and-play zijn in hardwaredocumentatie ingeburgerde vaktermen met een precieze betekenis (werkt zonder extra driver). In een citaat uit marketingmateriaal blijven ze staan. Eén slogan naast een concrete uitleg is geen treffer.

### Wisseling van taalvariëteit (Belgisch-Nederlands en Nederlands-Nederlands door elkaar) `english-variety-drift`

Ernst: **context** · Herkomst: transfer · en: `english-variety-drift`

Een mismatch tussen de lezer, het onderwerp en de gekozen variëteit: Belgisch-Nederlandse woorden in een tekst voor een Nederlandse lezer of andersom (gsm naast mobiel, plezant, goesting, seffens, kuisen, ambetant, enkel voor alleen), of een wisseling halverwege hetzelfde document. Kies één variëteit en houd hem vast.

Signalen: `gsm naast mobiel` · `plezant` · `goesting` · `seffens` · `kuisen` · `ambetant` · `enkel voor alleen` · `wisseling halverwege de tekst`

Voor: Een tekst voor een Nederlandse klant die halverwege van mobiel op gsm overstapt.

Na: Eén variëteit door de hele tekst, passend bij de lezer.

Niet markeren: Geen regex: voor een Vlaamse schrijver of een Vlaams publiek is gsm, goesting of plezant gewoon de juiste variëteit. Controleer eerst wie de tekst schreef en voor wie hij bedoeld is. Spelling geeft in het Nederlands geen tweede as zoals -ize en -ise in het Engels, dus alleen woordkeuze telt.

### Lege slagen om de arm (wellicht, zou kunnen, enigszins) `hedging`

Ernst: **context** · Herkomst: transfer · en: `hedging`

Verzachtende woorden en bijzinnen die een bewering verdunnen zonder echte onzekerheid uit te drukken: wellicht, mogelijkerwijs, zou kunnen, lijkt, enigszins, in zekere zin, naar verwachting, in sommige gevallen. Elk wordt een concrete bewering of verdwijnt. Let op de tegenindicator: kleine slagen om de arm komen juist vaker voor in menselijk proza dan in machinetekst, dus hun aanwezigheid bewijst weinig; de stapeling in één zin is het signaal.

Signalen: `wellicht` · `mogelijkerwijs` · `zou kunnen` · `lijkt` · `enigszins` · `in zekere zin` · `naar verwachting` · `misschien` · `ik denk dat` · `in sommige gevallen`

Voor: Dit zou de doorvoer mogelijk enigszins kunnen verbeteren.

Na: De doorvoer ging in de test met ongeveer 15 procent omhoog.

Niet markeren: In wetenschappelijke en medische tekst is voorzichtig formuleren de norm en soms een eis van de tijdschriftstijl. Wellicht, misschien en lijkt los zijn gewoon Nederlands en staan niet in de regex. Waar de onzekerheid echt is (een prognose, een lopend onderzoek) is de slag om de arm inhoudelijk.

### Aanname die niet langer waar is `ontological-slop-assumptions`

Ernst: **context** · Herkomst: transfer · en: `ontological-slop-assumptions`

Een aanname of vuistregel beschrijven alsof die van waar naar onwaar omklapt. Aannames verliezen hun bruikbaarheid, niet hun waarheidswaarde. Schrijf dat de aanname niet meer opgaat, dat hij het begeeft, of noem de schaal waarop hij stukloopt.

Signalen: `de aanname is niet langer waar` · `die veronderstelling is niet meer waar` · `houdt op waar te zijn`

Voor: Op schaal is die aanname niet langer waar.

Na: Vanaf ongeveer duizend gebruikers gaat die aanname niet meer op.

Niet markeren: Over een feitelijke bewering die inderdaad achterhaald is (de bewering dat er twee stations zijn, is niet meer waar) is dit gewoon correct Nederlands. In logica en wiskunde klapt een propositie wel degelijk van waar naar onwaar. Alleen aannames, veronderstellingen en vuistregels tellen.

### Echt en werkelijk als lege versterker `real-actual-adjective-inflation`

Ernst: **context** · Herkomst: transfer · en: `real-actual-adjective-inflation`

Echte, werkelijke, daadwerkelijke of ware als lege versterker op een abstract zelfstandig naamwoord: echte meerwaarde, werkelijke impact, de ware kracht van, echte behoefte. Het suggereert dat de rest van het veld nep is zonder ooit te zeggen wat deze versie echt maakt. Laat het bijvoeglijk naamwoord weg en zet de concrete bewering ervoor in de plaats.

Signalen: `echte meerwaarde` · `echte impact` · `werkelijke waarde` · `daadwerkelijke resultaten` · `de ware kracht van` · `echte behoefte` · `echte verandering`

Voor: Eindelijk echte meerwaarde voor onze klanten.

Na: Klanten hoeven hun adres niet meer over te typen; dat scheelt bij elke bestelling een minuut.

Niet markeren: Waar het bijvoeglijk naamwoord een echt contrast met een schijnvorm maakt (de werkelijke kosten tegenover de begrote), draagt het informatie. In een citaat blijft het staan. De ware kracht van in een sportverslag over een ploeg kan een beschreven eigenschap inleiden.

### Modewoord uit de tijdlijn (hits different, next level) `trendy-colloquialism`

Ernst: **context** · Herkomst: transfer · en: `trendy-colloquialism`

Een geleende trendfrase als kortere weg naar herkenbaarheid, zonder de emotie te verdienen: hits different, raakt anders, next level, gaat hard, is een vibe, chef's kiss. In Nederlandse tekst blijft deze categorie meestal onvertaald Engels en overlapt daarmee met het onvertaalde marketingleenwoord. Beschrijf wat er werkelijk veranderde, of schrap.

Signalen: `hits different` · `raakt anders` · `next level` · `gaat hard` · `is een vibe` · `geen woorden voor` · `chef's kiss`

Voor: Die changelog lezen hits different.

Na: In die changelog stond precies de bug waar ik dinsdag op vastliep.

Niet markeren: In een post die zelf over internettaal gaat, of in een citaat van een deelnemer, is de frase het onderwerp. Voor een schrijver die zo praat en dat door de hele tekst volhoudt, is het stem en geen tell: de tell is de losse frase in verder neutrale tekst.

### Te formeel register: de partikels ontbreken `uncontracted-forms`

Ernst: **context** · Herkomst: transfer · en: `uncontracted-forms`

Spreektaalcopy zonder de woordjes die Nederlands gesproken maken. Het Engelse mechanisme (geen samentrekkingen als isn't en won't) bestaat hier niet; de Nederlandse tegenhanger is dat de modale partikels wegvallen (even, maar, toch, nou, hoor, hè, eens, wel) en dat men dient, alsmede, het verdient aanbeveling en zich bevindt ervoor in de plaats komen. Schrijf zoals je het zou zeggen en zet de partikels terug.

Signalen: `men dient` · `men kan` · `alsmede` · `dan wel` · `zich bevindt` · `het verdient aanbeveling` · `ontbrekende partikels: even, maar, toch, nou, hoor, hè, eens`

Voor: Men dient zich vooraf aan te melden, alsmede de betaling te voldoen.

Na: Meld je van tevoren aan en betaal er gelijk voor.

Niet markeren: De afwezigheid van partikels is niet met een regex te vangen en is in een reglement, een akte of een encyclopedie de juiste toon: markeer alleen in copy die spreektaal wil zijn. Alsmede en dan wel staan niet in de regex omdat ze in juridische opsommingen een precieze functie hebben. Behandel dit vooral als bewaarregel: laat even, maar, toch en nou staan waar de stem ze zou gebruiken.

### Onverklaard jargon `undefined-jargon`

Ernst: **context** · Herkomst: transfer · en: `undefined-jargon`

Een vakterm gebruikt zonder uitleg waar je niet mag aannemen dat de lezer hem kent, of bedrijfstaal die de tekst moeilijker maakt zonder preciezer te worden. Geef de term één bijzin uitleg, of vervang hem door de gewone bewoording. Verwijder alleen wat het lezen in de weg zit, nooit de inhoud of de precisie.

Signalen: `afkorting zonder uitleg` · `vakterm zonder bijzin` · `interne projectnaam zonder toelichting`

Voor: We hebben de reconciliatielus achter de CRD gezet.

Na: We hebben de reconciliatielus, de controller die de echte toestand gelijk houdt aan de configuratie, achter een eigen Kubernetes-resource gezet.

Niet markeren: Geen regex: welke term jargon is, hangt af van de lezer. In documentatie voor vakgenoten is de vakterm juist het precieze woord en kost uitleg alleen ruimte. Schrap nooit een term omdat hij moeilijk is; leg hem uit of laat hem staan.

## Alinea- en documentstructuur

### Ondanks-de-uitdagingen-slot `despite-challenges-outlook`

Ernst: **always** · Herkomst: nl-bron · en: `despite-challenges-outlook`

Een vast slotblok, vaak onder een kop als 'Uitdagingen en toekomstperspectief', dat in twee slagen werkt: eerst kampt het onderwerp met uitdagingen, dan blijft het ondanks die uitdagingen floreren. Problemen worden alleen benoemd om ze weg te wuiven, meestal gevolgd door speculatie over wat investeringen of inzet zouden kunnen brengen. Er komt geen enkel feit bij.

Signalen: `Ondanks deze uitdagingen` · `Ondanks deze successen` · `Ondanks zijn populariteit` · `kampt met uitdagingen` · `staat voor verschillende uitdagingen` · `blijft floreren` · `blijft gedijen` · `blijft een belangrijke rol spelen` · `Uitdagingen en toekomstperspectief` · `Uitdagingen en kansen` · `Toekomstperspectieven` · `Vooruitblik` · `met de juiste inzet` · `met de juiste investeringen` · `de toekomst zal uitwijzen` · `zal de komende jaren`

Voor: Ondanks deze successen staat de meetup voor verschillende uitdagingen, waaronder groei en financiering. Met de juiste inzet kan het initiatief echter blijven bijdragen aan de regio.

Na: De meetup zoekt sinds juni een grotere zaal, want bij zestig aanmeldingen zit de huidige locatie vol.

Niet markeren: 'Ondanks de uitdagingen' met daarna een uitdaging die een naam, een datum en een gevolg heeft, is gewoon proza. Een subsidieaanvraag, beleidsstuk of jaarverslag heeft een voorgeschreven vooruitblik; daar is de kop geen signaal, de leegte eronder wel. Ook een echte risicoparagraaf met genoemde risico's telt niet mee.

### Kop herhaald in de eerste regel `heading-restated-below`

Ernst: **always** · Herkomst: transfer · en: `heading-restated-below`

Op een kop volgt een regel die de kop alleen herhaalt voordat de echte inhoud begint: '## Veiligheid' gevolgd door 'Veiligheid is belangrijk.' De luidste variant zet het kopwoord als eerste woord van de eerste zin en zegt er alleen van dat het onderwerp belangrijk is. De aanloopregel doet het werk van de kop nog een keer.

Signalen: `## Prestaties, daarna 'Prestaties zijn belangrijk.'` · `## Veiligheid, daarna 'Veiligheid is cruciaal.'` · `kopwoord als eerste woord van de eerste zin` · `eerste regel zegt alleen dat het onderwerp belangrijk is`

Voor: ## Prestaties

Prestaties zijn belangrijk.

Wie een trage pagina opent, klikt weg.

Na: ## Prestaties

Wie een trage pagina opent, klikt weg.

Niet markeren: Een definiërende openingszin in een lemma of glossarium herhaalt het kopwoord met opzet: 'Rijssen is een stad in Overijssel.' Die vorm is de norm, want de zin voegt een categorie en een plaats toe. Het signaal is de herhaling die niets toevoegt behalve een oordeel over het belang.

### Vetgedrukte bullet-openers `inline-header-lists`

Ernst: **always** · Herkomst: transfer · en: `inline-header-lists`

Elk lijstitem opent met een kort vet label en een dubbele punt, gevolgd door een zin die het label meestal herhaalt. Subvormen: dezelfde vorm zonder leesteken, de genummerde variant, en de aankondigende regel boven de lijst ('De belangrijkste punten:', 'bestaat uit drie kernonderdelen:'). In dezelfde familie hoort het vet in de lopende tekst dat losse woorden benadrukt.

Signalen: `- **Gebruikerservaring:**` · `- **Prestaties:**` · `- **Veiligheid:**` · `**Kernpunt**:` · `- **Wat het is:**` · `- **Waarom het werkt:**` · `De belangrijkste punten:` · `bestaat uit drie kernonderdelen:` · `1. Kop: tekst` · `1. **Aanpak:** uitleg` · `bullet points met vetgedrukte koppen` · `overmatig vetgedrukte woorden`

Voor: - **Gebruikerservaring:** De gebruikerservaring is sterk verbeterd met een nieuwe interface.
- **Prestaties:** De prestaties zijn verbeterd door geoptimaliseerde algoritmes.

Na: De update brengt een nieuwe interface, en pagina's laden sneller omdat de sortering herschreven is.

Niet markeren: Een definitielijst, een glossarium, een changelog en een parameter- of optietabel dragen het label met opzet, want de lezer zoekt op het label. Dat geldt ook voor releasenotes en een FAQ. Het signaal is het label dat de zin erna gewoon herhaalt. Let bij wikitext ook op geneste opsommingen, die met twee sterretjes beginnen.

### Aanloop voor het punt `preamble-before-the-point`

Ernst: **always** · Herkomst: transfer · en: `preamble-before-the-point`

Het stuk opent met brede context voordat het iets specifieks zegt: een wijdse openingszin over de wereld van vandaag, achtergrondalinea's die niets toevoegen, of onderbouwing die vóór het punt staat dat ze onderbouwt. Ook de tweeledige slogan-opener hoort hier: een openingsregel die zegt wat het niet is in plaats van wat er gebeurt. Schrap de wijdse zin en begin bij de tweede.

Signalen: `In de snel veranderende wereld van vandaag` · `In het huidige digitale landschap` · `In een tijd waarin` · `In de wereld van vandaag` · `belangrijker dan ooit` · `Het is geen geheim dat` · `Sinds jaar en dag` · `In een steeds digitaler wordende samenleving` · `slogan-opener die zegt wat het niet is`

Voor: In de snel veranderende digitale wereld van vandaag hebben teams snellere builds nodig. Wij brachten de onze terug van veertig naar zes minuten.

Na: We brachten onze build terug van veertig naar zes minuten.

Niet markeren: Een openingsanekdote die spanning, context of karakter oplevert is geen aanloop. In een wetenschappelijk artikel hoort de brede inleiding bij het genre, mits ze naar de vraagstelling toe werkt. Ook een lemma opent met een definiërende zin. Het signaal is de openingszin die je kunt schrappen zonder dat er iets verdwijnt.

### Aangekondigde conclusie (Kortom-slot) `signposted-conclusion`

Ernst: **always** · Herkomst: nl-bron · en: `signposted-conclusion`

De tekst of de alinea sluit af met een gemarkeerde samenvatting die herhaalt wat er net stond. Subvormen: het signaalwoord aan het begin van de slotalinea (Kortom, Samenvattend, Concluderend, Al met al), de alinea die met een samenvattende zin dichtklapt in plaats van door te stoten, en de vertaalrest In conclusie of Als conclusie, die als Nederlandse formule niet bestaat. De lezer was er net; het slot voegt niets toe.

Signalen: `Kortom` · `Samenvattend kunnen we zeggen` · `Kort samengevat` · `Concluderend` · `Resumerend` · `Al met al` · `Alles bij elkaar genomen` · `Om het samen te vatten` · `Om af te sluiten` · `Tot slot kunnen we stellen` · `In conclusie` · `Als conclusie` · `Uiteindelijk komt het erop neer dat` · `Onthoud dat` · `Aan het eind van de dag`

Voor: Kortom, de meetup is een waardevolle toevoeging aan de regio.

Na: (zin schrappen; de alinea erboven zegt het al)

Niet markeren: In een scriptie, onderzoeksrapport, jaarverslag of juridische tekst is een aangekondigde conclusie voorgeschreven en geen signaal. 'Tot slot' als laatste item van een opsomming of als overgang naar een echt nieuw punt is gewoon Nederlands. 'Samenvattend' in een abstract of managementsamenvatting hoort daar. Eén slotmarkeerder in een lang stuk is geen tell; het patroon is de markeerder boven een alinea die niets nieuws zegt.

### Opsomming van kale naamwoordgroepen `bare-noun-phrase-bullets`

Ernst: **cluster** · Herkomst: transfer · en: `bare-noun-phrase-bullets`

Vijf of meer bullets achter elkaar die elk een korte naamwoordgroep zijn, hoogstens zes woorden, zonder persoonsvorm en zonder een enkel controleerbaar gegeven. De symmetrie is de tell: een echte lijst waarnemingen varieert in lengte, heeft af en toe een werkwoord en heeft één item dat uit de pas loopt. Herschrijf elk item als een claim met een getal, of maak er proza van.

Signalen: `- Stabiele prestaties` · `- Betrouwbare verbinding` · `- Efficiënte inzet van middelen` · `- Consistente kwaliteit` · `- Geoptimaliseerde doorvoer` · `reeks van vijf of meer items van twee tot zes woorden zonder persoonsvorm`

Voor: - Stabiele mining-efficiëntie
- Betrouwbare poolverbinding
- Geoptimaliseerde RandomX-prestaties
- Laag aandeel mislukte shares
- Effectieve inzet van hardware

Na: Over twaalf uur bleef de hashrate binnen 2 procent van nominaal. De heetste kern zat op 71 graden.

Niet markeren: Kale naamwoordgroepen horen in een boodschappenlijst, een ingrediëntenlijst, YAML-frontmatter, tags, een menukaart, een agenda en een specificatietabel. Ook een cv en een pakketlijst bestaan er per definitie uit. De poort is de reeks van vijf of meer kale items in lopende tekst waar een lezer een bewering verwacht.

### Bullets waar proza hoort `bullets-instead-of-prose`

Ernst: **cluster** · Herkomst: nl-bron · en: `bullets-instead-of-prose`

Samenhangende gedachten worden in bullets gehakt, vaak genest, terwijl twee zinnen proza het werk doen. Rondom de bullets komt de rest van de overstructurering mee: een kop per paar zinnen, scheidingslijnen tussen alle delen, een tabel voor twee gegevens. Bij de tweede opsomming denkt de lezer dat het blijkbaar toch niet zo belangrijk is.

Signalen: `acht of meer bullets in minder dan 200 woorden` · `drie bulletblokken achter elkaar` · `geneste bullets voor samenhangende gedachten` · `lijst waar twee zinnen proza volstaan` · `in elke alinea een opsomming` · `scheidingslijnen tussen alle secties` · `een tabel voor twee gegevens` · `leest als een stappenplan in plaats van een verhaal`

Voor: - De latency daalde
  - Doordat we het token cachen
    - Wat ook de 401's oploste

Na: De latency daalde toen we het token gingen cachen, wat meteen de 401's oploste.

Niet markeren: Documentatie, releasenotes, boodschappenlijsten, checklists, agenda's en vergelijkingen zijn lijstgenres; daar is proza de fout. Ook een opsomming van gelijkwaardige, zelfstandige items hoort in bullets. Het signaal is de lijst die een redenering vervangt, waarin de items op elkaar steunen.

### Sjabloon-profielpagina `canned-profile-page`

Ernst: **cluster** · Herkomst: transfer · en: `canned-profile-page`

Een profiel- of biopagina volgens een vast sjabloon: koppen als Over mij, Mijn interesses en Laten we connecten, bullets met een emoji per item, vetgedrukte aantallen en een opgewekte afsluiter. Dezelfde vorm verschijnt op LinkedIn, op GitHub en op een gebruikerspagina. Twee of drie gewone zinnen over wat iemand werkelijk doet vervangen het geheel.

Signalen: `Over mij` · `Wie ben ik` · `Mijn interesses` · `Mijn bijdragen` · `Laten we connecten!` · `Laten we samenwerken` · `Neem gerust contact met mij op` · `Stuur me gerust een bericht` · `Veel plezier!` · `20+ artikelen`

Voor: == Over mij ==
* Ik schrijf graag over Twentse techbedrijven.
== Laten we connecten! ==
Neem gerust contact met mij op als je wilt samenwerken!

Na: Ik schrijf over techbedrijven in Twente, meestal over de maakindustrie. Een stuk of twintig artikelen inmiddels, en mijn overlegpagina staat open.

Niet markeren: 'Over mij' is op een portfolio of een website een gangbare, verwachte kop, en 'neem gerust contact op' hoort in zakelijke copy op een contactpagina. Een sollicitatiebrief mag een opgewekte afsluiter hebben. Het signaal is het hele sjabloon: de vaste koppenreeks met emoji-bullets en aantallen zonder inhoud.

### Cirkelslot `circular-return-ending`

Ernst: **cluster** · Herkomst: transfer · en: `circular-return-ending`

De slotzin keert terug naar het openingsbeeld of de openingsvraag in plaats van ergens nieuws te landen. Symmetrie vervangt het punt: de tekst voelt af omdat hij rond is, niet omdat er iets is beslist. In het Nederlands meestal korter dan in het Engels, vaak als 'daarmee is de cirkel rond'.

Signalen: `En zo zijn we terug bij het begin` · `Daarmee zijn we terug bij de vraag waarmee we begonnen` · `Terug bij af` · `Zoals we aan het begin al zeiden` · `En daarmee is de cirkel rond`

Voor: En zo zijn we terug bij het begin: is de tool het waard?

Na: Vanaf tien man verdient de tool zichzelf terug. Daaronder kost het opzetten meer dan het oplevert.

Niet markeren: In een column, essay of speech is de terugkeer naar het openingsbeeld een erkende figuur, mits de betekenis ervan bij de tweede keer verschoven is. Een verhaal dat op dezelfde plek eindigt om iets te tonen, is geen signaal. Het patroon is de terugkeer die alleen de vorm sluit.

### Dubbelepuntkop `colon-subtitle-headings`

Ernst: **cluster** · Herkomst: nl-bron · en: `colon-subtitle-headings`

Elke kop volgt hetzelfde schema: een pakkende frase, een dubbele punt, en dan de uitleg of de belofte. De luidste variant is de transformatieformule 'Van X naar Y: hoe je Z', met een tegenstellingspaar voor de dubbele punt. Eén dubbelepuntkop is redactionele praktijk; het signaal is dat elke kop in het document hem heeft.

Signalen: `Van X naar Y: hoe Z` · `Van chaos naar controle` · `kop met een dubbele punt in het midden` · `De complete gids: alles over ...` · `De ultieme gids voor` · `Titel: een diepere blik` · `elke tussenkop volgens hetzelfde schema` · `X: waarom het werkt` · `N manieren om` · `Zo doe je het in N stappen`

Voor: Van chaos naar controle: hoe je met AI je contentproces stroomlijnt

Na: Wat er misging toen we ons contentproces aan AI overlieten

Niet markeren: Een wetenschappelijke hoofdtitel met ondertitel heeft de dubbele punt als conventie, net als een serietitel of een aflevering ('Deel 2: de migratie'). Ook een kop die een echte tweedeling draagt, zoals 'Rijssen: de kerk en de schoenfabriek', is gewoon een kop. Het patroon is de herhaling over alle koppen, of het tegenstellingspaar zonder inhoud.

### Toegeven-redden-weerleggen `concede-salvage-rebut-template`

Ernst: **cluster** · Herkomst: transfer · en: `concede-salvage-rebut-template`

Wijst iemand op een fout en geeft het model die toe, dan volgt de eerste alinea een vaste drieslag: geef de ander gelijk, wijs aan wat nog wel klopt, en sluit af met een variant van 'maar dat is niet alles wat er speelt, en daar zit precies je punt'. De correctie wordt zo een compliment aan de corrigeerder. Beantwoord de correctie gewoon.

Signalen: `Je hebt gelijk dat` · `Je hebt helemaal gelijk` · `Dat klopt, en toch` · `Maar dat is niet alles wat er speelt` · `En daar zit precies je punt` · `Goed punt, en het gaat nog verder`

Voor: Je hebt gelijk dat de cache helpt. Hij halveert de p95 nog steeds. Maar dat is niet alles wat hij doet, en daar zit precies je punt.

Na: Klopt, de cache verbergt ook de retry-bug. Ik pak de retry eerst aan.

Niet markeren: 'Je hebt gelijk dat' is in een gewoon gesprek een normale opening, zeker als er daarna iets concreets volgt dat de ander niet wist. Een echte nuancering met een eigen argument is geen sjabloon. Het signaal is de drieslag als geheel, en de slotzin die de correctie terugkaatst als lof.

### Koppen die alleen koppen bevatten `empty-parent-headings`

Ernst: **cluster** · Herkomst: transfer · en: `empty-parent-headings`

Een kop waarvan de hele inhoud uit lagere koppen bestaat, zonder een zin ertussen. De opzet is als sectie gerenderd: de tak uit het plan werd een kop, ook al heeft hij niets eigens te zeggen. Geef de bovenliggende kop een zin die hem verdient, of haal hem weg en promoveer de kinderen.

Signalen: `kop direct gevolgd door een subkop` · `## Sectie gevolgd door ### Subsectie` · `= Sectie = gevolgd door == Subsectie ==` · `geen enkele regel proza onder een hoofdkop`

Voor: ## Hoofdpersonen

### Pixy

[...]

Na: ### Pixy

[...]

Niet markeren: Naslagstructuren mogen lege ouders hebben: een API-referentie, een inhoudsopgave, een specificatie of een wettekst waar de nummering de structuur draagt. In een lang lemma is een kop met alleen subkoppen ook gebruikelijk. Het signaal is de lege ouder in lopend proza.

### Vijfparagrafenopstel en drieslagsteiger `five-paragraph-essay`

Ernst: **cluster** · Herkomst: transfer · en: `five-paragraph-essay`

Inleiding, drie middenstukken en een samenvattend slot, opgelegd bij elke lengte, ook bij een antwoord van honderd woorden. Subvormen: drie punten per sectie ongeacht het echte aantal, en drie alinea's op rij die met de vaste these-antithese-synthesevoegwoorden openen. Het Nederlandse schoolopstel kent dezelfde vorm, dus de vorm alleen bewijst niets; de tell is de vorm bij een lengte die er niet om vraagt.

Signalen: `Er zijn drie redenen` · `Eerst ... Daarentegen ... Uiteindelijk` · `drie punten in elke sectie` · `Bij elkaar tonen deze drie` · `een inleiding, drie tot vijf punten met kopjes, en een conclusie` · `elke paragraaf heeft een tussenkop`

Voor: Er zijn drie redenen waarom dit ertoe doet. Ten eerste de kosten. Ten tweede de snelheid. Ten derde het vertrouwen. Samen laten deze drie redenen zien waarom dit ertoe doet.

Na: Het is goedkoper, en de snelheidswinst gaf de doorslag.

Niet markeren: Een examenopstel, een betoog voor school en een debatbijdrage worden op deze vorm beoordeeld; daar is hij de opdracht. Ook een advies met precies drie opties is geen steiger. Het signaal is het vaste aantal van drie dat terugkomt in secties die er niet om vragen, en de slotzin die de drie nog eens optelt.

### Sjabloonkoppen `formulaic-section-headers`

Ernst: **cluster** · Herkomst: nl-bron · en: `formulaic-section-headers`

Koppen die een vakje uit het sjabloon benoemen in plaats van de inhoud eronder: Inleiding, Overzicht, Samenvatting, Conclusie, Belangrijkste punten, Prijzen en erkenning. Twee subvormen: de verplichte combinatie van een inleidende en een afsluitende sectie ongeacht het genre, en de woordelijk vertaalde Amerikaanse artikelkop (Waarom dit ertoe doet, Wat je moet weten, De bottom line). De kop zegt niets wat de lezer niet al ziet.

Signalen: `## Inleiding` · `## Overzicht` · `## Samenvatting` · `## Conclusie` · `## Belangrijkste punten` · `## Kernpunten` · `## Kerncijfers` · `## Achtergrond` · `## Tot slot` · `## Prijzen en erkenning` · `## Vragen om over na te denken` · `Waarom dit ertoe doet` · `Wat je moet weten` · `Belangrijkste inzichten` · `Wat betekent dit voor jou` · `De bottom line` · `Key takeaways`

Voor: ## Belangrijkste punten

Na: ## Wat de migratie kostte

Niet markeren: In een scriptie, onderzoeksrapport, offerte, ADR of beleidsnota zijn 'Inleiding' en 'Conclusie' de voorgeschreven kopnamen. Op een productpagina is 'Hoe het werkt' een gangbare Nederlandse kop. Eén sjabloonkop in een lang document is geen tell; het signaal is de reeks, of de kop in een genre dat er geen kent, zoals een lemma, een blogpost of een README.

### Fractale samenvattingen `fractal-summaries`

Ernst: **cluster** · Herkomst: transfer · en: `fractal-summaries`

Zeg wat je gaat zeggen, zeg het, zeg wat je gezegd hebt, op elk niveau. Onder elke kop staat een aankondigingszin, aan het eind van elke sectie of alinea een minisamenvatting, en de volgende sectie opent met een recap van de vorige. De kop kondigt al aan wat er komt, dus de aankondigingszin doet dat werk twee keer.

Signalen: `In deze sectie bespreken we` · `In dit hoofdstuk behandelen we` · `In dit onderdeel kijken we naar` · `In deze paragraaf gaan we in op` · `Zoals we hebben gezien` · `Zoals hierboven beschreven` · `In het vorige hoofdstuk zagen we` · `Samengevat:` · `Vier kanttekeningen vooraf` · `Drie dingen vooraf` · `elke alinea eindigt met een samenvatting`

Voor: In deze sectie bespreken we hoe caching werkt. [...] Zoals we in deze sectie hebben gezien, verlaagt caching de latency.

Na: Caching haalt de p95 omlaag, omdat het token nu één keer per uur wordt opgehaald in plaats van bij elk verzoek.

Niet markeren: In academisch proza, een handboek of een lange technische gids verwijst 'zoals we hebben gezien' vaak echt naar een eerdere passage, en dan is het een verwijzing en geen sjabloon. Leerboeken en cursusmateriaal kondigen hun hoofdstukken bewust aan. Het signaal is de vaste plaatsing: onder elke kop dezelfde aankondiging, achter elke sectie dezelfde recap.

### Koppen boven te korte tekst `headers-over-short-text`

Ernst: **cluster** · Herkomst: transfer · en: `headers-over-short-text`

Kopjes worden opgelegd aan tekst die te kort is om navigatie nodig te hebben: een kop boven twee zinnen, meer dan drie koppen in minder dan driehonderd woorden, of getitelde secties in een reactie of een e-mail. Subvormen: het tussenkopje dat alleen het onderwerp van de volgende alinea benoemt, en het kopje in een essay of column, waar kopjes ongebruikelijk zijn. De koppen dienen het sjabloon, niet de lezer.

Signalen: `weinig zinnen onder een tussenkopje` · `meer dan drie koppen in minder dan 300 woorden` · `kopjes in een reactie of comment` · `kopjes die het onderwerp van de volgende alinea aankondigen` · `## Context` · `## Analyse` · `## Aanleiding` · `## Aanpak` · `## Resultaat`

Voor: ## Context

We zagen een piek.

## Analyse

Die kwam van de cronjob.

## Conclusie

We verzetten hem.

Na: We zagen een piek. Die kwam van de cronjob, dus we hebben hem naar 03:00 verzet.

Niet markeren: Naslagwerk, documentatie en runbooks worden gescand en niet gelezen; daar is een kop boven drie regels functioneel. FAQ's, changelogs en formulieren bestaan uit korte secties met een kop. Een handleiding met genummerde stappen valt er ook buiten. De poort is de verhouding koppen tot woorden in lopende tekst.

### Lijstje als proza `listicle-in-prose`

Ernst: **cluster** · Herkomst: transfer · en: `listicle-in-prose`

Genummerde punten vermomd als lopende tekst: opeenvolgende zinnen of alinea's die elk met een rangtelwoord openen, of inline-markeringen 1) 2) 3) binnen één alinea. Vaak het gevolg van de opdracht om te stoppen met lijstjes: de vorm verdwijnt, de steiger blijft staan. In geschreven Nederlands zijn 'eerst' en 'daarna' gewoner dan 'ten eerste' en 'ten tweede'.

Signalen: `Ten eerste` · `Ten tweede` · `Ten derde` · `Allereerst` · `Vervolgens` · `Daarnaast` · `Tot slot` · `De eerste reden is` · `De tweede stap is` · `1) ... 2) ... 3)`

Voor: De eerste muur is het ontbreken van een gratis API. De tweede muur is het ontbreken van gedelegeerde toegang. De derde muur is het ontbreken van scopes.

Na: De echte muur zijn de ontbrekende scopes. Zonder die heb je aan een gratis API weinig.

Niet markeren: In een betoog, een juridische tekst of een vergadernotitie zijn 'ten eerste' en 'ten tweede' de nette manier om twee argumenten uit elkaar te houden, zeker bij twee of drie items. Een echte procedure mag genummerd zijn. Het signaal is de reeks van vier of meer, of het rangtelwoord boven punten die niet parallel zijn.

### Verhaaldefaults: vast perspectief, vlak tempo, alles rond `narrative-flatness`

Ernst: **cluster** · Herkomst: transfer · en: `narrative-flatness`

Fictie kiest een verteltrant en houdt die met onnatuurlijke consequentheid vast, zonder drift tussen vrije indirecte rede, innerlijke monoloog en buitenscene. Elke scene loopt op hetzelfde tempo, zonder weglating, samenvatting of versnelling, en het einde knoopt elke draad dicht. Het model vertrouwt de lezer geen dubbelzinnigheid toe tenzij daarom gevraagd wordt.

Signalen: `elke scene op hetzelfde tempo` · `geen wisseling tussen vrije indirecte rede en scene` · `alle vragen aan het eind beantwoord` · `geen tijdsprong of samenvatting`

Voor: (elke scene op dezelfde afstand verteld, met een slot waarin elke vraag beantwoord wordt)

Na: (de reis in één zin, de aankomst in een bladzijde, en één vraag blijft bij de lezer liggen)

Niet markeren: Genres met een eigen belofte sluiten hun draden af: een detective wijst de dader aan, een sprookje eindigt goed, een kinderboek stelt gerust. Een korte scene hoeft geen tempowisseling te hebben. Beoordeel op de lengte van een verhaal of een hoofdstuk, niet op een fragment.

### Herhaalde zins- en alineavormen `repeated-sentence-shapes`

Ernst: **cluster** · Herkomst: translationese · en: `repeated-sentence-shapes`

Mechanische symmetrie voorbij lengte: hetzelfde alineasjabloon dat terugkeert, dezelfde volgorde van zetten, dezelfde soort slotzin, en een leestekendichtheid die van alinea tot alinea gelijk blijft. Daarbij hoort de stijl die van begin tot eind exact gelijk blijft, in toon, aanspreekvorm en woordkeus, consistenter dan een mens volhoudt. Elke zin is af, in balans en netjes, zonder ruwheid of terzijde. De vertaalde variant is mechanisch parallellisme: elke zin dezelfde bouw en ongeveer dezelfde lengte, elk onderdeel van een opsomming evenveel woorden, en alinea's die met hetzelfde woord beginnen.

Signalen: `elke alinea dezelfde volgorde van zetten` · `elke zin af, netjes en in balans` · `geen enkele terzijde of onafgemaakte zin` · `dezelfde aanspreekvorm van begin tot eind` · `tekst is te constant` · `trigramentropie functiewoorden onder 0,82` · `leestekendichtheid vlak over alle alinea's` · `drie of meer zinnen achter elkaar met dezelfde opbouw` · `bullets van gelijke lengte` · `elke alinea drie zinnen` · `elke zin begint met hetzelfde woord` · `elke tussenkop even lang` · `drieslag van gelijkgevormde woorden (sneller, slimmer, goedkoper)`

Voor: (elke alinea: stelling, uitleg, voorbeeld, afsluitende zin met dezelfde cadans)

Na: (een alinea die met een cijfer opent en na twee zinnen stopt, gevolgd door een lange)

Niet markeren: Een strak geredigeerd tijdschrift, een handleiding en een productcatalogus zijn met opzet uniform. Poëzie met een vaste vorm en een liturgische of juridische tekst leven van de herhaling. Let ook op het spiegelbeeld: abrupte stijlwissels binnen één tekst wijzen eerder op geplakte fragmenten dan op een mens. Meet over minstens zes alinea's van één auteur. Bewuste herhaling als stijlmiddel, bijvoorbeeld in een slotalinea of een speech, is geen signaal, en in technische documentatie en checklists dient gelijkvormigheid de leesbaarheid. Geen regex: dit is een oordeel over een hele passage. Het signaal is de gelijkvormigheid over de hele tekst, inclusief de alinealengte.

### Vlak zinsritme `sentence-rhythm-uniformity`

Ernst: **cluster** · Herkomst: transfer · en: `sentence-rhythm-uniformity`

Zinslengte en zinsvorm klonteren rond één instelling: of een metronomische mediaan van veertien tot tweeëntwintig woorden zonder één korte mededelende zin, of louter enkelvoudige hoofdzinnen na een opdracht om het kort te houden. Een bruikbare Nederlandse maat is de spreiding in zinslengte gedeeld door het gemiddelde, plus het aandeel zinnen dat met onderwerp en persoonsvorm opent: het Nederlands kent inversie, en gegenereerd Nederlands gebruikt die opvallend weinig.

Signalen: `alle zinnen 14 tot 22 woorden` · `alleen hoofdzinnen` · `geen enkele korte zin` · `geen zin langer dan 100 tekens` · `elke zin begint met onderwerp plus persoonsvorm` · `geen inversie in de hele tekst`

Voor: De service start. Hij laadt de configuratie. Hij opent een socket. Hij wacht op verzoeken.

Na: De service laadt zijn configuratie, opent een socket en wacht dan op verzoeken.

Niet markeren: Eenvoudig Nederlands (B1), kindertekst, ondertiteling en instructies zijn met opzet kort en gelijkmatig. Juridische en ambtelijke tekst is met opzet lang en gelijkmatig. Meet over minstens vijftien zinnen van één auteur, en niet op citaten, opsommingen of code.

### Kernzin aan het begin van elke alinea `topic-sentence-every-paragraph`

Ernst: **cluster** · Herkomst: transfer · en: `topic-sentence-every-paragraph`

Elke alinea opent met een samenvattende kernzin, de vorm uit het Angelsaksische opstelonderwijs. Het Nederlandse schrijfonderwijs kent de kernzin ook, dus één keer is niets; de tell is de mechanische toepassing op elke alinea. Laat een alinea ook eens openen met een geval, een getal of een citaat, en het punt als tweede komen.

Signalen: `elke alinea opent met een samenvattende stelling` · `eerste zin vat de alinea samen` · `kernzin gevolgd door de uitwerking`

Voor: Caching verlaagt de latency. Toen we het token gingen cachen, zakte de p95 van 800 naar 120 milliseconden.

Na: Toen we het token gingen cachen, zakte de p95 van 800 naar 120 milliseconden.

Niet markeren: Nieuws, documentatie en samenvattingen zetten de kern vooraan omdat de lezer afhaakt; dat is een genre-eis. Ook een adviesnota begint met de aanbeveling. Het signaal is de kernzin in verhalend of betogend proza, in elke alinea, zonder uitzondering.

### Gelijke alinealengte `uniform-paragraph-length`

Ernst: **cluster** · Herkomst: transfer · en: `uniform-paragraph-length`

Elke alinea is ongeveer even lang, meestal drie tot vijf zinnen, zodat het stuk op alineaniveau geen ritme heeft. Een menselijke tekst laat een alinea van één zin vallen als het punt kort is, en loopt uit als de gedachte langer duurt. Poort voor detectie: elke alinea binnen één zin van het gemiddelde, gemiddelde minstens drie zinnen, over minstens vier alinea's.

Signalen: `elke alinea drie tot vijf zinnen` · `alle alinea's binnen een zin van het gemiddelde` · `gemiddelde minstens drie zinnen over minstens vier alinea's` · `geen enkele alinea van één regel`

Voor: (vier alinea's van elk precies vier zinnen)

Na: (een alinea van één zin, daarna een van zeven)

Niet markeren: Nieuwsberichten, persberichten en encyclopedische lemma's hebben van huis uit korte, gelijkmatige alinea's; die vorm komt van de huisstijl. Vertaalde en geredigeerde tekst wordt ook gladder. Meet alleen op lopend proza van één auteur, en niet op een tekst korter dan vier alinea's.

### Opgepompte genummerde lijst `numbered-list-inflation`

Ernst: **context** · Herkomst: transfer · en: `numbered-list-inflation`

Een kop noemt een getal ('Vijf dingen die je moet weten', 'Dit zijn de zeven redenen') en de lijst is daarna opgevuld tot dat getal klopt. Items overlappen of herhalen elkaar in andere woorden, omdat het aantal eerder vaststond dan de inhoud. Snijd terug naar de punten die er echt zijn.

Signalen: `Drie belangrijke inzichten` · `Vijf dingen die je moet weten` · `De 7 belangrijkste redenen` · `Hier zijn de vijf` · `Dit zijn de drie lessen` · `belangrijkste takeaways`

Voor: Dit zijn de zeven redenen om over te stappen: 1. Snellere builds. 2. Licentie per gebruiker. 3. Snellere builds op CI. 4. Goedkoper. 5. Betere documentatie. 6. Sneller incrementeel bouwen. 7. Lagere kosten per plek.

Na: We stapten over omdat de build 40 procent sneller is en de licentie per gebruiker gaat in plaats van per core.

Niet markeren: Een echte listicle, een checklist, een stappenplan en een top-10 hebben het getal in de kop omdat de lezer erop zoekt. Een lijst met zeven zelfstandige, niet overlappende punten is geen opgepompte lijst. Het signaal is de overlap tussen de items, niet het getal.

### Verwisselbare alinea's `paragraph-reshuffle-immunity`

Ernst: **context** · Herkomst: transfer · en: `paragraph-reshuffle-immunity`

De middenalinea's kunnen van plek wisselen zonder dat de lezer het merkt. Elke alinea is een zelfstandige module zonder dragend verband met zijn buren, zodat het stuk een lijst punten is en geen betoog dat opbouwt. Leg een lijn waarin elke alinea op de vorige steunt, of maak er een expliciete lijst van als de alinea's echt zelfstandig zijn.

Signalen: `alinea's kunnen van plek wisselen zonder dat de lezer het merkt` · `geen verbindende zin tussen alinea's` · `elke alinea een zelfstandige module`

Voor: Alinea over kosten. Alinea over snelheid. Alinea over vertrouwen. (elke volgorde leest hetzelfde)

Na: We keken vanwege de kosten en vonden snelheid. Die winst houdt alleen stand als de cache te vertrouwen is, en daar gaat de volgende alinea over.

Niet markeren: Naslagwerk, een FAQ, een productoverzicht en een lemma bestaan met opzet uit losse blokken die je in elke volgorde kunt lezen. Ook een verzameling korte portretten of een linkdump hoeft geen lijn te hebben. De test geldt voor betogend en verhalend proza.

### Titelkop boven de tekst herhaald `title-heading-duplicate`

Ernst: **context** · Herkomst: transfer · en: `title-heading-duplicate`

De tekst opent met een kop van niveau 1, vaak vet of als link, die de titel van het document herhaalt. Het model neemt niet aan dat het vlak de titel al toont. Op een wiki, in een CMS, in een issue of in een pull-requestbeschrijving levert dat een dubbele titel op.

Signalen: `eerste regel is een H1 die de paginatitel herhaalt` · `# <artikelnaam> als eerste regel` · `kop van niveau 1 gelijk aan de paginanaam` · `vetgedrukte titel boven de eerste alinea`

Voor: # devmeetup.nl

devmeetup.nl is een stack-agnostische meetup in Twente.

Na: devmeetup.nl is een stack-agnostische meetup in Twente.

Niet markeren: In een los markdownbestand, een README of een e-mail rendert niets de titel, dus daar hoort de H1 gewoon. Ook een export naar pdf of een print-versie heeft de titel in de tekst nodig. Alleen op vlakken die de titel zelf al tonen is het een dubbeling.

### Standaardvormen in poëzie `verse-form-defaults`

Ernst: **context** · Herkomst: transfer · en: `verse-form-defaults`

Gegenereerde poëzie valt in de standaardinstellingen van het model, wat de opdracht ook was: eindrijm waar niemand erom vroeg, strofen van vier regels, en oppervlakkige trouw aan een vorm. Een sonnet haalt veertien regels, een sestine negenendertig, maar de interne regel klopt niet. In het Nederlands neigt de default bovendien naar rijmparen op -aar en -en, wat het geheel nog voorspelbaarder maakt.

Signalen: `sonnet` · `villanelle` · `sestine` · `kwatrijn` · `rijm zonder dat erom gevraagd is` · `vier regels per strofe` · `jambisch` · `rijmparen op -aar en -en`

Voor: Een 'sestine' van 39 regels waarvan de zes eindwoorden nooit rouleren, in rijmende jamben.

Na: Laat de zes eindwoorden door alle strofen en de envoi rouleren, of noem het geen sestine.

Niet markeren: Als om een vaste vorm gevraagd is, is die vorm de opdracht en geen signaal. Kinderversjes, liedteksten, sinterklaasgedichten en gelegenheidsrijm horen te rijmen. Ook een dichter met een eigen vaste vorm valt erbuiten. Het signaal is de vorm die niemand vroeg, of de vormnaam zonder de regel die erbij hoort.

### Muur van tekst als reactie `wall-of-text-replies`

Ernst: **context** · Herkomst: transfer · en: `wall-of-text-replies`

In gespreksregisters, zoals reacties op een issue of pull request, chat en losse mail, komt het antwoord als één ononderbroken blok van vier of meer zinnen. Vaak is het ook langer dan gevraagd en mist het toch de kern, of sluit het niet precies aan op de vraag. Mensen breken een reactie op de gedachtegrens en beantwoorden drie vragen in drie stukjes.

Signalen: `vier of meer zinnen in een blok in een reactie onder 150 woorden` · `PR-reactie als één alinea` · `drie losse vragen beantwoord in één blok` · `overbodig lange, uitgebreide antwoorden` · `lang, maar toch de kern mist`

Voor: (een blok van 140 woorden dat drie losse reviewvragen beantwoordt)

Na: (drie korte alinea's, één per vraag)

Niet markeren: Een formele brief, een klachtafhandeling en een juridisch antwoord horen in doorlopende alinea's. Sommige mensen schrijven nu eenmaal in blokken, dus één lange reactie zegt niets: kijk naar het patroon over meer berichten van dezelfde persoon. Een uitgebreid antwoord op een uitgebreide vraag is ook geen tell.

## Interpunctie en opmaak

### Gedachtestreepje als standaardsplitsing `em-dash-density`

Ernst: **always** · Herkomst: nl-bron · en: `em-dash-density`

Het lange streepje wordt de vaste manier om een zin te splitsen: een enkel streepje dat een pointe aanplakt, een gepaarde tussenzin, of een streepje waar een komma of een punt hoort. In het Nederlands weegt dit zwaarder dan in het Engels, want de Nederlandse typografie zet een half kastlijntje met spaties eromheen en de kastlijn zonder spaties is een Engelse gewoonte. De ASCII-vorm met twee koppeltekens hoort er ook bij. Vervang door een punt, een komma of een voegwoord, en gebruik in feitregels de huisseparator // of het middelpunt. De Amerikaanse zetting hoort bij het patroon: het lange streepje zonder spaties tegen de woorden aan, waar het Nederlands een gespatieerd half streepje, een komma, haakjes of een dubbele punt zet.

Signalen: `—maar` · `— en dat is` · `— niet omdat` · `em-dash` · `het eenzame gedachtestreepje` · `lang koppelteken` · `streepje voor een slotpointe` · `gepaarde tussenzin tussen twee streepjes` · `streepje waar een komma of punt hoort` · `meerdere streepjes per alinea` · `**Vet** — zin` · `woord—woord` · `zin—en dan` · `lang streepje zonder spaties eromheen` · `– en dat is precies het punt.` · `streepje zonder tweede streepje` · `streepje in de laatste vier woorden van de zin` · `één accentstreepje per alinea`

Voor: De meetup groeit—en dat betekent een nieuwe zaal.

Na: De meetup groeit. Daarom zoeken we een grotere zaal.

Niet markeren: Het halve kastlijntje met spaties eromheen (–) is gewoon Nederlands en telt niet mee. Ook niet markeren: koppeltekens in samenstellingen en getalbereiken, citaten uit een Engelse bron, code en commandoregels, en beeldmateriaal dat al is vastgesteld, zoals een vastgesteld huismiddel dat het streepje in datavorm draagt. Eén streepje in een lange tekst is geen patroon. Het gespatieerde half streepje is gewoon Nederlands, en een streepjespaar rond een echte tussenzin telt niet mee. Geen tell in geciteerd Engels, in overgenomen uitgeverstypografie, in getalsbereiken en bij schrijvers die het streepje aantoonbaar al voor 2023 zo gebruikten. Eén los accentstreepje is een normaal stijlmiddel; het patroon zit in de herhaling.

### Overgeslagen kopniveaus `heading-level-skipping`

Ernst: **always** · Herkomst: transfer · en: `heading-level-skipping`

Secties beginnen op het derde kopniveau zonder kop van het tweede niveau erboven, of een kop staat meer dan één stap onder zijn ouder. Dat druist in tegen toegankelijkheidsconventies op elk vlak, dus een met de hand opgemaakte pagina heeft die eigenaardigheid bijna nooit. Nummer de hiërarchie zo dat elk niveau één stap dieper is dan zijn ouder.

Signalen: `### als eerste kop zonder ## erboven` · `kopniveau springt twee stappen` · `=== zonder ==`

Voor: ### Achtergrond
Het project startte in 2024.
### Methode
We spraken twaalf teams.

Na: ## Achtergrond
Het project startte in 2024.
## Methode
We spraken twaalf teams.

Niet markeren: Een fragment dat uit een groter document is geknipt mist zijn ouderkop terecht, en een template of partial begint vaak bewust op een dieper niveau. Ook niet markeren in code, in wikitext waar de sjabloon de kop levert, en in een README waar de titel uit de metadata komt.

### Punt achter het bulletlabel `list-label-periods`

Ernst: **always** · Herkomst: transfer · en: `list-label-periods`

In een lijst waarvan de items met een kort label openen, eindigt dat label met een punt en loopt de toelichting als losse zin door, waar iemand een dubbele punt zou zetten. Met vet label is het signaal het sterkst, zonder vet blijft het zichtbaar. Maak er een dubbele punt van en ga klein verder, of schrijf een gewone zin.

Signalen: `- **Introducties.** Jaren aan conferenties` · `- **Bereik.** Ons netwerk` · `- **Contentdistributie.**` · `label met punt in plaats van dubbele punt`

Voor: - **Introducties.** Jaren aan conferenties en een netwerk van operators.

Na: - **Introducties:** jaren aan conferenties en een netwerk van operators.

Niet markeren: Een label dat zelf een volledige zin is, hoort met een punt te eindigen, en in een echte definitielijst of een changelog is de punt de huisstijl. Ook niet markeren: een afkorting met punt aan het eind van het label, en lijsten waarin elk item uit losse zinnen bestaat zonder labelvorm.

### Regieaanwijzing tussen haakjes in dialoog `parenthetical-stage-directions`

Ernst: **always** · Herkomst: transfer · en: `parenthetical-stage-directions`

Dialoog met een emotie tussen haakjes voor de regel, als in een scenario, in proza dat geen scenario is. Het is een toneelconventie die in verhalend Nederlands het werk van de zin overneemt. Leg de emotie in de woorden zelf of in een handeling.

Signalen: `(geïrriteerd)` · `(zuchtend)` · `(lachend)` · `(aarzelend)` · `Bob: (verdedigend) Waarom zou ik?`

Voor: Bob: (verdedigend) Waarom zou ik?
Tonny: (geïrriteerd) Luister nou.

Na: Bob sloeg zijn armen over elkaar. "Waarom zou ik?" Tonny wreef in zijn ogen. "Luister nou."

Niet markeren: In een scenario, een toneeltekst, een hoorspel, een podcastscript of een interviewtranscriptie is dit de juiste vorm. Ook niet markeren in ondertitelbestanden en in notulen die een reactie noteren.

### Wiskundig vet en bulletglyphs `unicode-math-bold-and-bullets`

Ernst: **always** · Herkomst: transfer · en: `unicode-math-bold-and-bullets`

Vet nagemaakt met Unicode-wiskundetekens in plaats van met opmaak, en lijstitems gemarkeerd met het losse bulletteken op een vlak dat echte lijstsyntaxis heeft. Het komt uit sociale platforms zonder opmaakknop en blijft daarna hangen. Gebruik de opmaak van het vlak zelf.

Signalen: `unicode-vet in plaats van opmaak` · `• als bullet op een vlak met echte lijstsyntaxis`

Voor: 𝐕𝐢𝐞𝐦𝐬
• kleinere batches
• minder rollbacks

Na: Lever wekelijks. Kleinere batches leiden tot minder rollbacks.

Niet markeren: In wiskundige tekst zijn de blackboard- en fraktuurtekens echte notatie, en op LinkedIn, Instagram en in een plain-text mail is het bulletteken de enige beschikbare vorm. Ook niet markeren in ASCII-art, in een terminalbanner en in gegenereerde tabeluitvoer van een tool.

### Vet als standaardnadruk `bold-overuse`

Ernst: **cluster** · Herkomst: nl-bron · en: `bold-overuse`

Vet wordt mechanisch uitgedeeld in plaats van als accent gezet: losse kernwoorden midden in een alinea, een vette frase in elke zin, elk voorkomen van hetzelfde woord, of een vet label vooraan elke bullet. Ook vet op een cijfer of jaartal, en vet dat de plek van een kop inneemt, horen erbij. Haal het vet bij de meeste frases weg en bouw de zin zo dat het belangrijke vooraan staat.

Signalen: `vetgedrukte kernwoorden midden in een alinea` · `elke bullet begint met een vet label` · `vet in plaats van een kop` · `meerdere vette frasen per alinea` · `vet op een cijfer of jaartal` · `meer dan drie vette stukken in een tekst` · `vet op elk voorkomen van hetzelfde woord`

Voor: **Belangrijk:** de meetup is **gratis** en vindt plaats in **Enschede**.

Na: De meetup is gratis en vindt plaats in Enschede.

Niet markeren: Eén vette frase per hoofdsectie is normaal, en een vet label in een echte definitielijst of een woordenlijst hoort daar. Niet markeren in tabelkoppen, in een leesbaar samengevatte checklist waar het vet de sleutel is, of in wikitext waar drie apostrofs de opmaaksyntaxis zijn. Nieuwe modellen zijn hierop bijgestuurd, dus de afwezigheid van vet zegt niets.

### Hoofdletter na de dubbele punt `capitalized-after-colon`

Ernst: **cluster** · Herkomst: translationese · en: `capitalized-after-colon`

Na een dubbele punt volgt een hoofdletter terwijl er geen volledige aangehaalde zin of reeks zinnen komt. Het Nederlands schrijft daar een kleine letter. De vorm komt mee met de Engelse zetconventie en staat vaak in tussenkoppen met een dubbele punt. Het Nederlands schrijft na een dubbele punt klein, behalve bij een citaat, een eigennaam of meer dan één volledige zin, dus de hoofdletter komt uit de Engelse conventie.

Signalen: `: Dit` · `: Het` · `: Een` · `: Ja` · `: Begin` · `tussenkop met dubbele punt gevolgd door hoofdletter` · `Er blijven twee opties over: We leveren nu` · `Het antwoord is simpel: Je moet kiezen` · `hoofdletter na dubbele punt zonder eigennaam of citaat`

Voor: Het antwoord is simpel: Begin met je punt.

Na: Het antwoord is simpel: begin met je punt.

Niet markeren: Wel een hoofdletter bij een volledige aangehaalde zin, bij meerdere zinnen achter elkaar en bij een eigennaam. In lijsten met een dubbele punt als label is de hoofdletter een opmaakkeuze. Geen regex, want de scanner draait hoofdletterongevoelig. Correct zijn de hoofdletter voor een citaat, voor een eigennaam, voor een titel en voor twee of meer volledige zinnen na de dubbele punt. Ook niet markeren in koppen, in tabelcellen, in code en in bibliografische verwijzingen. Er staat hier geen regex: de scanner draait hoofdletterongevoelig, dus dit patroon vraagt een leesbeurt.

### Kommadichtheid `comma-density`

Ernst: **cluster** · Herkomst: transfer · en: `comma-density`

Kommaoverschot op documentniveau: het aandeel zinnen met minstens één komma ligt ver boven wat mensen schrijven, en er staat een komma op elke syntactische grens. Vaak samen met een komma tussen onderwerp en persoonsvorm, en met ingelaste bijstellingen die de zin uit elkaar trekken. Splits zinnen, absorbeer de komma in een voegwoord, of schrap hem.

Signalen: `meer dan de helft van de zinnen bevat een komma` · `komma op elke syntactische grens` · `komma tussen onderwerp en persoonsvorm` · `drie of meer komma’s in een zin van gemiddelde lengte`

Voor: Het team, dat snel gegroeid was, kwam maandag bijeen, nam het plan door, en besloot, in beginsel, door te gaan.

Na: Het team was snel gegroeid. Maandag nam het het plan door en besloot voorlopig door te gaan.

Niet markeren: Dit is een maat over een hele tekst, geen oordeel over één zin. Juridisch, wetenschappelijk en ambtelijk Nederlands zetten van nature meer komma’s, en een lange opsomming of een reeks bijzinnen is gewoon correct. De seriekomma zit apart onder oxford-comma-nl; markeer die hier niet nog een keer.

### Krulaanhalingstekens op een recht-aanhalingsvlak `curly-quotes`

Ernst: **cluster** · Herkomst: nl-bron · en: `curly-quotes`

Typografische aanhalingstekens op een vlak waarvan de conventie recht is: code, commitberichten, Markdown, mail, chat. Het sterkere signaal is de menging, krullend en recht door elkaar in één tekst of zelfs één zin, want krullende software is consequent en een plakje uit een chatvenster niet. In het Nederlands komt erbij dat de Engelse paren worden uitgestoten terwijl de Nederlandse conventie „…” of ‘…’ is.

Signalen: `slimme aanhalingstekens` · `curly quotes` · `rechte aanhalingstekens` · `krullend en recht door elkaar in één tekst` · `Engels krulpaar in Nederlandse tekst`

Voor: Hij zei “het project ligt op schema”, maar zijn collega zei "dat halen we niet".

Na: Hij zei "het project ligt op schema", maar zijn collega zei "dat halen we niet".

Niet markeren: In gezette tekst, in Word, in een tijdschrift of op een site met een typografische pipeline zijn krullende tekens de norm en zegt dit niets. De krulapostrof in ’t, ’n en z’n is gewoon Nederlands en wordt nooit gemeld. Een losse krulapostrof of een enkel krulpaar is geen patroon.

### Emoji als versiering `emoji-decoration`

Ernst: **cluster** · Herkomst: nl-bron · en: `emoji-decoration`

Emoji staan stelselmatig voor een kop, voor een vet label of als opsommingsteken, uit een kleine vaste favorietenset. Het signaal is de systematiek en de plek: precies één emoji per kop of lijstitem, of een post die met een emoji opent en na de eerste zin met een emoji afsluit. Ook een losse sprankel aan het eind van een alinea in een rapport of README hoort erbij. Haal ze uit koppen en lopende tekst.

Signalen: `emoji direct voor een kop` · `emoji als opsommingsteken` · `vaste emoji per sectie` · `🚀 **Lanceerfase:**` · `✅ voor elk lijstitem` · `✨ aan het eind van een alinea`

Voor: 🚀 Wat je kunt verwachten
✅ Twee talks
✅ Borrel

Na: Programma: twee talks van twintig minuten, daarna borrel.

Niet markeren: Op sociale media, in chat en in issue-reacties is een emoji gewoon taal en zegt hij niets. Ook niet markeren: emoji in een statusregel die het team zelf heeft afgesproken, in een changelog-conventie, in commitprefixen, of in een citaat. Een enkele emoji aan het eind van een socialpost is geen patroon.

### Hashtagstapel onder de post `hashtag-stuffing`

Ernst: **cluster** · Herkomst: translationese · en: `hashtag-stuffing`

Een staartblok van zes of meer hashtags onder een korte post, meestal een specifieke tag plus brede categorietags. De Nederlandse variant schrijft elke tag met een hoofdletter aan het begin van elk woord. Breng het terug tot twee of drie tags die een lezer echt naar verwant werk brengen. Onder een Nederlandse post staat de rij vaak in het Engels of in CamelCase, met vertaalde marketingtermen erin.

Signalen: `#AI #innovatie #technologie #toekomst` · `#digitalisering` · `#ondernemen #groei` · `#Elk #Woord #Hoofdletter` · `zes of meer hashtags onder een korte post` · `#ElkWoordEenHoofdletter` · `#AIInnovatie` · `#DigitalTransformation` · `#FutureOfWork` · `rij van vijf of meer hashtags onder een Nederlandse post`

Voor: #AI #Innovatie #Technologie #Toekomst #Digitalisering #Ondernemen

Na: #devmeetup #meetup

Niet markeren: Een lanceerpost, een vacature of een evenementpost met veel tags is normaal marketinggedrag, en op Instagram en TikTok is een lange tagrij de conventie. Ook niet markeren: hoofdletters in een tag die een eigennaam of een acroniem is (#TwenteDev, #AI). Buiten sociale media geldt dit patroon niet. Vakhashtags die nu eenmaal Engels zijn (#kubernetes, #devops) zijn geen signaal, en twee of drie hashtags is op LinkedIn normaal. In een Engelstalige post hoort de hele rij thuis.

### Onberispelijke typografie in een ruw register `immaculate-typography`

Ernst: **cluster** · Herkomst: transfer · en: `immaculate-typography`

Perfecte spatiering, interpunctie en spelling op plekken waar mensen snel typen: issue- en PR-reacties, chat, DM’s, korte mailtjes. De stapel is de handtekening: krulaanhalingstekens plus een gedachtestreepje plus machinale netheid over tachtig woorden of meer, zonder d/t-twijfel, zonder samentrekking als z’n of ’t, zonder los zinsdeel. Omgekeerd geldt bij het redigeren van andermans losse tekst dat de typefouten en eigenaardigheden blijven staan.

Signalen: `geen d/t-fouten` · `geen typefouten` · `geen dubbele spaties` · `geen samentrekkingen (z'n, 't, 'n)` · `volledige woorden waar mensen afkorten`

Voor: Ik waardeer de grondige analyse en de snelle reactie. Het voorstel is doordacht en ik steun het van harte.

Na: thanks voor het uitzoekwerk, lijkt me prima zo. ben voor

Niet markeren: Mensen die netjes schrijven bestaan, en in een formeel register (een rapport, een offerte, een brief aan de gemeente) is verzorgde typografie de eis. Ook niet markeren: tekst die door een spellingchecker of een redacteur is gegaan, en niet-moedertaalsprekers die bewust volledige vormen schrijven. Alleen de hele stapel in een informeel register telt.

### Seriekomma voor 'en' of 'of' `oxford-comma-nl`

Ernst: **cluster** · Herkomst: nl-bron

Een komma voor het laatste lid van een opsomming van drie of meer: appels, peren, en bananen. Die komma is standaard in het Britse Engels en ongebruikelijk in het Nederlands, dus in een Nederlandse opsomming is hij een vertaalspoor. Fout is hij niet, maar bij herhaling in dezelfde tekst is het een tell. In een uit het Engels overgezette tekst lekt de serial comma systematisch mee, en dan is de regelmaat de tell, niet de losse komma.

Signalen: `, of` · `Oxford-komma` · `seriekomma` · `serial comma` · `appels, peren, en bananen` · `schrijven, lezen, en films kijken` · `snel, eenvoudig, en efficiënt` · `A, B, en C` · `komma voor 'en' in een opsomming` · `e-mailmarketing, social media, en SEO`

Voor: Ik kocht appels, peren, en bananen.

Na: Ik kocht appels, peren en bananen.

Niet markeren: Een komma voor 'en' tussen twee hoofdzinnen met verschillende onderwerpen is in het Nederlands juist wel correct, net als een komma die een bijzin afsluit voor het voegwoord. Niet markeren in juridische of technische opsommingen waar de komma dubbelzinnigheid wegneemt, in citaten, of bij één losse instantie. Geen tell wanneer de komma twee volledige hoofdzinnen scheidt ('Hij belde, en zij nam op'), wanneer vlak voor 'en' een tussenzin of bijzin afsluit ('Ze pakte de tas die er stond, en vertrok'), of wanneer de komma een dubbelzinnige nevenschikking uit elkaar houdt. In een citaat of een overgenomen Engelse zin telt hij niet.

### Verklarende haakjes op een rij `parenthetical-gloss-overload`

Ernst: **cluster** · Herkomst: transfer · en: `parenthetical-gloss-overload`

Verklarende haakjes van de vorm (dit betekent dat …) die claim na claim worden aangeplakt. De tell is de formule, niet het haakje: gegenereerd proza gebruikt juist minder terzijdes tussen haakjes dan menselijk proza. Zet de uitleg in de lopende tekst of laat hem weg.

Signalen: `(dit betekent dat …)` · `(wat betekent dat …)` · `(ofwel: …)` · `(met andere woorden: …)` · `(dat wil zeggen: …)`

Voor: De omzet groeide 40 procent (dit betekent dat de strategie werkt). Het verloop daalde (wat betekent dat klanten tevredener zijn).

Na: De omzet groeide 40 procent en het verloop daalde, wat erop wijst dat de strategie werkt.

Niet markeren: Eén verduidelijking bij een term die de lezer niet kent is gewoon goed schrijven, en in juridische en technische teksten is de formule "dat wil zeggen" staande taal. Terzijdes tussen haakjes zijn juist een menselijk teken en worden nooit weggeschreven. Alleen de opeenstapeling telt.

### Aanhalingstekens als distantie `scare-quotes`

Ernst: **cluster** · Herkomst: transfer · en: `scare-quotes`

Aanhalingstekens om gewone woorden voor nadruk of ironische afstand, en dan vijf of meer keer in één document. De woorden die er het vaakst tussen staan zijn reclamewoorden. Houd echte citaten en schrijf de rest als gewone tekst.

Signalen: `een "naadloze" ervaring` · `innovatieve" oplossingen` · `echte" resultaten` · `vijf of meer paar aanhalingstekens om gewone woorden`

Voor: Het "innovatieve" platform biedt "naadloze" onboarding voor "moderne" teams.

Na: Met het platform kan een nieuw team dezelfde dag beginnen.

Niet markeren: Een echt citaat, een term die als term wordt genoemd, een titel, een bijnaam en een omstreden woord dat de schrijver expliciet op afstand zet, zijn alle vier legitiem. Vakteksten die een begrip introduceren zetten het terecht één keer tussen aanhalingstekens. De poort is de telling, niet het losse paar.

### Scheve puntkomma-inzet `semicolon-colon-skew`

Ernst: **cluster** · Herkomst: transfer · en: `semicolon-colon-skew`

Het gebruik van de puntkomma wijkt af van menselijk proza, in een richting die van het model afhangt. Of het teken komt nergens voor en komma’s en streepjes doen het werk, of de puntkomma verbindt hoofdzinnen op een tempo dat ver boven gewoon Nederlands ligt en vervangt punt en voegwoord. Nederlands proza gebruikt de puntkomma zeldzamer dan Engels, dus drie in één alinea is hier al veel.

Signalen: `puntkomma als standaardsplitsing tussen hoofdzinnen` · `drie of meer puntkomma’s in één alinea` · `puntkomma komt nergens voor`

Voor: De build faalde; de logs waren leeg; niemand kreeg een melding; de piketregeling was verlopen.

Na: De build faalde en de logs waren leeg. Niemand kreeg een melding, want de piketregeling was verlopen.

Niet markeren: In code, CSS, CSV-achtige regels, bibliografieën en lange opsommingen met interne komma’s is de puntkomma functioneel. Wetenschappelijk en juridisch Nederlands gebruiken hem vaker en correct. De afwezigheid van puntkomma’s is op zichzelf niets om te melden.

### Klemtoonaccent en willekeurige nadruk `stress-accents-nl`

Ernst: **cluster** · Herkomst: nl-bron

Nadrukmarkering op woorden die geen nadruk dragen: klemtoonaccenten als té, wél en én, of cursief en kapitalen op willekeurige plekken. Het accent zelf is een gewoon Nederlands middel, het patroon is de toepassing te pas en te onpas. Zet alleen iets in de spotlight als de betekenis dat vraagt.

Signalen: `te pas én te onpas` · `HOOFDLETTERS voor nadruk` · `cursief op een willekeurig woord`

Voor: Het gebeurt te pas én te onpas, en dat is té veel.

Na: Het gebeurt te pas en te onpas, en dat is te vaak.

Niet markeren: Het klemtoonaccent is correct Nederlands waar het betekenisverschil draagt: 'één' tegenover 'een', 'vóór' tegenover 'voor', en een tegenstelling die anders verkeerd wordt gelezen. Niet markeren in citaten, in leermateriaal over spelling, of bij één losse instantie. Vet valt onder bold-overuse.

### Scheidingslijn voor elke sectie `thematic-breaks`

Ernst: **cluster** · Herkomst: transfer · en: `thematic-breaks`

Een horizontale lijn boven elke sectie of subsectie, standaard in Markdown-uitvoer. Eén lijn die een echte wending markeert is normaal, het patroon is er één voor elke kop. Haal ze weg en laat de koppen de structuur dragen.

Signalen: `----` · `<hr>` · `een streep boven elke kop`

Voor: De oudste woordenboeken kennen die betekenis niet.

---

## Geschiedenis

Hoofddoeken staan in de bronnen.

Na: De oudste woordenboeken kennen die betekenis niet.

## Geschiedenis

Hoofddoeken staan in de bronnen.

Niet markeren: YAML-frontmatter wordt door dezelfde drie streepjes begrensd, vandaar dat de regex een kop erna eist. Ook niet markeren: een enkele lijn die een echte wending markeert, een scheiding tussen brieffragmenten of dagboeknotities, en een huisstijl waarin de lijn onder een kop hoort.

### Typografische Unicode-vervangingen `unicode-typography-nl`

Ernst: **cluster** · Herkomst: nl-bron

Unicode-varianten van gewone leestekens waar een mens de toetsenbordvorm typt: het ellipsis-teken in plaats van drie punten, de harde spatie, het lange streepje in plaats van een koppelteken. Typografisch zijn ze correcter, en juist dat is het spoor: ze staan er allemaal, overal, zonder dat iemand ze heeft ingetypt. Zet ze terug naar de gewone vorm op vlakken die geen zetwerk doen.

Signalen: `ellipsis-karakter` · `non-breaking space` · `harde spatie` · `typografisch correcte tekens die niemand intypt`

Voor: De aanmelding loopt nog… en de zaal telt 60 plaatsen.

Na: De aanmelding loopt nog... en de zaal telt 60 plaatsen.

Niet markeren: In gezette tekst, in LaTeX-uitvoer, in een CMS met een typografiefilter en in PDF’s zijn deze tekens de bedoeling. De harde spatie hoort bij een getal met eenheid en in een naam die niet mag afbreken. Het gedachtestreepje zelf valt onder em-dash-density; meld het hier niet dubbel.

### H1 voor gewone secties `level-1-heading-overuse`

Ernst: **context** · Herkomst: transfer · en: `level-1-heading-overuse`

Koppen van niveau 1 voor gewone secties op een vlak dat niveau 1 voor de paginatitel reserveert, zoals een wiki, de meeste CMS’en en HTML met een gerenderde titel. Het komt van Markdown-koppen die één op één naar de doelopmaak zijn overgezet. Zet de secties een niveau lager.

Signalen: `meerdere # koppen in een document` · `= Geschiedenis =` · `# Geschiedenis` · `H1 waar de pagina zelf al een titel toont`

Voor: # Geschiedenis

# Programmering

# Externe links

Na: ## Geschiedenis

## Programmering

## Externe links

Niet markeren: Eén H1 als documenttitel is juist de bedoeling, en in een los Markdown-bestand zonder eigen titelweergave is een tweede H1 soms een bewuste paginascheiding. Ook niet markeren in slidedecks, in changelogs met een kop per versie, en in bestanden die een generator later herschrijft.

### Overbodige afkortingsuitleg `redundant-acronym-expansion`

Ernst: **context** · Herkomst: transfer · en: `redundant-acronym-expansion`

Elke afkorting wordt bij het eerste gebruik tussen haakjes uitgeschreven, ook als het publiek de term dagelijks gebruikt, vaak in de omgekeerde volgorde met de afkorting voorop en met de meervoudsapostrof erbij. Meestal staat het ook nog in vet, en dan voor elke term in dezelfde zin. Laat de uitleg weg waar de lezer de term kent.

Signalen: `KPI's (Key Performance Indicators)` · `OKR's (Objectives and Key Results)` · `AVG (Algemene verordening gegevensbescherming)` · `API (Application Programming Interface)` · `elke afkorting uitgeschreven bij eerste gebruik`

Voor: Het combineert KPI's (Key Performance Indicators) met het Business Model Canvas (BMC).

Na: Het combineert KPI's met het Business Model Canvas.

Niet markeren: Bij een publiek dat de term niet kent is uitschrijven precies goed, en in wetenschappelijke, juridische en overheidsteksten schrijft de stijlgids het voor bij eerste gebruik. Ook niet markeren in een begrippenlijst, in een norm of in een tekst voor buitenstaanders. Eén uitleg per document is geen patroon.

### Pijlen als voegwoord `unicode-arrows`

Ernst: **context** · Herkomst: transfer · en: `unicode-arrows`

Typografische pijlen of hun ASCII-vormen midden in lopende tekst, waar een schrijver "leidt tot" of "dus" zou zeggen of gewoon een zin zou maken. Vaak als kettinkje: invoer, verwerking, uitvoer. Schrijf de relatie uit.

Signalen: `Invoer → Verwerking → Uitvoer` · `betere resultaten → meer betrokkenheid`

Voor: Dat leidt tot betere resultaten → dus tot meer betrokkenheid.

Na: Betere resultaten zorgen ervoor dat meer mensen meedoen.

Niet markeren: In code, in commitberichten, in diagrammen, in wiskunde en in taalkundige afleidingen (Latijn → Frans) is de pijl vaknotatie. Ook niet markeren in een migratieregel, in een routebeschrijving en in een menupad zoals Instellingen → Profiel.

### Overbodige kleine tabellen `unnecessary-tables`

Ernst: **context** · Herkomst: transfer · en: `unnecessary-tables`

Een tabel van een paar rijen met feiten die als zin beter lezen: twee kolommen Metriek en Waarde, of Naam en Functie, vaak met een bijschrift als Kerncijfers. De mismatch tussen de tabelvorm en de kleine, prozavormige inhoud is de tell. Vouw de feiten in de tekst.

Signalen: `| Metriek | Waarde |` · `| Kenmerk | A | B |` · `| Naam | Functie |` · `Kerncijfers` · `Vergelijking van X en Y`

Voor: | Metriek | Waarde |
| --- | --- |
| Marktwaarde (2024) | circa 2,1 miljard euro |
| Aantal locaties | 4 |

Na: De markt was in 2024 ongeveer 2,1 miljard euro waard, verdeeld over vier locaties.

Niet markeren: Een tabel met meer dan een handvol rijen, met echte kolomvergelijking of met getallen die de lezer naast elkaar wil leggen, verdient zijn vorm. Ook niet markeren: infoboxen, API-parameterlijsten, prijstabellen en roosters. Documentatieconventies die alles in tabellen zetten zijn een huisstijl.

## Inhoud en bewijs

### Zelfverzekerde onjuistheden en anachronismen `confident-fabrication-nl`

Ernst: **always** · Herkomst: nl-bron

Aannemelijk klinkende beweringen die niet kloppen, compleet met redenering en voorbeelden, en zonder enig voorbehoud gebracht. De verwante kleine vorm is het losse rare detail: een jaartal, een techniek of een gebruik dat niet in de tijd past en dat niemand met kennis van het onderwerp zou opschrijven. Waar het model geen antwoord had, gaat het verzinnen, en de zekerheid in de zin is precies even groot als bij het deel dat wel klopt. Het middel is feitcontrole per bewering, niet een hedge erbij.

Signalen: `klinkt aannemelijk maar klopt niet` · `anachronisme: techniek of gebruik dat niet in de tijd past` · `verzonnen jaartal of aantal zonder voorbehoud` · `dezelfde stelligheid bij het onjuiste als bij het juiste deel`

Voor: De textielfabriek schakelde in 1832 over op elektrische weefgetouwen, wat de productie verdrievoudigde.

Na: De fabriek nam in 1832 een stoommachine in gebruik. Elektrische aandrijving kwam er pas na 1900.

Niet markeren: Geen tekstueel patroon en dus geen regex: dit vind je alleen door de bewering na te lopen. Niet markeren bij een omstreden feit waar de tekst de onenigheid netjes weergeeft, en niet bij een fout in een citaat dat correct wordt weergegeven.

### Verzonnen auteursregels en plaatsdatums `fabricated-bylines-and-datelines`

Ernst: **always** · Herkomst: transfer · en: `fabricated-bylines-and-datelines`

Publicatiemetadata die met niemand en nergens overeenkomt: auteursbio's en portretten van verslaggevers die niet bestaan, en datum- of plaatsregels die de beschreven gebeurtenissen tegenspreken. Anders dan de prozatells is dit verzonnen herkomst die aan het stuk hangt, en die valt te controleren tegen redactieoverzichten, beeldbanken en het verloop van de gebeurtenis. In Nederlandstalige media is de auteursbio de gangbaarste vorm; de plaatsdatum komt vooral in vertaalde persbureaukopij voor.

Signalen: `auteursbio zonder vindbare persoon` · `portret uit een beeldbank met gegenereerde gezichten` · `plaatsdatum die niet klopt met de gebeurtenis` · `auteursregel bij een redactie waar niemand van die naam werkt`

Voor: Door Sanne de Vries. Sanne schrijft al jaren over technologie en woont met haar hond op het platteland.

Na: Auteursregel verwijderd: er werkt niemand met die naam bij de redactie en het portret komt uit een beeldbank met gegenereerde gezichten.

Niet markeren: Geen regex: de vorm van een auteursregel is niet van een gewone zin te onderscheiden zonder hoofdlettergevoeligheid, dus dit wordt met de hand gecontroleerd. Niet markeren bij pseudoniemen die als zodanig bekend zijn en bij redactionele verzamelnamen (Van onze verslaggever).

### Verzonnen eigen ervaring `fake-first-person`

Ernst: **always** · Herkomst: transfer · en: `fake-first-person`

Beweringen in de eerste persoon waar niemand achter stond: ik heb dit al honderd keer gezien, in mijn ervaring, uit eigen ervaring weet ik, of een lyrische ik zonder lichaam, plaats of geschiedenis. Bij herschrijven is elke toegevoegde ik een fout, want de herkomst is juist de vraag en geen enkele frase kan die aantonen. Staat er in de bron geen eerste persoon, dan staat die ook niet in de herschrijving.

Signalen: `ik heb dit al honderd keer gezien` · `in mijn ervaring` · `ik geef toe` · `uit eigen ervaring weet ik` · `ik heb het vaak zien gebeuren` · `wij zagen dit bij tientallen klanten` · `in de praktijk merk ik`

Voor: Ik heb dit al honderd keer gezien: teams leveren de migratie op en slaan de rollback over.

Na: Teams leveren de migratie vaak op zonder rollback.

Niet markeren: Niet markeren als de schrijver de ervaring echt heeft en dat na te gaan is, en niet in een citaat, een interview of een ondertekende column. Het patroon is de eerste persoon die tijdens het genereren of herschrijven is ontstaan.

### Verzonnen of oncontroleerbare bronvermelding `hallucinated-citations`

Ernst: **always** · Herkomst: nl-bron · en: `hallucinated-citations`

Een bronvermelding die compleet oogt en de claim niet kan dragen: het werk bestaat niet, de DOI lost niet op of wijst naar iets anders, het ISBN haalt zijn controlecijfer niet, de URL geeft 404 zonder archiefkopie, of de bron bestaat wel en zegt niets over de bewering. Nederlandse extra vormen zijn verzonnen ECLI-nummers, verzonnen wetsartikelen en een link naar een zoekopdracht in plaats van naar het document. De controle gaat in twee stappen: bestaat de bron, en staat de bewering erin. Één verkeerd jaartal is een vergissing, meerdere foute vermeldingen zijn een werkwijze.

Signalen: `DOI die niet oplost` · `ISBN met verkeerd controlecijfer` · `404 zonder archiefkopie` · `auteur en titel die samen niet bestaan` · `keurige opmaak met verzonnen paginanummers` · `bron bestaat wel maar zegt niets over de bewering` · `een link naar een zoekopdracht in plaats van naar het document` · `verwijzing naar een rapport zonder uitgever of jaartal` · `een verzonnen ECLI:NL:HR:2019:1234` · `artikel 12 van de AVG (bestaat, maar zegt iets anders)`

Voor: M. E. Jansen, De grenzen van de wet van Ohm, Tijdschrift voor Elektrotechniek, jrg. 62, nr. 6, 1974. doi:10.1109/PROC.1974.9547

Na: Verwijzing verwijderd: de DOI wijst naar een ander artikel en het stuk staat niet in die jaargang.

Niet markeren: De regex markeert kandidaten om na te lopen, geen fouten: een echte DOI, een echt ECLI-nummer en een correct AVG-artikel raken hem net zo goed. Niet markeren in bibliografieën en juridische stukken zonder de verwijzing eerst te controleren, en tel een archiefkopie (web.archive.org) als geldig.

### Eigen duiding toegeschreven aan een bron `misattributed-source-analysis`

Ernst: **always** · Herkomst: transfer · en: `misattributed-source-analysis`

Een model met bronnen erbij plakt zijn eigen interpretatie aan een echte, met naam genoemde bron, of die bron dat nu zegt of niet: hij benadrukt daarmee het blijvende belang van, dit citaat toont aan hoe relevant het werk nog is. De verwijzing klopt, de bewering erover is gegenereerd. Alleen de bron zelf lezen wijst dit aan; laat de bron zeggen wat hij zegt en zet je eigen oordeel in je eigen zin.

Signalen: `benadrukt daarmee` · `onderstreept hiermee` · `dit citaat toont aan` · `wijst op het blijvende belang` · `waarmee hij zijn invloed aantoont` · `hij laat hiermee zien dat`

Voor: Van Dijk vergelijkt de twee woordenboeken en benadrukt daarmee hun kritische blik op afkortingen. Dit citaat toont aan hoe relevant het werk nog altijd is.

Na: Van Dijk (2019, p. 44) vergelijkt hoe beide woordenboeken met afkortingen omgaan.

Niet markeren: Niet markeren als de duiding letterlijk in de bron staat en dat te controleren is, en niet in een recensie of een essay waarin de schrijver openlijk zelf interpreteert en dat ook zo formuleert.

### Speculatie als feit gepresenteerd `speculative-gap-fill`

Ernst: **always** · Herkomst: nl-bron · en: `speculative-gap-fill`

Waar het model niets vond, stelt de tekst eerst vast dat er weinig bekend is en vult het gat daarna met omzichtige verzinsels: waarschijnlijk, vermoedelijk, naar alle waarschijnlijkheid, lijkt te hebben. Een veelvoorkomende subvorm schrijft een levend persoon bewuste terughoudendheid toe (houdt zich bewust op de achtergrond) terwijl de werkelijkheid is dat er geen gegevens zijn. Een tweede subvorm hedget over de eigen bronnen (op basis van de beschikbare informatie, in de gevonden zoekresultaten) en gaat daarna toch door. Zowel de bewering over de leegte als de invulling moeten weg; de mededeling over de trainingsgrens zelf staat in de categorie artifacts.

Signalen: `er is weinig bekend over` · `hoewel hierover weinig bekend is` · `hoewel niet gedocumenteerd` · `waarschijnlijk groeide hij op` · `vermoedelijk` · `naar alle waarschijnlijkheid` · `het is aannemelijk dat` · `het valt aan te nemen dat` · `men neemt aan dat` · `naar verluidt` · `lijkt te hebben gestudeerd` · `houdt zich bewust op de achtergrond` · `blijft liever uit de schijnwerpers` · `de organisatie doet hier geen uitspraken over` · `dit suggereert dat` · `dit wijst erop dat` · `op basis van de beschikbare informatie` · `hoewel specifieke details beperkt zijn` (+3)

Voor: Over haar jeugd is weinig bekend, wat erop wijst dat zij zich bewust op de achtergrond houdt. Waarschijnlijk groeide zij op in een middenklassegezin.

Na: De bronnen die ik heb gebruikt zeggen niets over haar jeugd.

Niet markeren: 'Vermoedelijk' en 'naar verluidt' zijn in journalistiek en in historisch onderzoek legitieme markeringen als de onzekerheid zelf uit een bron komt; daarom staan ze hier als cue en niet in de regex. Niet markeren in een methodeparagraaf die eerlijk beschrijft wat wel en niet gevonden is, zolang er daarna geen invulling volgt.

### Vage bronvermelding `vague-attribution`

Ernst: **always** · Herkomst: nl-bron · en: `vague-attribution`

Een bewering wordt toegeschreven aan een gezag dat de tekst nooit benoemt: experts, deskundigen, onderzoek, studies, waarnemers, critici, analisten, branchekenners. Subvormen zijn de vage externe bevestiging waarbij een ongenoemde partij een superlatief levert (wordt algemeen beschouwd als) en het oordeel zonder oordelaar (velen vinden, men zegt dat). Noem de bron met naam en jaar, of haal de zin weg.

Signalen: `experts zeggen` · `deskundigen stellen` · `onderzoek toont aan dat` · `uit onderzoek blijkt` · `uit studies blijkt` · `studies laten zien` · `volgens critici` · `sommige critici stellen` · `wordt algemeen beschouwd als` · `het wordt algemeen erkend dat` · `branchekenners melden` · `kenners wijzen erop` · `men zegt dat` · `velen beschouwen` · `waarnemers merken op` · `steeds meer organisaties kiezen voor` · `veel bedrijven merken dat`

Voor: Deskundigen stellen dat hybride werken de productiviteit verhoogt, en uit onderzoek blijkt dat werknemers tevredener zijn.

Na: TNO mat in 2024 bij 1.200 kantoorwerkers geen verschil in productiviteit tussen twee en vier kantoordagen.

Niet markeren: Niet markeren als de bron in dezelfde of de vorige zin met naam staat (onderzoekers van de UT stellen), en niet in een samenvatting van een debat waarin de tekst juist zegt dat de partijen ongenoemd blijven. In wetenschappelijke tekst met een verwijzing erachter is 'uit onderzoek blijkt (Kok, 2021)' gewoon correct.

### Abstractie waar een concreet gegeven bestaat `abstraction-over-specifics`

Ernst: **cluster** · Herkomst: transfer · en: `abstraction-over-specifics`

Een claim blijft abstract terwijl er een naam, een getal, een datum, een mechanisme of een voorbeeld beschikbaar is: verbeterde de efficiëntie, aanzienlijk sneller, een groot bestand, een database in plaats van de productnaam. Subvormen zijn het abstracte hoeveelheidswoord in plaats van een gemeten waarde en het categoriewoord in plaats van de naam van het ding. Zet het getal, de naam of het mechanisme terug.

Signalen: `verbeterde de efficiëntie` · `aanzienlijk sneller` · `significant verbeterd` · `een groot bestand` · `diverse voordelen` · `in hoge mate` · `een aantal verbeteringen` · `aanzienlijke besparingen`

Voor: De koppeling verbeterde de efficiëntie aanzienlijk.

Na: Door de koppeling ging de deploytijd van 40 naar 4 minuten.

Niet markeren: Niet markeren als het abstracte woord het onderwerp is (een definitie van efficiëntie) of als de meting elders in het stuk staat. In samenvattingen en abstracts hoort een zekere mate van abstractie bij het genre, en 'in hoge mate' is in juridisch en wetenschappelijk register gewoon de gangbare formulering; de tell is de abstractie waar de schrijver het getal had.

### Cliché en overdadig proza `cliche-and-purple-prose`

Ernst: **cluster** · Herkomst: transfer · en: `cliche-and-purple-prose`

Standaardformuleringen en overversierde beschrijving zonder iets eronder: alles wat de tekst bedoelt staat op de bladzijde, er zit geen laag onder het beeld, en de versiering vervangt de waarneming. In het Nederlands gaat het om eigen clichés (het hart bonkte in haar keel, een golf van emoties) en om beeldspraak die te groot is voor het onderwerp (een rijk tapijt, een symfonie van, een baken van hoop). Ervaren lezers noemen juist dit cluster als de manier waarop ze machinefictie herkennen.

Signalen: `haar hart bonkte in haar keel` · `een traan gleed over haar wang` · `niets zou ooit nog hetzelfde zijn` · `met een brok in de keel` · `de tijd leek stil te staan` · `een golf van emoties` · `rijk tapijt` · `een symfonie van` · `baken van hoop`

Voor: Haar hart bonkte in haar keel terwijl een traan over haar wang gleed, en ze wist dat niets ooit nog hetzelfde zou zijn.

Na: Ze las het bericht twee keer, legde haar telefoon omgekeerd neer en ruimde de vaatwasser verder in.

Niet markeren: Niet markeren in een citaat, in pastiche of parodie, en niet bij één vaste uitdrukking in een verder sobere tekst. In liedteksten en in gelegenheidspoëzie hoort een deel van dit register bij het genre.

### Schrijven vanaf de wijziging `diff-anchored-writing`

Ernst: **cluster** · Herkomst: transfer · en: `diff-anchored-writing`

Documentatie of proza beschrijft het ding als een verandering ten opzichte van een toestand die de lezer nooit zag: deze functie vervangt de oude aanpak, de verbeterde versie kan nu ook, voorheen moest je. Een lezer zonder commitgeschiedenis krijgt archeologie in plaats van gedrag. Beschrijf wat het nu doet en zet de geschiedenis in de changelog of het commitbericht.

Signalen: `ter vervanging van de oude aanpak` · `voorheen moest je` · `de oude methode` · `de verbeterde versie` · `nu ondersteunt het ook` · `in tegenstelling tot vroeger`

Voor: Deze functie is toegevoegd ter vervanging van de oude aanpak waarbij alle items werden doorlopen.

Na: Deze functie zoekt items op in een hashmap, dus een lookup kost constante tijd.

Niet markeren: Niet markeren in een changelog, een migratiegids, release notes of een ADR: daar is de vorige toestand het onderwerp. In gebruikersdocumentatie en in referentiepagina's is het wel een tell.

### Ecosysteem- en erfgoedvulling `ecosystem-heritage-padding`

Ernst: **cluster** · Herkomst: transfer · en: `ecosystem-heritage-padding`

Een stuk over een soort, een plek of een voorwerp wordt opgevuld met algemene verbanden met het ecosysteem, het milieu of het cultureel erfgoed die uit geen enkele bron blijken. De tekst blijft daarna hangen op beschermingsstatus, bedreigingen en behoud, ook waar geen beoordeling en geen inspanning bestaan. De verraderlijkste vorm geeft eerst toe dat er geen beoordeling is en speculeert daarna toch over bedreigingen. Houd de ecologie die in een bron staat en laat de rest weg.

Signalen: `speelt een rol in het ecosysteem` · `draagt bij aan het rijke culturele erfgoed` · `het behoud van deze soort is van groot belang` · `er is geen specifieke beoordeling van de beschermingsstatus` · `bedreigingen zoals overbevissing, vervuiling en habitatverlies` · `van onschatbare waarde voor de biodiversiteit`

Voor: De soort speelt een rol in het ecosysteem en draagt bij aan het rijke culturele erfgoed van de streek.

Na: De soort komt in Nederland alleen voor op de Sallandse Heuvelrug.

Niet markeren: Niet markeren in een beheerplan, een Natura 2000-document of een rode lijst, waar beschermingsstatus en bedreigingen het onderwerp zijn en uit een beoordeling komen.

### Lege kanttekening `empty-caveat-slot`

Ernst: **cluster** · Herkomst: transfer · en: `empty-caveat-slot`

Een toegevende zin die niets toegeeft: een niet-benoemde uitdaging gekoppeld aan een niet-benoemd antwoord (ondanks de uitdagingen blijft de organisatie groeien), of een losse regel dat er kanttekeningen blijven na een reeks positieve claims. Het speelt evenwicht en voegt niets toe. Benoem de echte uitdaging en het echte antwoord, of laat de zin weg.

Signalen: `ondanks de uitdagingen blijft` · `er blijven uitdagingen bestaan` · `er zijn ook kanttekeningen` · `natuurlijk zijn er ook nadelen` · `toch is er ook kritiek` · `er valt ook wat op af te dingen` · `blijft veerkrachtig`

Voor: Ondanks de uitdagingen blijft de coöperatie groeien.

Na: De coöperatie verloor in 2024 haar grootste afnemer en verving dat volume met drie regionale groothandels.

Niet markeren: Niet markeren als de uitdaging in dezelfde alinea benoemd staat, en niet in een bestuurlijk stuk waarin de kanttekeningen in een eigen paragraaf uitgewerkt worden.

### Uitleg in plaats van betoog `exposition-instead-of-argument-nl`

Ernst: **cluster** · Herkomst: nl-bron

De tekst somt feiten en uitleg op zonder een hoofdargument: er is geen stelling die de alinea's bij elkaar houdt en geen zichtbare keuze tussen mogelijke lezingen. Waar een mens zou vertellen, vergelijken of betogen, informeert de tekst. Dit is in het onderwijs een van de gangbaarste signalen bij ingeleverde essays. Zet de stelling in de eerste alinea en laat elke alinea er iets aan toevoegen of tegenin gaan.

Signalen: `een lijst met feiten en informatie` · `geen duidelijk hoofdargument` · `meer informatief, minder verhalend` · `elke alinea legt uit, geen enkele beweert iets`

Voor: Scrum kent drie rollen, vijf gebeurtenissen en drie artefacten. Kanban werkt met een bord en een WIP-limiet. Beide methoden worden veel gebruikt.

Na: Voor een team van vier met veel binnenkomend werk is Kanban de betere keuze, omdat de sprintverplichting van Scrum bij ons elke week sneuvelde.

Niet markeren: Niet markeren bij genres die met opzet informatief zijn: een encyclopedie-artikel, een handleiding, een productbeschrijving, notulen of een naslagpagina. De tell geldt voor tekst waar een standpunt of een keuze werd gevraagd.

### Verzonnen spreektaal `fabricated-colloquialism-nl`

Ernst: **cluster** · Herkomst: nl-bron

Een poging tot informele toon die niemand zo zegt: bedachte spreektaal in plaats van gehoorde. In het Nederlands zijn de vaakst voorkomende vormen letterlijke vertalingen van Engelse gemeenplaatsen (aan het eind van de dag, impact maken, het verschil maken) die in een gesproken Nederlandse zin nooit zo vallen. Vervang ze door wat je iemand hier echt hoort zeggen, of laat de zin gewoon zakelijk.

Signalen: `aan het eind van de dag draait het om impact maken` · `het verschil maken` · `je moet er gewoon voor gaan`

Voor: Aan het eind van de dag draait het om impact maken voor de klant.

Na: Uiteindelijk telt of de klant er iets aan heeft.

Niet markeren: 'Aan het einde van de dag' in de letterlijke betekenis van tijd is gewoon Nederlands en valt buiten de regex, die een figuurlijk vervolg eist (draait, telt, gaat het om). Niet markeren in een citaat waarin iemand het zelf zegt, en niet in marketingtekst die dit register bewust hanteert.

### Vlakke dialoog en uitleg voor de lezer `flat-dialogue-and-exposition`

Ernst: **cluster** · Herkomst: transfer · en: `flat-dialogue-and-exposition`

Personages zijn onderling verwisselbaar: geen eigen woorden, geen tic, geen dialect, geen eigen manier van ontwijken onderscheidt de een van de ander. In de dialoog staat bovendien informatie die de sprekers allang delen, zodat de lezer hem kan horen, en raadsels worden opgelost met uitleg in plaats van met handeling. Geef elke spreker een eigen manier van praten en laat de gebeurtenissen het verhaal dragen.

Signalen: `zoals je weet` · `zoals u weet` · `zoals we allemaal weten` · `alle personages praten hetzelfde` · `uitleg in dialoog voor de lezer`

Voor: Zoals je weet, dokter, is de reactor in 1974 gebouwd en sindsdien nooit nagekeken, zei ze.

Na: Negentienvierenzeventig, zei ze. Sindsdien heeft niemand hem opengemaakt. Hij wist het al en liet haar het zeggen.

Niet markeren: 'Zoals je weet' is in gewone correspondentie en in lesmateriaal een normale beleefdheidsformule; de tell is de vorm in dialoog waar de spreker informatie geeft die de ander al heeft. Niet markeren in toneel waar het personage die formule met opzet gebruikt.

### Gratis universalia en categoriefouten `gratuitous-universals-and-category-errors`

Ernst: **cluster** · Herkomst: transfer · en: `gratuitous-universals-and-category-errors`

Gezag wordt geleend van een bereik dat de schrijver niet kan nagaan (elke ontwikkelaar weet, wordt in elk eerstejaarscollege behandeld, niemand betwist dat), en morele of waarderende bijvoeglijke naamwoorden komen terecht op dingen die ze niet kunnen dragen, tot en met aannames en abstracties die intenties of deugden krijgen. Vervang de kwantor door het echte bereik en het morele bijvoeglijk naamwoord door de eigenschap die je bedoelt.

Signalen: `elke ontwikkelaar weet` · `iedereen weet dat` · `in elk eerstejaarscollege` · `wordt overal onderwezen` · `niemand betwist dat` · `een eerlijke aanname` · `een moedige architectuur`

Voor: Wordt in elk eerstejaarscollege biochemie behandeld, iedereen weet dat.

Na: Staat in de inleiding biochemie van de UT, tweede blok.

Niet markeren: Niet markeren als het bereik echt universeel en controleerbaar is (elke Nederlandse gemeente heeft een raad), en niet in een citaat of in openlijk hyperbolisch taalgebruik zoals een column.

### Bedachte conceptlabels `invented-concept-labels`

Ernst: **cluster** · Herkomst: transfer · en: `invented-concept-labels`

Een pseudo-analytische samenstelling wordt halverwege de zin gemunt en nooit gedefinieerd (de supervisieparadox, de contextval, een coördinatiebelasting), of een bestaand begrip wordt aan het onderwerp toegeschreven als vondst (hij introduceerde de term). Iets een naam geven is geen verklaring. In het Nederlands plakt het label meestal aaneen tot één samenstelling, wat het makkelijker te herkennen maakt. Beschrijf het mechanisme in gewone woorden, of laat de bron de naam leveren.

Signalen: `de supervisieparadox` · `het contextprobleem` · `een coördinatiebelasting` · `-paradox` · `-spagaat` · `-kloof` · `wat ik de contextval noem` · `de zogeheten ...` · `hij introduceerde de term`

Voor: Dit is de supervisieparadox: hoe meer je automatiseert, hoe meer je moet meekijken.

Na: Door de controles te automatiseren verschoof het werk. Iemand leest nu 200 samenvattingen per week in plaats van er 20 te schrijven.

Niet markeren: Niet markeren bij ingeburgerde begrippen met een vindbare herkomst (de tweelingparadox, de paradox van Simpson, de digitale kloof) en niet als de tekst het label direct definieert en er daarna mee werkt.

### Werktitel behandeld als bestaand ding `list-title-as-entity`

Ernst: **cluster** · Herkomst: transfer · en: `list-title-as-entity`

De openingszin definieert een werktitel of een beschrijvende titel alsof het een ding in de wereld is: X verwijst naar, X is het chronologische overzicht van, de lijst van ... is een samengestelde verzameling. Het artikel gaat dan over zijn eigen titel in plaats van over zijn onderwerp. Introduceer het onderwerp meteen.

Signalen: `verwijst naar de verzameling` · `is een samengesteld overzicht van` · `is de chronologische lijst van` · `De "Lijst van ..." is`

Voor: De "Lijst van liedjes over Twente" is een samengesteld overzicht van muziekwerken die naar Twente verwijzen.

Na: Liedjes over Twente lopen van de Daglichtploeg tot Normaal.

Niet markeren: Niet markeren bij echte namen die toevallig als een titel klinken (De Nachtwacht, de Lijst Pim Fortuyn) en niet in metadocumentatie die met opzet over een lijst gaat, zoals een onderhoudspagina.

### Verloren context uit de draad of de opdracht `lost-thread-context`

Ernst: **cluster** · Herkomst: transfer · en: `lost-thread-context`

Een antwoord beantwoordt niet wat er gevraagd is: het reageert op het onderwerp in plaats van op de vraag, laat de specifieke punten uit de draad vallen en brengt informatie terug die al afgehandeld was. Dezelfde fout in een opdracht ziet er zo uit dat de gevraagde lengte of opzet genegeerd wordt en juist de stof ontbreekt die centraal stond, terwijl er materiaal in staat dat er niet vandaan komt. In correspondentie is dit het duidelijkste teken dat de tekst uit een samenvatting is gemaakt en niet uit de draad.

Signalen: `Bedankt voor je bericht over de factuur` · `Ons team helpt je graag verder` · `We staan voor je klaar` · `antwoord op het onderwerp in plaats van op de vraag` · `gevraagde lengte of opzet genegeerd` · `de gevraagde stof ontbreekt`

Voor: Bedankt voor je bericht over de factuur. Ons team helpt je graag verder met al je vragen.

Na: Factuur 2214 stond op het oude inkoopnummer. Ik heb hem gecrediteerd en opnieuw gestuurd op PO 8871, zoals je dinsdag vroeg.

Niet markeren: Niet markeren bij een eerste reactie op een binnengekomen bericht waarin de dank oprecht de opening is en het antwoord daarna wel op de vraag ingaat, en niet bij een automatische ontvangstbevestiging die zichzelf als zodanig aankondigt.

### Geen concreet detail (verplaatsbare zin) `missing-concrete-detail`

Ernst: **cluster** · Herkomst: transfer · en: `missing-concrete-detail`

De tekst blijft op het niveau van het algemene en het overal toepasbare: geen eigennaam, geen merk, geen straat, geen maand, geen eigenaardig citaat, niets wat alleen hier kan staan. De toets is verplaatsbaarheid: kan een zin ongewijzigd naar een andere persoon, stad of onderneming, dan is het vulling. Een verwante vorm is het antwoord dat op elke vraag past en de niche-kennis mist die het publiek juist wel heeft. Vervang de zin door een feit, een voorbeeld, een mechanisme of een gevolg dat alleen voor dit onderwerp geldt.

Signalen: `geen eigennaam, geen getal, geen datum in de hele alinea` · `geen enkel detail dat alleen hier past` · `breed, niet-specifiek of te algemeen` · `vage algemeenheden zonder concrete details` · `niche-kennis die het publiek zou kennen ontbreekt`

Voor: Loop een paar straten van het centrum en je ontdekt een rustiger, authentieker kant van de stad: sfeervolle gevels en vriendelijke bewoners.

Na: Twee straten omhoog vanaf de markt hangt het wasgoed nog buiten en staan de ramen open bij de wedstrijd.

Niet markeren: Geen lexicale cues mogelijk, dus geen regex: dit is een oordeel over een alinea. Niet markeren in inleidingen, definities en samenvattingen die met opzet algemeen zijn, en niet bij één algemene zin tussen concrete alinea's.

### Relevantie bewijzen met namen `notability-name-dropping`

Ernst: **cluster** · Herkomst: transfer · en: `notability-name-dropping`

Belang wordt aangetoond door op te sommen waar het onderwerp is verschenen in plaats van wat er gezegd is: een rij prestigieuze titels, een classificatie daarvan (onafhankelijke berichtgeving, landelijke media) of een volgersaantal. Een verwante vorm prijst een bewerking omdat die goed gebrond is, in plaats van te zeggen wat eraan is toegevoegd. Houd een verwijzing met inhoud en laat de opsomming weg.

Signalen: `werd geciteerd in NRC, de Volkskrant en het FD` · `onafhankelijke berichtgeving` · `landelijke media` · `regionale media` · `een actieve aanwezigheid op sociale media` · `meer dan 500.000 volgers` · `vakbladen`

Voor: Haar opvattingen werden geciteerd in NRC, de Volkskrant, het FD en Trouw, en ze heeft een actieve aanwezigheid op sociale media met meer dan 500.000 volgers.

Na: In NRC bepleitte ze in 2024 dat statistiekbureaus hun ruwe microdata publiceren.

Niet markeren: Niet markeren waar het bereik het onderwerp is, zoals een mediaverantwoording, een jaarverslag of een relevantiediscussie op Wikipedia. Eén verwijzing met een citaat erbij is gewoon bronvermelding.

### Scheve of gemengde metafoor `off-metaphor`

Ernst: **cluster** · Herkomst: transfer · en: `off-metaphor`

Beelden komen uit de juiste betekenishoek met de verkeerde natuurkunde: figuren die uit elkaar vallen zodra je ze voor je ziet, of twee onverenigbare beelden in één zin gelast. Het model grijpt naar het bijbehorende woord in plaats van naar het werkende beeld. De toets is de metafoor letterlijk voorstellen; is dat plaatje onmogelijk, bouw hem dan opnieuw op uit iets wat je echt hebt gezien.

Signalen: `twee onverenigbare beelden in één zin` · `beeld dat uit elkaar valt als je het voor je ziet` · `fluisterde door de circuits` · `een rivier van logica die opbloeide`

Voor: Het algoritme fluisterde door de circuits, een rivier van logica die opbloeide in de tuin van haar geest.

Na: Het algoritme liep zoals water een scheur vindt. Het nam de goedkoopste weg en maakte die breder.

Niet markeren: Oordeel, geen cues, dus geen regex. Niet markeren bij vaste uitdrukkingen die technisch gemengd zijn maar ingeburgerd (de kar trekken, het roer omgooien) en niet in surrealistische of komische tekst waar de botsing het effect is.

### Decor als stemmingsspiegel `pathetic-fallacy-mood-setting`

Ernst: **cluster** · Herkomst: transfer · en: `pathetic-fallacy-mood-setting`

Weer, kamers en voorwerpen bestaan alleen om het gevoel van een personage te spiegelen: regen bij verdriet, een kamer die koud is omdat het huwelijk dat is. Het decor draagt geen zelfstandig feit meer en houdt daarmee op een plek te zijn. Laat het decor zichzelf zijn en laat de emotie uit de gebeurtenis komen.

Signalen: `alsof de regen haar verdriet weerspiegelde` · `tikte zacht tegen het raam` · `de lucht was net zo grauw als haar stemming` · `de kamer voelde koud aan, net als` · `de lucht weerspiegelde haar stemming`

Voor: De regen tikte zacht tegen het raam, alsof hij haar onuitgesproken verdriet weerspiegelde.

Na: Het regende. Ze hield het raam toch open, want de kamer rook naar zijn shag.

Niet markeren: Niet markeren als het weer een rol speelt in de handeling (de wedstrijd ging niet door), en niet in poëzie of in een stijl die het beeld bewust en herkenbaar inzet. Één stemmig decorzinnetje in een verhaal is geen patroon.

### Brochuretaal `promotional-language`

Ernst: **cluster** · Herkomst: nl-bron · en: `promotional-language`

Tekst die wil informeren zakt af naar reclame: waarderende bijvoeglijke naamwoorden, reisgidsformules en persberichtwerkwoorden over plaatsen, verenigingen, mensen en bedrijven. De twee subvormen zijn de erfgoedreisgids (gelegen in het hart van, adembenemend, rijke geschiedenis, een absolute aanrader) en het bedrijfspersbericht (toonaangevend, zet zich in voor, unieke combinatie van, state of the art). Schrap het oordeel en houd het feit dat eronder zit. Op tekstniveau is de tell een positieve sfeer zonder één narekenbare bewering: uniek, adembenemend, baanbrekend, naar een hoger niveau tillen, een must voor iedereen die.

Signalen: `gelegen in het hart van` · `het bruisende hart van` · `adembenemend` · `rijke geschiedenis` · `rijk cultureel erfgoed` · `een must voor iedere bezoeker` · `een absolute aanrader` · `niet te missen` · `indrukwekkende natuurlijke schoonheid` · `genesteld tussen` · `unieke sfeer` · `toonaangevend` · `gerenommeerd` · `zet zich in voor` · `unieke combinatie van` · `biedt een schat aan` · `onderscheidt zich door` · `hét adres voor` (+6)

Voor: Gelegen in het bruisende hart van Twente is Almelo een levendige stad met een rijke geschiedenis en adembenemende natuur om de hoek.

Na: Almelo ligt in Twente en heeft 73.000 inwoners.

Niet markeren: Niet markeren in tekst die openlijk reclame is: een advertentie, een wervingspagina of een citaat uit een persbericht. In een reisgids of VVV-tekst hoort een deel van dit register erbij; de tell is het register in een encyclopedisch of journalistiek stuk. Eigennamen die het woord bevatten (Bruisend Twente, De Gerenommeerde) blijven staan. In reclame en productcopy is dit het genre; markeer het waar de tekst informatief hoort te zijn. Een geciteerde recensie mag superlatieven bevatten. Eén enthousiast bijvoeglijk naamwoord in een persoonlijk verslag is stem.

### Opgeblazen betekenis `significance-inflation`

Ernst: **cluster** · Herkomst: transfer · en: `significance-inflation`

Een gewoon feit krijgt het gewicht van een keerpunt, een erfenis of het bewijs van een brede trend, met een kleine vaste set duidingswerkwoorden: markeert een keerpunt, speelt een cruciale rol, onderstreept het belang van, getuigt van. Twee subvormen: de zelfbenoemde betekenis (dit is een belangrijk inzicht) en duiding vastgeplakt aan een alledaags gegeven zoals een etymologie of een inwonertal. De reparatie is het feit laten staan en de duiding schrappen, of hem vervangen door een gevolg dat je kunt aanwijzen.

Signalen: `markeert een keerpunt` · `vormt een mijlpaal` · `speelt een cruciale rol` · `onderstreept het belang van` · `getuigt van` · `blijvende nalatenschap` · `zet de toon voor` · `laat een onuitwisbare indruk achter` · `in het snel veranderende landschap` · `is van onschatbare waarde` · `vormt de basis voor` · `weerspiegelt een bredere ontwikkeling`

Voor: Het bureau werd in 1899 opgericht, wat een keerpunt markeerde in de Nederlandse statistiek en getuigt van een blijvende nalatenschap.

Na: Het bureau werd in 1899 opgericht, tijdens een reeks bestuurlijke hervormingen.

Niet markeren: Niet markeren in een tekst waarin de betekenis het onderwerp zelf is, zoals een herdenkingsrede of een juryrapport, en niet bij een gedocumenteerd keerpunt met bron erbij. Een enkele keer 'speelde een belangrijke rol' in een historisch overzicht is gewoon Nederlands; het patroon is de opeenstapeling.

### Opgeblazen bronnentelling `source-count-inflation`

Ernst: **cluster** · Herkomst: transfer · en: `source-count-inflation`

Er staan bronnen in de tekst, maar hun aantal of hun breedte klopt niet: de mening van een persoon wordt breed gedeeld genoemd, meervoudige recensenten of publicaties staan voor een enkele naam, en 'meerdere bronnen' verschijnt boven twee verwijzingen. Ook 'zoals' suggereert een langere lijst dan de bronnen dragen. Laat het meervoud kloppen met het aantal verwijzingen, of noem de ene bron die je hebt.

Signalen: `meerdere bronnen` · `verschillende publicaties` · `diverse media` · `meerdere onderzoeken` · `veel wetenschappers` · `wordt breed geïnterpreteerd` · `recensenten noemden`

Voor: Verschillende publicaties noemden het apparaat een onderwijsplatform.

Na: Bright noemde het apparaat in maart 2024 een onderwijsplatform.

Niet markeren: Niet markeren als het aantal klopt en de bronnen erbij staan, en niet in een methodeparagraaf waarin het aantal bronnen zelf het gegeven is (we vonden 12 publicaties).

### Tredmolen (herhalen zonder vooruit te komen) `treadmill-redundancy`

Ernst: **cluster** · Herkomst: transfer · en: `treadmill-redundancy`

Alinea's herformuleren het uitgangspunt in nieuwe woorden in plaats van het verder te brengen: beweging zonder afstand. De tekenen zijn een passage die 40 tot 60 procent korter kan zonder informatieverlies, verbanden tussen alinea's die worden beweerd en niet gelegd, en volle alinea's met lege clichézinnen. Benoem per alinea het ene feit, de ene claim of de ene wending; is die er niet, dan gaat de alinea eruit.

Signalen: `dezelfde stelling in andere woorden` · `alinea die 40 tot 60 procent korter kan zonder verlies` · `verband beweerd in plaats van gelegd` · `met andere woorden, ...` · `nietszeggende opvulzinnen` · `veel herhaling in andere bewoordingen`

Voor: Testen is belangrijk. Zonder tests kan een team niet met vertrouwen wijzigen. Dat gebrek aan vertrouwen vertraagt de levering, omdat engineers aarzelen om code aan te passen die ze niet kunnen verifiëren.

Na: Zonder tests durven engineers de code niet aan te raken, en onze mediane PR bleef drie dagen liggen.

Niet markeren: De regex vangt alleen de expliciete herformuleermarkeerder en raakt het voorbeeld met opzet niet: de echte tredmolen heeft geen signaalwoord en moet met de hand beoordeeld worden. Één 'met andere woorden' na een formule of een citaat is gewoon uitleg; niet markeren in lesmateriaal, waar herhaling didactisch is.

### Plaatsing in een niet-benoemd debat `unnamed-debate-situating`

Ernst: **cluster** · Herkomst: transfer · en: `unnamed-debate-situating`

Het onderwerp zou discussie of debat hebben losgemaakt, vragen oproepen of tot nadenken stemmen, terwijl het debat, de deelnemers, de plaats en de datum nergens staan. De zin ziet eruit als context en levert er geen. Benoem wie wat waar zei, of laat de zin weg.

Signalen: `heeft geleid tot discussie over` · `roept vragen op over` · `zorgde voor de nodige discussie` · `wakkert het debat aan` · `leidde tot maatschappelijk debat` · `stemt tot nadenken over`

Voor: Het initiatief heeft geleid tot discussie over toegankelijkheid en roept vragen op over de rol van de gemeente.

Na: In de raadsvergadering van 14 mei stemde de VVD tegen de subsidie omdat de zaal geen lift heeft.

Niet markeren: Niet markeren als het debat in dezelfde alinea wordt benoemd met deelnemer, plek of datum, en niet in een verslag van een vergadering waar de discussie zelf het onderwerp is.

### Vage verbinding `vague-association`

Ernst: **cluster** · Herkomst: transfer · en: `vague-association`

Een concrete relatie (was directeur van, doceerde aan, componeerde voor, ontving) wordt vervangen door een onbepaalde band: in verband gebracht met, geassocieerd met, gelieerd aan. De zin ziet er gebrond uit en zegt niets wat je kunt nagaan. Haal de echte relatie uit de bron en schrijf die op.

Signalen: `in verband gebracht met` · `geassocieerd met` · `wordt gelinkt aan` · `gelieerd aan` · `verbonden aan` · `houdt verband met`

Voor: In 2017 werd Jan de Vries in verband gebracht met de leiding van het bedrijf.

Na: Jan de Vries was in 2017 directeur van het bedrijf.

Niet markeren: 'Verbonden aan' plus een instelling is in het Nederlands een precieze en gangbare formulering (verbonden aan de Universiteit Twente) en staat daarom niet in de regex. 'Geassocieerd met' is in medische en statistische tekst een vakterm voor correlatie; daar niet markeren. In berichtgeving over een strafzaak is 'in verband gebracht met' soms juist de zorgvuldige formulering.

### Geschatte marge in plaats van een meting `vague-numeric-range`

Ernst: **cluster** · Herkomst: transfer · en: `vague-numeric-range`

Er staat een marge waar een enkel waargenomen getal had gestaan als de schrijver het echt had gedaan: duurt 5 tot 10 minuten, tussen de 20 en 30 verzoeken, een uur of twee. De marge verklapt dat het cijfer geraden is. Noem het getal dat je gemeten hebt, of zeg dat je niet gemeten hebt.

Signalen: `duurt 5 tot 10 minuten` · `tussen de 20 en 30` · `ongeveer 10 tot 15 procent` · `een uur of twee, drie` · `5 à 10 minuten`

Voor: De installatie duurt 5 tot 10 minuten.

Na: De installatie duurde 7 minuten op een schone machine.

Niet markeren: Niet markeren waar de spreiding zelf het gegeven is: een meetreeks, een prognose, een dienstregeling, een dosering of een bandbreedte uit een bron. Een historische periode (van 1940 tot 1945) valt buiten de regex omdat er geen eenheid achter staat.

### Ontbrekende menselijke wrijving `absent-human-friction`

Ernst: **context** · Herkomst: transfer · en: `absent-human-friction`

Dit is een patroon van afwezigheden: de tekst onderbreekt zichzelf nooit met een correctie of een echte terzijde, geeft nooit een onopgelost dubbel gevoel toe, citeert niemand en draagt geen tijdgebonden verwijzing, grap of uitdrukking. Gepubliceerd menselijk proza citeert vrijelijk en spreekt zichzelf terloops tegen. Het is zwakke ondersteuning op zichzelf; de waarde zit in het bewaren van de wrijving die er wel is.

Signalen: `nul citaten in het hele stuk` · `geen enkele terzijde tussen haakjes` · `geen tijdgebonden verwijzing` · `geen correctie, geen aarzeling, geen dubbel gevoel`

Voor: De migratie verliep goed en het team was tevreden met het resultaat.

Na: De migratie verliep goed, al was de eerste nacht dat niet. Ellen zei achteraf: nooit meer op een donderdag.

Niet markeren: Geen regex mogelijk. Niet markeren in korte teksten, in normatieve documenten en in genres waar een terzijde ongepast is (bijsluiter, vergunning, notariële akte). Op zichzelf nooit voldoende bewijs.

### Geen eerstehands detail of standpunt `missing-first-hand-detail`

Ernst: **context** · Herkomst: transfer · en: `missing-first-hand-detail`

In een stuk waarvan het register om een stem vraagt, staat niets wat alleen deze schrijver kon leveren: geen anekdote, geen zelf gemeten getal, geen benoemde mislukking, geen voorkeur, geen 'ik denk'. Het proza blijft onverstoorbaar neutraal waar een keuze werd verwacht, en elke optie krijgt evenveel ruimte. Een vuistregel is ongeveer één schrijverspecifiek detail per sectie; daaronder draait het stuk op algemeenheden. De reparatie is een eigen getal, een eigen geval of een uitgesproken voorkeur, niet een zin die er een claimt.

Signalen: `geen anekdote, geen eigen getal, geen benoemde mislukking` · `elke optie krijgt evenveel ruimte, geen keuze` · `ik denk ontbreekt waar het register erom vraagt` · `afwezigheid van elk eigen geval`

Voor: Er zijn verschillende benaderingen van piketdienst, elk met voor- en nadelen, en teams moeten kiezen wat bij hen past.

Na: We draaiden acht maanden follow-the-sun en dat kostte ons twee engineers. Voor een team van zes werkt een weekrooster met een harde overdracht beter.

Niet markeren: Niet markeren in registers die juist geen stem hebben: encyclopedie, norm, handleiding, notulen, productdocumentatie. En let op de tegenovergestelde fout: het gat vullen met een verzonnen ervaring is erger dan het gat (zie fake-first-person). In dit repo worden veldverslagen opgetekend uit interviews, dus de stem hoort van de geïnterviewde te komen.

### Autoritair gekleurde framing `pro-authoritarian-bias`

Ernst: **context** · Herkomst: transfer · en: `pro-authoritarian-bias`

Bij politieke onderwerpen neigt gegenereerde tekst naar de kadering van staatsmedia: regeringen van vrijere landen krijgen makkelijker kritiek dan repressieve, en soms volgt een weigering op veiligheidsgronden die maar één kant op werkt. In het Nederlands is dit niet gemeten, dus de cues zijn gereconstrueerd en de vondst is een aanleiding om te controleren, geen bewijs. Leg politieke kadering naast onafhankelijke verslaggeving voordat je publiceert.

Signalen: `heeft zich onder de huidige regering stabiel ontwikkeld` · `onder leiding van de autoriteiten` · `de situatie is genormaliseerd` · `westerse media melden daarentegen`

Voor: De regio heeft zich onder leiding van de huidige autoriteiten stabiel ontwikkeld en de situatie is inmiddels genormaliseerd.

Na: Human Rights Watch documenteerde in 2025 340 detenties in de regio. Het bestuur betwist dat aantal.

Niet markeren: Geen regex: elke formulering hier komt ook in gewone verslaggeving en in diplomatieke taal voor, dus een regex zou vooral neutrale nieuwstekst raken. Niet markeren bij een geciteerde regeringsverklaring of een weergave van een standpunt die als zodanig gemarkeerd is.

### Plotselinge stijl- en niveausprong `sudden-polish-jump`

Ernst: **context** · Herkomst: nl-bron · en: `sudden-polish-jump`

Woordkeus, zinsbouw en interpunctie springen binnen een stuk of tussen twee opeenvolgende stukken boven het aantoonbare niveau van de schrijver uit. Drie subvormen: de stijlbreuk met alles wat dezelfde persoon eromheen schrijft, de tekst die over de hele lengte geen enkele spel- of tikfout bevat terwijl mensen die wel maken, en beweringen die de schrijver op grond van eigen lezen niet met zekerheid kan doen. Dit vraagt een eerder corpus om tegen af te lezen en wijst op de grens tussen wat de persoon schreef en wat een tool maakte.

Signalen: `foutloze d/t na een tekst vol fouten` · `plotseling geen enkele typefout` · `register springt van spreektaal naar ambtelijk` · `woorden als cruciaal of essentieel in een verder eenvoudige tekst` · `hoogwaardige tekst maar matige communicatie eromheen` · `beweringen boven het kennisniveau van de schrijver`

Voor: (een alinea gewone, foutgevoelige tekst gevolgd door een vlekkeloze volzin met puntkomma en drie bijzinnen)

Na: (vraag de schrijver naar de sprong en vergelijk met drie eerdere stukken voordat je iets concludeert)

Niet markeren: Geen regex: dit is alleen zichtbaar tegen eerder werk. Niet markeren bij een tekst die door een redacteur of een spellingchecker is gegaan, bij een schrijver die in één taal veel sterker is dan in de andere, of bij een stuk waar dagen aan gewerkt is. In het Nederlands is de d/t-foutloosheid het scherpste deelsignaal, en tegelijk het makkelijkst te verklaren door een corrector.

### Dunne of scheve bronnenpraktijk `thin-citation-practice-nl`

Ernst: **context** · Herkomst: nl-bron

Het genre vraagt om verwijzingen en de tekst geeft er minder dan gebruikelijk, vooral in essays en scripties. Wat er wel staat, leunt daarnaast op obscure of oude publicaties waar recentere voor de hand liggen. Anders dan bij verzonnen bronnen bestaan deze bronnen wel; de keuze en het aantal zijn het signaal. Vraag naar de gebruikte literatuur en vergelijk met wat in het vak gangbaar is.

Signalen: `minder verwijzingen dan het genre vraagt` · `alleen bronnen uit de jaren negentig` · `obscure publicaties waar een standaardwerk bestaat` · `geen enkele verwijzing in een betoog van vier pagina's`

Voor: Een betoog van vijf pagina's over privacywetgeving met één voetnoot naar een handboek uit 1998.

Na: Hetzelfde betoog met de AVG-tekst, twee uitspraken van de Autoriteit Persoonsgegevens uit 2024 en het handboek waar het die uitleg vandaan haalt.

Niet markeren: Niet markeren in vakgebieden waar oude bronnen de standaard zijn (wiskunde, taalkunde, rechtsgeschiedenis) en niet in genres zonder verwijzingsplicht: een column, een blog, een interne notitie. Een enkele oude bron zegt niets.

## Machinesporen

### Tekst die middenin stopt `abrupt-cutoff`

Ernst: **always** · Herkomst: transfer · en: `abrupt-cutoff`

Het stuk eindigt midden in een zin of een sectie omdat de generatie tegen een tokenlimiet liep en niemand hem heeft afgemaakt, of omdat het plakken is afgekapt. Herkenbaar aan een slotzin zonder eindleesteken die op een lidwoord, voorzetsel of hulpwerkwoord eindigt. Het Nederlands zet de persoonsvorm vaak achteraan, dus een tekst die op "wordt" of "heeft" eindigt is hier een sterker signaal dan in het Engels. Maak de zin af of snijd terug naar de laatste hele zin.

Signalen: `eindigt midden in een zin` · `geen punt aan het eind van de tekst` · `eindigt op de, het, een, van, dat, om te, wordt, heeft`

Voor: De vier tildes aan het eind zijn wikiopmaak die automatisch

Na: Vier tildes aan het eind ondertekenen je bericht met je gebruikersnaam en een tijdstempel.

Niet markeren: Een fragment dat je bewust citeert of een tekst die je halverwege uit een groter bestand hebt geknipt eindigt legitiem middenin. Koppen, tabelrijen, opsommingsregels en broncode dragen geen eindpunt en vallen buiten de regel. Gedichten en slogans mogen zonder punt eindigen.

### De vraag herhaald voor het antwoord `acknowledgment-loop`

Ernst: **always** · Herkomst: transfer · en: `acknowledgment-loop`

De tekst opent door de vraag terug te formuleren naar degene die hem stelde: "Om je vraag te beantwoorden", "Je vraagt je af of", "Als ik je vraag goed begrijp". In een zelfstandige tekst heeft de lezer niets gevraagd, dus de parafrase zegt niets en vertraagt de opening. Schrap de aanloop en begin bij het antwoord.

Signalen: `Om je vraag te beantwoorden` · `Je vraagt je af of` · `Je vraagt naar` · `Als ik je vraag goed begrijp` · `Wat je vraagt is` · `Even samengevat wat je vroeg`

Voor: Om je vraag te beantwoorden: de cache wordt bij elke schrijfactie ongeldig gemaakt.

Na: De cache wordt bij elke schrijfactie ongeldig gemaakt.

Niet markeren: In een echt vraag-en-antwoordstuk, een interview of een FAQ hoort de vraag er letterlijk boven te staan; dat is opmaak, geen restant. Ook in een antwoordmail op een concrete vraag is een korte terugkoppeling normaal.

### AI-trackingparameter in een URL `ai-url-tracking-parameter`

Ernst: **always** · Herkomst: transfer · en: `ai-url-tracking-parameter`

Een queryparameter die een AI-tool aan de links plakt die het schrijft: utm_source=chatgpt.com, utm_source=openai, utm_source=copilot.com, utm_source=claude.ai, utm_source=perplexity.ai, referrer=grok.com. De parameter is de handtekening van de herkomst, wat de omringende tekst ook beweert. Haal de AI-verwijzer uit de URL en laat de rest van de querystring staan.

Signalen: `utm_source=chatgpt.com` · `utm_source=copilot.com` · `utm_source=openai` · `utm_source=claude.ai` · `utm_source=perplexity.ai` · `referrer=grok.com` · `google.com/search?q= als bronlink` · `chatgpt.com/share/ als bron`

Voor: https://www.nrc.nl/nieuws/2026/02/11/interview?utm_source=chatgpt.com

Na: https://www.nrc.nl/nieuws/2026/02/11/interview

Niet markeren: Een stuk over AI-verkeer of over utm-tagging mag de parameter als voorbeeld tonen. Een eigen campagnelink met utm_source=nieuwsbrief is normale marketingpraktijk en valt hier niet onder.

### Chatbot die zijn eigen antwoord terugneemt `assistant-self-correction-nl`

Ernst: **always** · Herkomst: nl-bron

De tekst spreekt als assistent over zijn eigen eerdere antwoord: hij prijst de vraag, geeft toe dat een claim niet klopte en herformuleert met een sturende overgang. Vaste vormen zijn "Goede en terechte vraag", "Ik zei dat omdat", "Ik had dat niet mogen presenteren" en "Dus om het helder te zeggen:". Dit is een gespreksbeurt, geen tekst; in een gepubliceerd stuk hoort er alleen de gecorrigeerde bewering te staan, met haar bron.

Signalen: `Goede en terechte vraag` · `Ik zei dat omdat` · `Ik had dat niet mogen presenteren` · `Dus om het helder te zeggen:` · `Je hebt gelijk dat ik` · `Excuses, dat klopt niet` · `Dat had ik zorgvuldiger moeten formuleren`

Voor: Goede en terechte vraag. Ik zei dat omdat ik de observatie wilde illustreren, maar ik had dat niet als bestaand onderzoek mogen presenteren. Dus om het helder te zeggen: dat onderzoek bestaat niet.

Na: Er bestaat geen onderzoek dat dit meet.

Niet markeren: Een auteur die in een rectificatie of een blogpost zijn eigen eerdere claim terugneemt schrijft precies zo, en dat is goede journalistiek. De tell is dat de zin over het antwoord gaat in plaats van over het onderwerp, in een tekst die verder geen ik-verteller heeft.

### Briefingtaal en bestemming in het product `brief-vocabulary-and-destination-naming`

Ernst: **always** · Herkomst: transfer · en: `brief-vocabulary-and-destination-naming`

De uitvoer herhaalt de bewoordingen van de criteria waaraan hij moest voldoen, of noemt vanuit de tekst zelf de plek waarvoor hij is geschreven. Subvormen: richtlijnvocabulaire dat in het product terechtkomt ("significante, onafhankelijke berichtgeving, geen triviale vermeldingen"), de bestemming met een bezitsvorm en een regelwoord ("voldoet aan de richtlijnen van Wikipedia") en verwijzingen naar de opdracht ("zoals gevraagd in de briefing"). Zulke zinnen horen in het gesprek met de opdrachtgever, niet in de tekst.

Signalen: `voldoet aan de relevantiecriteria` · `conform de richtlijnen van Wikipedia` · `zoals gevraagd in de briefing` · `significante, onafhankelijke berichtgeving` · `geen triviale vermeldingen of persberichten` · `zoals verzocht in de opdracht`

Voor: Deze bronnen leveren significante, onafhankelijke berichtgeving, geen triviale vermeldingen of persberichten.

Na: (geschrapt uit het artikel; de bronnen staan bij de zin die ze onderbouwen)

Niet markeren: Op een overlegpagina of in een verantwoording mag je uitleggen waarom een onderwerp aan de relevantiecriteria voldoet; daar is het argument. De tell is dat de zin in het artikel zelf staat.

### Verzonnen of kapotte opmaak voor het doelsysteem `broken-target-markup`

Ernst: **always** · Herkomst: transfer · en: `broken-target-markup`

Opmaak die het model niet beheerst komt er verzonnen, verminkt of half toegepast uit. Subvormen: sjabloon- en parameternamen die op het echte schema lijken maar niet bestaan, zodat ze als rode link renderen of niets doen; verhaspelde sjabloonsyntaxis; en verwijzingstags die niet sluiten. Controleer elke sjabloonnaam tegen het doelsysteem voordat je publiceert.

Signalen: `{{Infobox oude bevolking | regio = IJsseldal` · `| archeologische_vindplaatsen =` · `<ref name="bron1">Twentse Courant` · `<sup>[1]</sup>` · `[[Categorie:Nederlandse gemeente]]` · `een sjabloonnaam die op de doelwiki niet bestaat`

Voor: {{Infobox oude bevolking | regio = IJsseldal | archeologische_vindplaatsen = Hunebed D27 }}

Na: {{Infobox archeologische cultuur | regio = IJsseldal | belangrijkstevindplaatsen = Hunebed D27 }}

Niet markeren: Op een wiki zelf zijn categorieregels, infoboxen en ref-tags gewone syntaxis; de regels markeren kandidaten, en alleen het doelsysteem kan zeggen of een sjabloon bestaat. Een ref-tag die verderop in het document sluit valt buiten het venster van de zoekregel en levert dan onterecht een treffer op bij zeer lange citaten.

### Onzichtbare en lookalike-tekens `bypass-trick-characters`

Ernst: **always** · Herkomst: nl-bron · en: `bypass-trick-characters`

Onzichtbare of gelijkende tekens die zijn ingevoegd om AI-detectors te misleiden: zero-width-spatie, zero-width-non-joiner, zero-width-joiner, word joiner en byte order mark, en Cyrillische of Griekse letters op de plaats van Latijnse lookalikes. Hun aanwezigheid betekent dat de tekst door een humanizer of een omzeilingstool is gegaan. Haal de tekens weg en typ het woord opnieuw op je eigen toetsenbord. De codepunten zijn U+200B, U+200C, U+200D, U+2060 en U+FEFF; ze zijn alleen zichtbaar in een code-editor of een hex-viewer en horen in gewone Nederlandse lopende tekst nooit thuis.

Signalen: `U+200B zero-width space` · `U+200C ZWNJ` · `U+200D ZWJ` · `U+FEFF BOM` · `U+2060 word joiner` · `Zero-Width Non-Joiner` · `Zero-Width Joiner` · `onzichtbaar teken in een hex-viewer`

Voor: duikеn in de logs (de tweede e is Cyrillisch, midden in een verder Latijns woord)

Na: duiken in de logs, opnieuw getypt op je eigen toetsenbord

Niet markeren: Een zero-width joiner hoort in emoji-reeksen en in schriften die ligaturen sturen. Een tekst die Russisch, Bulgaars of Grieks citeert bevat die letters legitiem; de regel zoekt naar een enkele vreemde letter tussen Latijnse letters in hetzelfde woord. In Arabisch, Perzisch, Hindi en emoji-samenstellingen doen deze tekens echt werk, en in HTML en JavaScript worden ze bewust gebruikt om een afbreekpunt te zetten. Een BOM aan het begin van een bestand komt van de editor. Buiten die gevallen is er geen reden voor.

### Chatbotopening en assistenttaal vooraf `chatbot-opener`

Ernst: **always** · Herkomst: transfer · en: `chatbot-opener`

De aanloop van de assistent naar het eigenlijke antwoord blijft in de afgeleverde tekst staan. Subvormen: het instemmende woord vooraf ("Natuurlijk!", "Zeker!", "Uiteraard!", "Goede vraag!", "Je hebt helemaal gelijk"), de aankondiging van wat er nu volgt ("Hier is een overzicht van", "Hieronder vind je", "Hieronder volgt"), de verwijzing naar de opdracht ("Zoals gevraagd", "Op basis van wat je hebt gedeeld") en het voorbehoud over wat het model wel en niet kan. De tekst hoort te beginnen bij de eerste zin die inhoud draagt.

Signalen: `Natuurlijk!` · `Uiteraard!` · `Absoluut!` · `Jazeker!` · `Goede vraag!` · `Wat een goede vraag` · `Scherpe vraag` · `Je hebt helemaal gelijk` · `Je hebt volkomen gelijk` · `Hier is een overzicht van` · `Hier is een opzet` · `Hieronder vind je` · `Hieronder volgt` · `Zoals gevraagd` · `Op basis van wat je hebt gedeeld` · `Ik kan je daarbij helpen` · `een gedetailleerdere uitsplitsing`

Voor: Natuurlijk! Hier is een overzicht van de Twentse tech-meetups. De oudste loopt sinds 2015.

Na: Twente heeft vier terugkerende tech-meetups. De oudste loopt sinds 2015.

Niet markeren: "Natuurlijk" midden in een zin is gewoon een bijwoord ("dat gaat natuurlijk niet vanzelf"); alleen als eerste woord met uitroepteken is het een tell. "Hieronder vind je" mag in een echte handleiding of nieuwsbrief die de lezer aanspreekt. In een chatlog dat je bewust citeert hoort de opening erbij: markeer geciteerde gesprekken niet. 'Hieronder staat' is gewoon Nederlands en telt niet mee; alleen 'hieronder vind je' en 'hieronder volgt' zijn de assistentvorm.

### Gelekte citatiemarkup uit de chattool `citation-markup-leak`

Ernst: **always** · Herkomst: transfer · en: `citation-markup-leak`

Interne verwijzingstokens uit een chatinterface overleven het kopieren en staan op de plaats van een echte bronvermelding. Bekende vormen: de contentReference- en oai_citation-tokens, de citeturn- en turn0search-reeksen, kale afsluitende cijfers of Unicode-bolletjes die overblijven nadat de onzichtbare omhulsels zijn gestript, en een verwijzing naar een zoekopdracht ("ga naar zoekopdracht nr. 3") in plaats van naar het document. Vervang door een echte bronvermelding of haal ze weg.

Signalen: `citeturn0search0` · `turn0search1` · `citeturn0news0` · `turn0file` · `:contentReference[oaicite:20]{index=20}` · `[oai_citation:3]` · `turn0image0` · `(ga naar zoekopdracht nr.)` · `<ref name="0search12">`

Voor: De vereniging werd in 1998 opgericht :contentReference[oaicite:20]{index=20}.

Na: De vereniging werd in 1998 opgericht (Kamer van Koophandel, dossier 06012345).

Niet markeren: Een artikel of runbook dat deze tokens beschrijft als verschijnsel bevat ze noodzakelijk; markeer alleen tokens die als bronvermelding fungeren. Een losse hoge voetnootcijfer aan het zinseinde kan gewoon een voetnoot zijn in een systeem dat voetnoten rendert.

### Behulpzaam slot en aanbod om door te gaan `collaborative-closer`

Ernst: **always** · Herkomst: transfer · en: `collaborative-closer`

De afsluiting die aan de opdrachtgever is gericht blijft onder de tekst staan. Subvormen: de behulpzaamheidsafsluiter ("Ik hoop dat dit helpt", "Hopelijk heb je hier wat aan"), het vervolgaanbod als vraag ("Wil je dat ik er voorbeelden bij zet?", "Zal ik het korter maken?") en de open uitnodiging ("Laat het me weten als je nog vragen hebt", "Is er nog iets waarmee ik kan helpen?"). Het hele blok gaat weg; het staat los van de inhoud.

Signalen: `Ik hoop dat dit helpt!` · `Hopelijk heb je hier wat aan` · `Laat het me weten als je nog vragen hebt` · `Laat gerust weten of ik ergens dieper op in moet gaan` · `Wil je dat ik` · `Zal ik er voorbeelden bij zetten?` · `Veel succes ermee!` · `Stel gerust je vragen` · `Is er nog iets waarmee ik kan helpen`

Voor: De migratie loopt in twee fasen. Ik hoop dat dit helpt! Laat het me weten als je wilt dat ik een onderdeel verder uitwerk.

Na: De migratie loopt in twee fasen.

Niet markeren: In een echte mail tussen twee mensen zijn "laat het me weten" en "als je nog vragen hebt" volstrekt normaal; de tell is de plaatsing onder een afgeleverd stuk tekst dat verder niemand aanspreekt. Servicepagina's en handleidingen mogen eindigen met een contactregel, zolang die naar een echt adres wijst en niet naar de schrijver van het antwoord.

### Verdubbelde sectie of alinea `content-duplication`

Ernst: **always** · Herkomst: transfer · en: `content-duplication`

Een sectie of alinea komt binnen hetzelfde stuk woordelijk of bijna woordelijk terug, omdat de generator het spoor bijster raakte van wat er al stond. Twee vormen: dezelfde sectie twee keer uitgestoten, en alinea 3 die als alinea 17 terugkomt met geschud woordgebruik. Op te sporen met alineahashes of n-gram-overlap. Schrap de kopie, en kijk eerst of een van de twee een feit draagt dat de andere kwijt is.

Signalen: `dezelfde sectie twee keer, woord voor woord` · `alinea 3 en alinea 17 zijn dezelfde zin anders geformuleerd` · `twee keer dezelfde kop in de inhoudsopgave`

Voor: De sectie Ontvangst staat er twee keer, woord voor woord, op plek 4 en op plek 9.

Na: Een sectie Ontvangst, op plek 4.

Niet markeren: Een refrein, een vaste kop boven elk hoofdstuk, een samenvatting die de inleiding herhaalt en een juridische bepaling die per artikel terugkeert zijn bewuste herhaling. Ook een tabel die dezelfde rijkop meerdere keren draagt telt niet.

### Kennisgrensdisclaimer en AI-zelfbenoeming `cutoff-disclaimer-and-ai-self-identification`

Ernst: **always** · Herkomst: transfer · en: `cutoff-disclaimer-and-ai-self-identification`

Het model schrijft in de eerste persoon over zijn eigen beperkingen, en die zin blijft staan. Subvormen: het voorbehoud over de kennisgrens ("Op het moment van mijn laatste update", "mijn trainingsdata loopt tot", "ik heb geen toegang tot actuele informatie"), de zelfbenoeming ("Als AI-taalmodel", "Ik ben een taalmodel"), de weigering die op de opdracht slaat in plaats van op het onderwerp, en de standaardafwijzing van professioneel advies. Vervang door een datum met een bron, of schrap.

Signalen: `Op het moment van mijn laatste update` · `Mijn trainingsdata loopt tot` · `Ik heb geen toegang tot actuele informatie` · `Ik heb geen toegang tot internet` · `Als AI-taalmodel` · `Als AI kan ik niet` · `Ik ben een taalmodel` · `Het spijt me, maar ik kan` · `Ik kan geen juridisch advies geven` · `Dit antwoord is gegenereerd door`

Voor: Als AI-taalmodel kan ik geen actuele bezoekersaantallen geven, maar ik schets wel een algemeen beeld.

Na: Actuele bezoekersaantallen zijn niet gepubliceerd.

Niet markeren: Een colofon of verantwoording die eerlijk vermeldt dat een tekst met AI-hulp is gemaakt is beleid, geen restant; dat hoort er juist te staan. Een artikel over taalmodellen mag de frase "als AI-taalmodel" citeren.

### Gegenereerde reactie onder een post `generated-engagement-reply-nl`

Ernst: **always** · Herkomst: nl-bron

Een gegenereerde reactie op een bericht die de auteur bij naam prijst, bedankt voor het delen en verder niets toevoegt: "Interessant perspectief, Piet! Dank voor het delen van deze waardevolle inzichten." De vorm is altijd dezelfde: compliment met naam, dankwoord, een samenvatting van wat er al stond. Een reactie die niets toevoegt hoort niet geplaatst te worden.

Signalen: `Interessant perspectief, Piet!` · `Dank voor het delen van deze waardevolle inzichten` · `Wat een sterk stuk!` · `Helemaal mee eens!` · `Goed punt, dit raakt de kern`

Voor: Interessant perspectief, Piet! Dank voor het delen van deze waardevolle inzichten.

Na: Piet, hoe ging dat bij jullie met de oude Jenkins-pipeline?

Niet markeren: Een oprecht bedankje onder een gastbijdrage of een nieuwsbrief is normaal, zeker als er iets concreets bij staat. De tell is de reactie die alleen prijst, de naam van de schrijver invoegt en de post samenvat zonder een vraag, een ervaring of een bezwaar toe te voegen.

### Generatorwikkel en sprekerlabel `generation-wrapper-and-speaker-label`

Ernst: **always** · Herkomst: transfer · en: `generation-wrapper-and-speaker-label`

De transportverpakking rond het antwoord is met de inhoud mee geplakt. Subvormen: een containerdirectief boven het geleverde stuk (:::writing{variant="document" id="68427"} met een willekeurig vijfcijferig id, gelokaliseerd als :::schrijven{variant=...} en vaak gesloten met een kale :::), en een sprekerlabel uit een transcript dat het model bij naam noemt ("Claude antwoordde:", "ChatGPT: Ik heb de tekst herschreven"). Haal de wikkel weg en houd wat erin stond.

Signalen: `:::writing{variant="document" id="68427"}` · `:::schrijven{variant=` · `Claude antwoordde:` · `ChatGPT: Ik heb de tekst herschreven` · `Gemini zei:`

Voor: :::writing{variant="document" id="68427"}
AK7 is een Belgische rapper.

Na: AK7 is een Belgische rapper.

Niet markeren: Een artikel dat een chatgesprek weergeeft heeft sprekerlabels nodig; daar zijn ze opmaak. Drie dubbele punten zijn in sommige documentatiedialecten een geldig blok (admonitions in MkDocs, Docusaurus), dus toets tegen de opmaaktaal van het bestand.

### Instructies aan degene die het plaatst `instructions-to-the-handler`

Ernst: **always** · Herkomst: transfer · en: `instructions-to-the-handler`

Tekst gericht aan wie het document gaat plakken, indienen of nakijken, gepubliceerd binnenin dat document. Subvormen: genummerde indieningsnotities, de regel die de plaatser opdraagt de notitie te verwijderen ("Verwijder deze sectie voor publicatie"), coaching over wat te zeggen als een beoordelaar bezwaar maakt, en een checklist van wat het onderwerp zou moeten hebben. Het hele blok hoort niet in de tekst.

Signalen: `Verwijder deze sectie voor publicatie` · `Na het plakken van het artikel` · `Let op: pas dit aan voordat je het verstuurt` · `Dien dit in via` · `Als een beoordelaar vraagt`

Voor: Verwijder deze sectie voor publicatie. Zet na het plakken van het artikel de bronnenlijst om naar voetnoten.

Na: (het blok is geschrapt; het artikel begint bij zijn eerste regel)

Niet markeren: In een sjabloon, een checklist of een redactiehandleiding zijn instructies aan de plaatser precies de inhoud. Een insteltekst in een CMS die de redacteur uitlegt wat er in een veld hoort is ook geen restant.

### Opzet gepubliceerd in plaats van de sectie `outline-plan-left-in-body`

Ernst: **always** · Herkomst: transfer · en: `outline-plan-left-in-body`

Een zin die beschrijft wat een sectie zou bevatten, geleverd in plaats van die inhoud: "In deze sectie zou worden ingegaan op mogelijke ontwikkelingen", "Hier komt nog een beschrijving van het bestuur". De opzet van het model is blijven staan waar de tekst had moeten komen. Schrijf de sectie of haal de kop weg.

Signalen: `In deze sectie zou worden ingegaan op` · `Hier zou een beschrijving komen van` · `Hier komt nog` · `Dit hoofdstuk behandelt straks` · `nader uit te werken` · `nog aan te vullen`

Voor: In deze sectie zou worden ingegaan op mogelijke ontwikkelingen in de energiemarkt.

Na: Het IEA legt de piek in de olievraag bij ongewijzigd beleid tussen 2029 en 2032 (World Energy Outlook 2025).

Niet markeren: Een werkdocument of een openbaar concept mag "nog aan te vullen" dragen als de status van het document dat zegt. In een projectplan is "nader uit te werken" een normale bestuurlijke formulering over toekomstig werk, geen restant.

### Plaatshouder in een gestructureerd veld `placeholder-in-metadata-field`

Ernst: **always** · Herkomst: transfer · en: `placeholder-in-metadata-field`

Een bron-, infobox- of frontmatterveld draagt een stomp in plaats van een waarde: "url=URL", "BRON_URL_HIER", "uitgever=UITGEVER", "datum=onbekend". Datumstompen als "2025-XX-XX" horen hier ook bij; ze duiken vooral op in geraadpleegd-op en veroorzaken gereedschapsfouten. Vul het veld of haal de hele verwijzing weg, want een bron die niet naar iets wijst onderbouwt niets.

Signalen: `geraadpleegd op 2025-XX-XX` · `url=URL` · `BRON_URL_HIER` · `uitgever=UITGEVER` · `titel=Titel` · `datum=onbekend`

Voor: {{Citeer web |url=BRON_URL_HIER |uitgever=UITGEVER |datum=2022-11-XX}}

Na: (de verwijzing is weggehaald; er is nooit iets geraadpleegd)

Niet markeren: Documentatie over een sjabloon toont de veldnamen met een voorbeeldwaarde; dat is de bedoeling. Een echte bron met een onbekende datum hoort het veld leeg te laten in plaats van er "onbekend" in te zetten, maar dat is een stijlkeuze, geen machinespoor.

### Gelekte redeneerstappen `reasoning-chain-leak`

Ernst: **always** · Herkomst: transfer · en: `reasoning-chain-leak`

De denksteiger van het model is als proza blijven staan: "Laten we dit stap voor stap bekijken", "Om dit systematisch aan te pakken", genummerde stappen die als innerlijke monoloog lezen in plaats van als betoog. Een subvorm vertelt de eigen werkwijze in plaats van een bron te noemen ("Mijn analyse is gebaseerd op de beschikbare titels"). Houd de conclusie met haar onderbouwing en haal de steiger weg.

Signalen: `Laten we dit stap voor stap bekijken` · `Laat me dit stap voor stap doorlopen` · `Om dit systematisch aan te pakken` · `Ik ontleed dit even` · `Mijn gedachtegang` · `Laten we eerst kijken naar` · `Mijn analyse is gebaseerd op`

Voor: Laten we dit stap voor stap bekijken. Kijk eerst naar het schrijfpad. De cache wordt bij elke schrijfactie ongeldig gemaakt.

Na: De cache wordt bij elke schrijfactie ongeldig gemaakt.

Niet markeren: Een handleiding of installatiegids mag "Stap 1" en "Stap 2" als koppen dragen; dat is de vorm van het stuk. Een didactisch artikel dat de lezer echt meeneemt door een berekening is ook geen restant, zolang de stappen voor de lezer zijn geschreven en niet voor de schrijver.

### Niet-ingevulde plaatshouder `unfilled-placeholder`

Ernst: **always** · Herkomst: transfer · en: `unfilled-placeholder`

Een invulplek die de schrijver had moeten vervangen, gepubliceerd zoals hij is. Subvormen: plaatshouders tussen blokhaken ("[jouw naam]", "[bedrijfsnaam]", "[datum]", "[link naar bron]"), instructies tussen haken ("[beschrijf hier het onderdeel]", "(vul hier je kanaal-URL in)"), een openstaande takenmarkering ("TODO :") en vulmateriaal als "Lorem ipsum" of "XYZ". Vul de waarde in of schrap de regel.

Signalen: `[naam invullen]` · `[jouw naam]` · `[bedrijfsnaam]` · `[datum]` · `[link naar bron]` · `[vul hier in]` · `(vul hier je kanaal-URL in)` · `[functietitel]` · `[plaats]` · `[voorbeeld toevoegen]` · `TODO :` · `Lorem ipsum`

Voor: Neem contact op met [naam contactpersoon] via [e-mailadres] voor meer over de meetup op [datum].

Na: Vragen over de meetup van 24 september gaan naar hallo@voorbeeld.nl.

Niet markeren: Een sjabloonbestand dat bedoeld is om ingevuld te worden hoort deze haken te dragen; markeer alleen gepubliceerde tekst. Blokhaken in een citaat markeren een toevoeging van de citeerder ("[de gemeente] besloot") en zijn correct. Een TODO in broncode of in een takenlijst is geen publicatiefout.

### Spatie- en plakresten uit het chatvenster `paste-whitespace-residue-nl`

Ernst: **cluster** · Herkomst: nl-bron

Witruimte die niet uit een toetsenbord komt maar uit het kopieren: dubbele spaties midden in een zin, een of meer spaties aan het begin van een regel of zin, en een spatie voor een leesteken. Ze ontstaan doordat een chatvenster zijn eigen opmaak meestuurt en het doelveld die niet opruimt. Op zichzelf zwak, in combinatie met andere plakresten een goede aanwijzing om de ruwe tekst na te kijken.

Signalen: `extra spaties aan het begin van een nieuwe zin of regel` · `twee spaties tussen twee woorden` · `een spatie voor de komma of de punt` · `onterechte spaties`

Voor: De inloop begint om 19.00 uur  en de eerste talk om 19.30 uur .

Na: De inloop begint om 19.00 uur en de eerste talk om 19.30 uur.

Niet markeren: In code, in een codeblok, in tabellen en in uitgelijnde configuratiebestanden is meervoudige witruimte betekenisdragend. Franse typografie zet een spatie voor de dubbele punt en het uitroepteken, dus in geciteerd Frans klopt het. Een enkele dubbele spatie na een punt is bij oudere schrijvers een gewoonte uit het typemachinetijdperk.

### Rollenspel-regieaanwijzingen `roleplay-action-markers`

Ernst: **cluster** · Herkomst: transfer · en: `roleplay-action-markers`

Regieaanwijzingen tussen sterretjes uit rollenspelchat zijn in het proza blijven staan: *knikt*, *zucht*, *haalt zijn schouders op*. De frase erbinnen opent met een handelingswerkwoord in de derde persoon, en dat onderscheidt hem van gewone cursivering. Twee of meer in een document is de drempel, want een enkel paar sterretjes kan markdown-cursief zijn.

Signalen: `*knikt*` · `*zucht*` · `*lacht*` · `*knikt bedachtzaam*` · `*haalt zijn schouders op*` · `*leunt naar voren*`

Voor: *knikt bedachtzaam* De migratie liep schoon.

Na: De migratie liep schoon.

Niet markeren: In een toneeltekst, een scenario of een chatlog dat je citeert zijn regieaanwijzingen de vorm van het genre. Een los paar sterretjes rond een woord is markdown-cursief; pas bij twee of meer handelingsaanwijzingen in hetzelfde stuk is het een restant.

### Eigen verklaring dat het aan de regels voldoet `self-certification-of-compliance`

Ernst: **cluster** · Herkomst: transfer · en: `self-certification-of-compliance`

De tekst beweert zijn eigen neutraliteit, bronvastheid of regelconformiteit in plaats van die te laten zien: "Neutraal van toon en overal gebrond", "voldoet aan de richtlijnen", "Ik begrijp je zorgen over AI-gegenereerde tekst". In een bewerkingssamenvatting stapelt dezelfde zet uitvoerige, niet-specifieke verzekeringen. Laat de tekst het werk doen en schrap de verklaring.

Signalen: `Neutraal van toon` · `voorzien van betrouwbare bronnen` · `in lijn met de richtlijnen` · `voldoet aan de richtlijnen` · `geschreven volgens de huisstijl` · `Ik begrijp je zorgen over` · `conform de geldende regels`

Voor: Sectie herzien voor helderheid en conform de richtlijnen; promotionele formuleringen gecorrigeerd en bronvermelding en neutraliteit verbeterd.

Na: overbodige links weggehaald

Niet markeren: In een auditrapport, een aanbesteding of een compliancedocument is "voldoet aan de richtlijnen" de kern van de mededeling en hoort er een verwijzing bij welke richtlijn. De tell is de losse verzekering zonder norm, in een tekst die er verder niets mee doet.

### Verouderde of onmogelijke sjabloonmetadata `stale-boilerplate-metadata`

Ernst: **cluster** · Herkomst: transfer · en: `stale-boilerplate-metadata`

Een nieuw document draagt metadata die het niet verdiend kan hebben: een onderhouds- of stijlsjabloon met een datum van voor het bestaan van het document, een inzendkop die de inzending alvast afwijst, of een geraadpleegd-op-datum die niet kan kloppen. Het model kopieert de vorm inclusief een datum die het uit zijn trainingsmateriaal kent. Zet de datum op de dag van aanmaak of haal het sjabloon weg.

Signalen: `{{Wikify|datum=september 2022}} op een pagina van 2026` · `{{Beginnetje}}` · `|bezochtdatum=12 december 2024` · `|datum=februari 2025 op een nieuw artikel` · `{{Meebezig}}`

Voor: Een pagina die in februari 2026 is aangemaakt en opent met {{Wikify|datum=september 2022}}

Na: Een pagina die in februari 2026 is aangemaakt en opent met {{Wikify|datum=februari 2026}}

Niet markeren: Een oud artikel dat al jaren een onderhoudssjabloon draagt hoort die oude datum te hebben. Een geraadpleegd-op-datum in het verleden is normaal bij een bron die eerder is nagekeken; de tell is dat de datum ouder is dan het document zelf.

### Sjabloonmatige wijzigingsnotitie `templated-change-note`

Ernst: **cluster** · Herkomst: transfer · en: `templated-change-note`

Een wijzigingsbeschrijving (commitbericht, PR-tekst, bewerkingssamenvatting) geschreven als uitputtend procedureel proza in plaats van een korte notitie. Subvormen: de volzin die alles opsomt wat er is gedaan en hoe het aan de regels voldoet, en de mededeling wat er bewust niet is veranderd, die de beperking uit de opdracht terugkaatst. Schrijf op wat er veranderde, in zo min mogelijk woorden.

Signalen: `Verbeterde duidelijkheid, structuur en leesbaarheid` · `Herzien voor betere leesbaarheid` · `met behoud van de oorspronkelijke betekenis` · `Uitgebreide herschrijving:` · `zonder de inhoud te wijzigen` · `Toon en stijl gelijkgetrokken`

Voor: Verbeterde duidelijkheid, structuur en leesbaarheid van de plotsectie; herhaling teruggebracht en toon aangescherpt voor een betere encyclopedische stijl.

Na: plot ingekort

Niet markeren: Een release-aankondiging of changelog voor gebruikers mag uitleggen wat er beter is geworden. In een refactorcommit is "zonder gedragswijziging" een nuttige en precieze mededeling; de tell is de opgestapelde, niet-specifieke opsomming.

### Briefregister waar geen brief hoort `letter-register-on-non-correspondence`

Ernst: **context** · Herkomst: transfer · en: `letter-register-on-non-correspondence`

Zakelijk briefformaat op een ticket, een overlegpagina, een reactie, een formulier of in een artikel: een onderwerpregel boven lopende tekst, een aanhef ("Geachte redactie"), beleefdheidsformules over goede bedoelingen en een groet aan het eind. Het register klopt in een echte brief; de tell is dat het opduikt waar niemand brieven schrijft, en het reist meestal samen met niet-ingevulde plaatshouders. De sterkste Nederlandse variant is "Ik hoop dat dit bericht u in goede gezondheid bereikt", een letterlijke vertaling van "I hope this message finds you well" die in spontaan Nederlands niet bestaat.

Signalen: `Onderwerp:` · `Geachte heer/mevrouw,` · `Geachte redactie,` · `Beste redactie` · `Ik hoop dat dit bericht u in goede gezondheid bereikt` · `Ik schrijf u om` · `Bij dezen verzoek ik u` · `Alvast dank voor uw begrip en medewerking` · `Bij voorbaat dank voor uw tijd` · `Met vriendelijke groet,` · `Hoogachtend,`

Voor: Geachte redactie, ik hoop dat dit bericht u in goede gezondheid bereikt. Bij dezen verzoek ik u een aanpassing door te voeren in het lemma.

Na: In de tweede alinea staat 1932 als oprichtingsjaar. De akte is van 1924.

Niet markeren: In een echte brief of formele mail zijn "Geachte heer" en "Met vriendelijke groet" precies goed; markeer alleen vlakken die geen correspondentie zijn. Een sollicitatiebrief, een bezwaarschrift of een brief aan de gemeente die in een artikel wordt geciteerd houdt zijn aanhef. "Onderwerp:" is in een mailclient een veld, geen tekstregel.

### Markdown op een vlak dat het niet rendert `markdown-in-non-markdown-surface`

Ernst: **context** · Herkomst: transfer · en: `markdown-in-non-markdown-surface`

Markdown-tekens blijven zichtbaar omdat het doelsysteem ze niet omzet: sterretjes rond woorden, hekjes voor koppen, streepjeslijnen, pijptabellen of een codeblok in een e-mail, een CMS-veld, een wiki of een commitbericht. Chatbots leveren standaard markdown af omdat hun systeemprompt daarom vraagt, en plakken houdt dat vast. Zet het om naar de opmaak van het doel, of haal het weg.

Signalen: `**vet** dat als sterretjes blijft staan` · `## voor een kop` · `--- als scheidingslijn` · `| kolom | kolom | in platte tekst` · `` ```bash in een e-mail `` · `[programma] (https://devmeetup.nl/programma) in een wiki` · `markdown vermengd met de opmaaktaal van het doelsysteem`

Voor: ## Programma

- **19:00** inloop
- **19:30** eerste talk

Na: Programma: 19.00 uur inloop, 19.30 uur de eerste talk.

Niet markeren: Op een markdown-bestand, in een README of in een chatvenster dat markdown rendert geeft deze regel per definitie vals alarm; draai hem alleen op vlakken die markdown niet omzetten. Ontwikkelaars, onderzoekers en technisch schrijvers gebruiken markdown overal, dus op zichzelf is het zwak bewijs. Sterk wordt het pas als markdown zich vermengt met de opmaaktaal van het doelsysteem, of als een heel antwoord inclusief codeblok is geplakt.

### Herkomstsignalen buiten de tekst `out-of-text-provenance-signal`

Ernst: **context** · Herkomst: transfer · en: `out-of-text-provenance-signal`

Aanwijzingen over hoe de tekst is aangekomen in plaats van hoe hij leest: het hele document dat in de versiegeschiedenis als een enkele plakactie verschijnt, en een auteur die plotseling foutloos of formeel schrijft tegen zijn eigen basislijn in, zeker als die basislijn van voor eind 2022 is. Zulk procesbewijs is beter verdedigbaar dan een detectorscore. Het is op zichzelf nooit een reden om de tekst te wijzigen; het is een reden om te vragen.

Signalen: `2000 woorden in een enkele bewerking geplakt` · `account dat verder alleen tweeregelige bewerkingen doet` · `stijlsprong tegen de eigen basislijn in`

Voor: Een sectie van 2000 woorden arriveert in een plakactie, vanaf een account dat verder alleen bewerkingen van twee regels doet.

Na: (geen tekstwijziging; de auteur is gevraagd hoe de sectie tot stand kwam)

Niet markeren: Iemand die offline schrijft en het resultaat in een keer plakt doet niets verkeerds; dat is normale werkwijze. Een auteur die beter gaat schrijven na een cursus of met een spellingcontrole is geen bewijs. Gebruik dit signaal om een vraag te stellen, nooit om een verwijt te onderbouwen.

## Translationese: Engelsvormig Nederlands

### Bij merknaam begrijpen we `at-brand-we-understand-nl`

Ernst: **always** · Herkomst: translationese

De tekst opent met een merk dat zichzelf empathie toeschrijft, letterlijk uit At X, we understand. De geclaimde empathie staat zonder inhoud, meestal in de eerste zin van een bedrijfspagina.

Signalen: `Bij [merknaam] begrijpen we` · `Bij ons geloven we` · `Wij bij` · `Bij X weten we hoe belangrijk` · `Wij begrijpen als geen ander`

Voor: Bij Webgrip begrijpen we hoe belangrijk snelheid is.

Na: Een trage build kost ons twintig minuten per release. Daarom doen we dit.

Niet markeren: Een merk dat zijn eigen ervaring beschrijft en met een feit onderbouwt valt hier niet onder, en 'bij ons weten we dat' in een gespreksverslag is gewoon Nederlands. Het signaal is de geclaimde empathie zonder inhoud.

### Meer dan alleen X `beyond-mere-escalation`

Ernst: **always** · Herkomst: translationese · en: `beyond-mere-escalation`

Een opwaardering midden in de zin verheft het onderwerp door een kleinere versie ervan weg te wuiven: meer dan alleen een meetup, verder dan louter techniek, niet zomaar een tool. Leenvertaling van beyond mere X en more than just X. Het beweert belang in plaats van het te tonen, en het tweede lid is meestal vager dan het eerste.

Signalen: `meer dan alleen` · `meer dan zomaar` · `verder dan louter` · `niet zomaar een` · `meer dan slechts` · `het is niet X, het is Y` · `X, geen Y als slogan-opener` · `niet omdat X, maar omdat Y`

Voor: Dit is meer dan alleen een meetup.

Na: Bij deze meetup horen ook een workshop en een vacaturebord.

Niet markeren: 'Meer dan alleen' is in een gewone vergelijking correct Nederlands ('het kost meer dan alleen tijd') en staat daarom niet in de regex; alleen de opwaarderende vorm aan het begin van een claim telt. Overlapt met het negatief parallellisme onder syntax, waar het contrastbinair (het is niet X, het is Y; de slogan-opener X, geen Y) zijn eigen entry heeft; markeer één keer.

### Duiken en delven in een onderwerp `calque-dive-in-nl`

Ernst: **always** · Herkomst: nl-bron

Een onderwerp wordt 'ingedoken' of 'in gedolven', letterlijk uit dive into en delve into. In het Nederlands duik je in water, zelden in een tekst. Subvormen: de opening 'laten we erin duiken', de kop 'een diepe duik in', en het aangekondigde 'laten we ons verdiepen in'.

Signalen: `Laten we erin duiken` · `laten we duiken in` · `we duiken dieper in` · `een diepe duik in` · `delven in` · `laten we ons verdiepen in` · `een deep dive` · `Duik in de wereld van`

Voor: Laten we erin duiken en de mogelijkheden verkennen.

Na: De drie opties staan hieronder, met wat elke optie kost.

Niet markeren: Gewoon Nederlands bij duiksport en letterlijk water, en in oudere vaste uitdrukkingen als 'de boeken in duiken' of 'het archief in duiken'. 'Zich verdiepen in' is normaal Nederlands en pas een signaal in de aankondigende vorm 'laten we ons verdiepen in'.

### Landschap-, reis- en ecosysteemmetafoor `calque-landscape-journey-nl`

Ernst: **always** · Herkomst: nl-bron

Het onderwerp krijgt een Engelse ruimtemetafoor: een landschap waar je doorheen beweegt, een reis die je aflegt, een ecosysteem waar je deel van bent. De metafoor draagt geen informatie en dekt elk onderwerp even goed. Landschap is in de Nederlandse detectiepraktijk het meest gemelde AI-woord: bijna altijd met huidige, dynamische, complexe of veranderende ervoor, en bijna altijd in de eerste zin. Schrappen kan meestal zonder vervanging; anders noem je de markt, de sector of de club waar het over gaat.

Signalen: `in dit snel veranderende landschap` · `een veranderend landschap` · `het AI-landschap` · `een dynamisch landschap` · `de reis van` · `jouw AI-reis` · `het ecosysteem` · `in ons huidige dynamische tijdperk` · `in het huidige landschap` · `het huidige medialandschap` · `navigeren door het landschap` · `het complexe AI-landschap` · `het digitale landschap`

Voor: In het huidige landschap is de digitale reis van elke organisatie anders.

Na: Elk bedrijf begint hier op een ander punt.

Niet markeren: 'Landschap' is gewoon Nederlands in aardrijkskunde en beeldende kunst, en in vaste termen als medialandschap en onderwijslandschap, die ouder zijn dan de modellen. 'Reis' is normaal bij een echte reis en bij 'klantreis' als vakterm met een gedefinieerde betekenis. 'Ecosysteem' hoort thuis in de biologie en in software waar het een afgebakende verzameling koppelingen aanduidt. Landschap in de letterlijke zin (het Twentse landschap, landschapsbeheer, een landschapsschilder) is gewoon Nederlands en komt in regionale teksten veel voor. Alleen de figuurlijke koppeling aan een markt, sector of vakgebied telt.

### Letterlijk vertaalde Engelse uitdrukkingen en discoursformules `calqued-idiom-nl`

Ernst: **always** · Herkomst: nl-bron

Een Engelse vaste uitdrukking wordt woordelijk vertaald en levert een zin op die grammaticaal klopt en in Nederlandse spraak niet bestaat: de olifant in de kamer, buiten de doos denken, op dezelfde pagina zitten, de bal ligt bij jou. Daar horen de gespreksformules bij die uit Engelse spraak komen: aan het eind van de dag, dat gezegd hebbende, maak geen vergissing, in alle eerlijkheid. Ook valse vrienden vallen eronder, zoals 'eventueel' voor eventually en 'actueel' voor actually.

Signalen: `aan het eind van de dag` · `aan het einde van de dag` · `dat gezegd hebbende` · `maak geen vergissing` · `het is wat het is` · `in alle eerlijkheid` · `aan de andere kant` · `de olifant in de kamer` · `buiten de doos denken` · `buiten de kaders denken` · `op de radar` · `de bal ligt bij jou` · `een win-winsituatie` · `het beste van beide werelden` · `op dezelfde pagina zitten` · `aan boord zijn` · `de onderste regel` · `op een dagelijkse basis`

Voor: Laten we de olifant in de kamer benoemen: de bal ligt bij jou.

Na: Het punt dat niemand aansnijdt is dat jij nu aan zet bent.

Niet markeren: 'Aan het einde van de dag' is gewoon Nederlands als het letterlijk over het einde van een werkdag gaat, en 'het is wat het is' en 'win-winsituatie' zijn in spreektaal doorgedrongen. 'Buiten de gebaande paden treden' is een oude Nederlandse uitdrukking en geen calque. Losse anglicismen in vaktaal (deployen, commit, stack) horen hier niet.

### Beeldspraak en waardeclaims zonder Nederlandse traditie `calqued-imagery-nl`

Ernst: **always** · Herkomst: translationese

Nederlandse woorden staan in een betekenis die alleen in het Engels bestaat: een baken van hoop, het rijke tapijt van de gemeenschap, een testament aan vakmanschap, een symfonie van kleuren, resoneert met de lezer. Dezelfde familie levert de vaste waardeformules: de sleutel tot, een gamechanger, een lichtend voorbeeld van. Het beeld is een letterlijke vertaling en heeft in het Nederlands geen traditie.

Signalen: `baken van hoop` · `een baken van` · `in de diepten van` · `een standvastige toewijding` · `hubs van` · `lichtend voorbeeld van` · `tapestry` · `het rijke tapijt van` · `testament aan` · `een testament van` · `realm` · `een symfonie van` · `symboliseert` · `resoneert met` · `weerspiegelt` · `de sleutel tot` · `naar nieuwe hoogten`

Voor: Dit draagt bij aan het rijke tapijt van de gemeenschap.

Na: Hier komen mensen uit de hele regio op af.

Niet markeren: 'Weerspiegelen' is normaal Nederlands voor een spiegelbeeld en voor cijfers die iets laten zien, 'resoneren' is een natuurkundige term, 'testament' is een juridisch document en 'baken' is een navigatiemiddel. In poëzie en literaire tekst is beeldspraak het middel zelf. Het signaal is het figuurlijke gebruik in een gewone zakelijke of journalistieke zin.

### Engelse getal-, datum- en tijdnotatie `english-number-date-format-nl`

Ernst: **always** · Herkomst: translationese

Cijfers, datums, tijden, bedragen en eenheden staan in Amerikaanse notatie in een Nederlandse zin: punt als decimaalteken, komma als duizendtalscheiding, maand voor dag, klokstanden met AM of PM, dollars en Fahrenheit. Daarbij hoort de hoofdletter op maandnamen, weekdagen, functietitels en vakgebieden, die het Nederlands klein schrijft. Beide vormen overleven vaak een redactieronde omdat ze op een stijlkeuze lijken.

Signalen: `3.5 waar 3,5 hoort` · `1,000 waar 1.000 hoort` · `September 5, 2026` · `12/05/2026 in Amerikaanse volgorde` · `July 4, 2026 in een Nederlandse zin` · `2:30 PM` · `$1,200` · `70°F` · `10 miles` · `Maandag met een hoofdletter midden in de zin` · `Januari` · `onze Marketing Manager` · `Machine Learning in lopende tekst`

Voor: Op September 5, 2026 kwamen 1,250 bezoekers; de opkomst steeg met 3.5 procent.

Na: Op 5 september 2026 kwamen 1.250 bezoekers en de opkomst steeg met 3,5 procent.

Niet markeren: In code, versienummers, tabellen uit een Engelstalige bron en geciteerde Engelse tekst is de Amerikaanse notatie correct, net als in meetdata uit Engelstalige tooling. Hoofdletters horen wel aan het zinsbegin, bij eigennamen, in een aanhef of ondertekening en bij merknamen; talen en nationaliteiten krijgen in het Nederlands juist een hoofdletter. De hoofdlettervariant is met een hoofdletterongevoelige scanner niet te vangen en vraagt een lezer.

### Engelse stam met Nederlandse vervoeging `english-stem-dutch-inflection-nl`

Ernst: **always** · Herkomst: translationese

Een Engels werkwoord wordt Nederlands vervoegd terwijl er een gangbaar Nederlands werkwoord bestaat, of terwijl de vorm in het Nederlands helemaal niet bestaat: superchargeer, leveragen, unlocken, empoweren, gedisrupt, gecraft. Het is de morfologische variant van het onvertaalde leenwoord.

Signalen: `superchargeer` · `leveragen` · `unlocken` · `empoweren` · `geleveraged` · `gedisrupt` · `onboarden` · `gecraft`

Voor: Superchargeer je online aanwezigheid en leverage je data.

Na: Zorg dat mensen je site vinden en gebruik de cijfers die je al hebt.

Niet markeren: Ingeburgerde Engelse werkwoorden met Nederlandse vervoeging zijn gewoon Nederlands: mailen, downloaden, deployen, mergen, updaten, rebasen. Het signaal is de vervoeging van een marketingwerkwoord met een gangbaar Nederlands equivalent.

### Echter aan het zinsbegin met komma `free-conjunction-clause-linking`

Ernst: **always** · Herkomst: translationese · en: `free-conjunction-clause-linking`

Een tegenstellend of optellend bijwoord opent de zin met een komma erachter, naar het Engelse However, en Nevertheless,. Het Nederlands zet echter in de zin met inversie, of laat de komma weg. Dezelfde beweging plakt hoofdzinnen los aan elkaar met 'en' waar het Nederlands zou onderschikken.

Signalen: `Echter,` · `Desalniettemin,` · `Bovendien,` · `Daarnaast,` · `Uiteindelijk,` · `Ten slotte,` · `Sterker nog,` · `Bovenal,`

Voor: Echter, de resultaten vielen tegen.

Na: De resultaten vielen echter tegen.

Niet markeren: Een komma hoort wel na een langere bijwoordelijke aanloop met inversie erachter, en na 'Kortom' en 'Met andere woorden', die in het Nederlands wel een komma krijgen. In geciteerde spraak en in oudere teksten komt de komma na 'Echter' voor als eigen stijl. Het signaal is de combinatie van komma en Engelse woordvolgorde.

### Hier is waarom en Dit is hoe `here-is-why-nl`

Ernst: **always** · Herkomst: nl-bron

Een aankondigende overgangszin uit het Engels: Here's why, Here's how, This is why, Here's what you need to know. In spontaan Nederlands bestaan deze vormen niet; daar staat 'daarom', 'zo werkt het' of gewoon de bewering zelf. Dezelfde familie levert de opgesplitste pointe: het punt is dit, laten we het opsplitsen, en dat is precies waarom.

Signalen: `Hier is waarom` · `Hier is hoe` · `Hier is wat je moet weten` · `Dit is waarom` · `Dit is hoe` · `Hier komt het` · `Het punt is dit` · `En dat is precies waarom` · `Dit is wat het betekent`

Voor: Hier is waarom dat belangrijk is.

Na: Dat is belangrijk omdat de build dan twee keer draait.

Niet markeren: 'Daarom' en 'Zo werkt het' zijn de Nederlandse vormen en geen signaal. In ondertiteling en in weergegeven spraak kan de directe vorm voorkomen, en in een letterlijk citaat blijft hij staan.

### Je en u door elkaar `honorific-register-drift`

Ernst: **always** · Herkomst: translationese · en: `honorific-register-drift`

Binnen één tekst, soms binnen één alinea, wisselt de aanspreekvorm tussen je en u, omdat het Engelse you geen keuze afdwingt en het model per zin opnieuw kiest. De wissel is in het Nederlands extra zichtbaar omdat ook de bezittelijke vorm meebeweegt: jouw naast uw. Het scherpst zichtbaar tussen de lopende tekst en de knop, het formulier of de bevestigingsmail eronder.

Signalen: `je … uw` · `jouw … u` · `u kunt je aanmelden` · `'Meld je aan' onder een tekst die 'u' gebruikt` · `uw organisatie … jouw situatie` · `gebiedende wijs in de verkeerde beleefdheidsvorm`

Voor: Je meldt je aan via de site. Vervolgens ontvangt u een bevestiging per e-mail.

Na: Je meldt je aan via de site en krijgt daarna een bevestiging per mail.

Niet markeren: Sommige merken hanteren bewust 'u' in juridische teksten en 'je' in marketing; dat is beleid en geen fout, zolang de scheiding per tekst loopt. In dialoog en geciteerde spraak wisselt de aanspreekvorm per spreker. Ook een tekst die 'u' gebruikt en een aangehaalde knoptekst met 'je' toont, is geen signaal.

### In termen van `in-terms-of-frame`

Ernst: **always** · Herkomst: translationese · en: `in-terms-of-frame`

Het frame 'in termen van' leidt een onderwerp of domein in, als letterlijke weergave van in terms of, when it comes to en with respect to. Het Nederlands gebruikt daar een gewoon voorzetsel, een onderwerpszin, of laat het frame weg. Eén voorkomen is genoeg, anders dan bij de zwaardere voorzetselomschrijvingen die op dichtheid gepoort worden.

Signalen: `in termen van` · `als het gaat om` · `wanneer het aankomt op` · `wat betreft`

Voor: In termen van snelheid scoort deze aanpak goed.

Na: Deze aanpak is sneller.

Niet markeren: 'Wat betreft', 'qua' en 'als het gaat om' zijn gewoon Nederlands en staan bewust niet in de regex. In wiskunde en logica is 'in termen van' een vakterm ('uitgedrukt in termen van x'), en daar is het correct.

### Engelse brok midden in Nederlandse tekst `language-switch-mid-text-nl`

Ernst: **always** · Herkomst: nl-bron

Een zin, kop, opsommingsonderdeel of antwoord staat plotseling in het Engels, als rest van de Engelse generatie eronder. Het gaat om de onaangekondigde wissel in lopende tekst, meestal in een overgangszin of de laatste alinea, en om een Engels antwoord op een Nederlandse vraag.

Signalen: `Here's the thing` · `In conclusion` · `In short` · `Note that` · `Overall` · `The honest answer` · `What nobody tells you` · `Engelse kop boven Nederlandse tekst` · `één Engelse bullet in een Nederlandse lijst` · `Engels antwoord op een Nederlandse vraag` · `de ene zin Nederlands, de andere Engels` · `rare afkap`

Voor: De drie stappen zijn helder. Here's the thing: de laatste kost het meeste tijd.

Na: De drie stappen zijn helder. De laatste kost het meeste tijd.

Niet markeren: Citaten, songteksten, productnamen, foutmeldingen, code en Engelstalige eigennamen horen in het Engels te blijven. In een tweetalige tekst of een expliciet Engelse sectie is de wissel aangekondigd en dus geen signaal.

### Letterlijk vertaalde lichte werkwoorden `light-verb-literalism`

Ernst: **always** · Herkomst: translationese · en: `light-verb-literalism`

Een Engelse constructie met een licht werkwoord wordt woord voor woord overgezet: make a decision wordt een beslissing maken in plaats van nemen, make an impact wordt impact maken, take a picture wordt een foto nemen, have a good understanding wordt een goed begrip hebben van. Breng het paar terug tot het werkwoord dat in het zelfstandig naamwoord verstopt zit.

Signalen: `een beslissing maken` · `impact maken` · `een punt maken` · `geld maken` · `sense maken` · `een foto nemen` · `een kans nemen` · `een goed begrip hebben van` · `een sterke focus hebben op`

Voor: Het team maakt een beslissing over de datum en wil impact maken.

Na: Het team kiest de datum en wil dat het iets oplevert.

Niet markeren: 'Een foto maken' en 'een beslissing nemen' zijn de Nederlandse vormen; het gaat om de omgekeerde koppeling. In Vlaamse spreektaal komt 'een foto nemen' voor als eigen variant, dus let op de variëteit van de schrijver. Vakjargon met een vaste vorm ('een beslissing forceren' in schaken) valt erbuiten.

### Geen inversie na een aanloop `missing-inversion-after-fronting-nl`

Ernst: **always** · Herkomst: translationese

Na een aanloop blijft het onderwerp voor het werkwoord staan, zoals in het Engels: 'In dit artikel, we bespreken drie manieren.' Het Nederlands vraagt op die plek de omgekeerde volgorde. De tweede vorm is de losse deelwoordaanloop uit Based on, Given en Considering: gebaseerd op, kijkend naar, rekening houdend met, gevolgd door een komma en rechte volgorde.

Signalen: `In dit artikel, we bespreken` · `In 2024, we lanceerden` · `Na de update, het werkt` · `Volgens de onderzoekers, het model is` · `Gebaseerd op` · `Gezien het feit dat` · `Rekening houdend met` · `Kijkend naar` · `Sprekend over` · `Voortbouwend op`

Voor: Na de storing, we hebben de retries uitgezet.

Na: Na de storing hebben we de retries uitgezet.

Niet markeren: Geen tell in geciteerde spreektaal, in poëzie en in dialect, waar de volgorde bewust afwijkt, en niet bij een losse aanroep of tussenwerpsel ('Nou, dat viel mee'). 'Gelet op' en 'Gezien' zijn correct Nederlands als voorzetsel, zonder komma en met inversie erachter.

### Engelse ziekte: samenstellingen los of met een streepje `noun-stacking-particle-drop`

Ernst: **always** · Herkomst: translationese · en: `noun-stacking-particle-drop`

Een Nederlandse samenstelling wordt met spaties geschreven omdat het Engelse origineel uit losse woorden bestaat, of er komt een streepje waar het woord aaneen hoort: 'content marketing bureau', 'lange termijn strategie', 'data gedreven', 'klant tevredenheid onderzoek'. Een tweede vorm is de kale naamwoordstapel zonder het voorzetsel dat de relatie legt ('AI technologie ontwikkeling snelheid'). Een derde vorm is de onvertaalde Engelse streepvorm in naamwoordelijk gebruik ('het rapport is high-quality', 'werkt out-of-the-box').

Signalen: `content marketing bureau` · `data analyse` · `klant ervaring` · `klant tevredenheid onderzoek` · `AI gedreven` · `machine learning model` · `bronzen medaille winnaar` · `software ontwikkelaar` · `e-mail adres` · `lange termijn strategie` · `korte termijn oplossing` · `data gedreven` · `klant gerichte aanpak` · `gebruikers ervaring` · `project manager` · `markt onderzoek` · `kwaliteit controle` · `team lid` (+4)

Voor: Wij zijn een content marketing bureau met veel data analyse ervaring.

Na: Wij zijn een contentmarketingbureau met veel ervaring in data-analyse.

Niet markeren: Engelse productnamen die officieel los staan blijven los (Visual Studio Code, Machine Learning als vaknaam in een Engelse titel). Woordgroepen die geen samenstelling zijn ('een lange termijn' als zelfstandige woordgroep, 'de data die we analyseren') vallen erbuiten, en 'datagedreven' aaneen is gewoon Nederlands. In citaten en in code blijft de spelling zoals ze is.

### Gestapelde hulpwerkwoorden aan het zinseind `stacked-double-passive`

Ernst: **always** · Herkomst: translationese · en: `stacked-double-passive`

Drie of meer hulpwerkwoorden op één gezegde, meestal omdat een Engelse modale plus lijdende constructie hulpwerkwoord voor hulpwerkwoord is nagebouwd: zou moeten kunnen worden opgeleverd, zal moeten worden bekeken, had kunnen worden voorkomen. De lezer moet de hele eindgroep vasthouden voor hij weet wat er gebeurt.

Signalen: `zou moeten kunnen worden` · `zal moeten worden` · `had kunnen worden` · `zou kunnen worden gedaan` · `dient te kunnen worden`

Voor: Het rapport zou vóór maart moeten kunnen worden opgeleverd.

Na: We leveren het rapport vóór maart op.

Niet markeren: Twee hulpwerkwoorden ('kan worden gebruikt', 'moet worden bekeken') zijn gewoon Nederlands en horen niet in dit patroon; de regex begint pas bij drie. In wetgeving en normteksten is de zware eindgroep de gangbare vorm.

### Engelse titelhoofdletters in koppen `title-case-headings`

Ernst: **always** · Herkomst: nl-bron · en: `title-case-headings`

Een kop of tussenkop krijgt op bijna elk woord een hoofdletter, volgens de Engelse title case. Het Nederlands schrijft koppen als een zin: alleen het eerste woord en eigennamen krijgen een hoofdletter. Het sterkste teken is een hoofdletter op een functiewoord midden in de kop (En, Of, De, Van, Voor), en dezelfde vorm duikt op in menu-items, knoppen en tabbladen.

Signalen: `De Complete Gids Voor Moderne Marketing` · `Hoe Bedrijven Van AI Profiteren` · `De Vijf Belangrijkste Voordelen Van Dakisolatie` · `Zo Herken Je Een AI-Tekst` · `SEO Geheimen Onthuld` · `## Strategische Onderhandelingen En Wereldwijde Partnerschappen` · `## Belangrijke Punten En Aanbevelingen` · `hoofdletter op En/Of/De/Het/Van/Voor midden in een kop` · `elk woord in de titel met een hoofdletter` · `hoofdletters in menu-items, knoppen en tabbladen`

Voor: De Vijf Belangrijkste Voordelen Van Dakisolatie

Na: De vijf belangrijkste voordelen van dakisolatie

Niet markeren: Eigennamen, merk- en productnamen en aangehaalde Engelse titels houden hun eigen hoofdletters. Geen regex: de scanner draait met IGNORECASE en kan hoofdletters dus niet zien; dit patroon vraagt een hoofdlettergevoelige controle of een lezer. In het Nederlands bestaat geen genre waarin title case correct is, dus buiten citaten is een kop al genoeg.

### Abstract onderwerp met een kleurloos werkwoord `abstract-subject-all-purpose-verb`

Ernst: **cluster** · Herkomst: translationese · en: `abstract-subject-all-purpose-verb`

Drie mechanismen met dezelfde oorzaak: een abstract of levenloos onderwerp met een kleurloos werkwoord (dit onderzoek laat zien, het rapport biedt inzicht), de letterlijk overgezette Engelse causatief (X brengt risico's met zich mee, in plaats van door X ontstaan risico's), en denk- en spreekwerkwoorden met een niet-menselijk onderwerp (de data suggereert). Zet een mens of een organisatie terug als onderwerp, of noem de bron.

Signalen: `dit onderzoek laat zien` · `het rapport biedt inzicht` · `de data suggereert` · `brengt risico's met zich mee` · `zorgt ervoor dat` · `leidt ertoe dat` · `maakt het mogelijk om`

Voor: Dit onderzoek laat nieuwe mogelijkheden zien, en dit beleid bracht prijsstijgingen met zich mee.

Na: De onderzoekers vonden twee nieuwe toepassingen. Door dit beleid stegen de prijzen.

Niet markeren: 'Zorgt ervoor dat' en 'maakt het mogelijk om' zijn te gewoon voor een regex en staan er niet in; beoordeel die op dichtheid. In wetenschappelijk proza is 'het onderzoek laat zien' de vaste, correcte formulering. Overlapt bewust met inanimate-agent onder syntax: markeer één keer.

### Lijdende vorm met door-bepaling `agentive-by-passive`

Ernst: **cluster** · Herkomst: translationese · en: `agentive-by-passive`

De Engelse lijdende vorm met genoemde handelende persoon (generated by AI, used by many teams) wordt overgezet als een Nederlandse worden-passief met door-bepaling. De handelende partij staat er dus al en kan gewoon het onderwerp van een bedrijvende zin worden. Het signaal is de dichtheid, en de passief op een onderwerp dat een zin eerder gewoon genoemd is.

Signalen: `wordt gebruikt door` · `wordt aangedreven door` · `is gegenereerd door` · `werd gepubliceerd door` · `wordt beheerd door` · `is opgesteld door` · `is ontwikkeld door` · `kan worden bereikt` · `worden ingezet om`

Voor: De afbeelding is gegenereerd door een AI-model.

Na: Een AI-model maakte de afbeelding.

Niet markeren: De lijdende vorm met door-bepaling is correct Nederlands en in encyclopedische, historische en procedurele tekst de norm ('de kerk werd door Cuypers ontworpen'); een brede regex hierop markeert elke Wikipedia-zin. Daarom vangt de regex alleen de vaste AI-copyvormen. Beoordeel de rest op dichtheid binnen de alinea.

### Lijdende vorm zonder enige handelende partij `agentless-automated-passive`

Ernst: **cluster** · Herkomst: translationese · en: `agentless-automated-passive`

Een gebeurtenis wordt gemeld als iets dat is gebeurd, met een kleurloze lijdende vorm en zonder dat iemand het doet: er is overeenstemming bereikt, er wordt gewerkt aan, er is besloten. Anders dan bij de door-variant is de handelende partij helemaal verdwenen. De Nederlandse er-constructie vult de onderwerpsplek zonder iemand te noemen.

Signalen: `er is overeenstemming bereikt` · `er wordt gewerkt aan` · `er is besloten` · `er wordt gekeken naar` · `de norm is opgesteld` · `er wordt gesproken over`

Voor: Er is overeenstemming bereikt over de nieuwe norm.

Na: De twee partijen werden het eens over de nieuwe norm.

Niet markeren: In notulen, persberichten van overheden en procedurebeschrijvingen is de onpersoonlijke vorm de gangbare, en soms de enige eerlijke vorm als echt niet vaststaat wie iets deed. Het signaal is de vorm bij een gebeurtenis met een bekende partij, en de herhaling ervan door een hele tekst.

### Amerikaanse leestekenplaatsing en de Engelse bezitsapostrof `american-quote-and-genitive-nl`

Ernst: **cluster** · Herkomst: translationese

Twee Engelse leestekenregels lekken mee in Nederlandse tekst: de komma of punt gaat binnen het sluitende aanhalingsteken, en de bezitsvorm krijgt een apostrof waar het Nederlands er geen zet. Daarbij hoort de spiegelvorm: meervouden van afkortingen verliezen de apostrof die het Nederlands juist eist. Ook het door elkaar lopen van rechte en gekrulde aanhalingstekens hoort erbij, als rest van het kopiëren uit een chatvenster.

Signalen: `punt binnen het sluitende aanhalingsteken` · `komma binnen het sluitende aanhalingsteken` · `wisseling tussen rechte en gekrulde quotes` · `Peter's laptop` · `de klant's wensen` · `Peter's boek` · `APIs` · `URLs` · `KPIs` · `de 90s`

Voor: Hij noemde het “een goede avond,” en vertrok. Dat was Peter's idee.

Na: Hij noemde het ‘een goede avond’ en vertrok. Dat was Peters idee.

Niet markeren: Wel een apostrof bij namen en woorden op een klinkerletter ('Anna's boek', 'foto's', 'API's') en bij merknamen die officieel een apostrof dragen. De keuze tussen enkele en dubbele aanhalingstekens is een huisstijlkwestie en geen signaal; het gaat om de plaatsing van het leesteken en om het mengen van beide vormen in dezelfde tekst. Bij een volledige aangehaalde zin staat de punt in het Nederlands ook binnen het sluitteken.

### Letterlijk vertaalde Engelse marketingwerkwoorden `calqued-marketing-verbs-nl`

Ernst: **cluster** · Herkomst: translationese

Vier families werkwoorden komen woord voor woord uit het Engels en staan waar een gewoon Nederlands werkwoord hoort. Ontsluiten, ontgrendelen en ontketenen uit unlock, unleash en empower, met potentieel of mogelijkheden als lijdend voorwerp. Faciliteren, stroomlijnen, benutten, optimaliseren en maximaliseren uit facilitate, streamline, leverage en optimize. Transformeren, revolutioneren en superchargen uit de Engelse hyperbool, en navigeren, verkennen en omarmen uit navigate, explore en embrace.

Signalen: `ontsluit het potentieel` · `ontsluiten` · `ontgrendelen` · `empoweren` · `stelt je in staat om` · `de kracht van X ontketenen` · `de kracht van je data benutten` · `haal het maximale uit` · `een oplossing faciliteren` · `processen stroomlijnen` · `kansen benutten` · `optimaliseren` · `maximaliseren` · `transformeren` · `transformatief` · `revolutioneren` · `superchargeer` · `boosten` (+10)

Voor: Ontsluit nieuw groeipotentieel en til je marketing naar een hoger niveau.

Na: Met deze aanpak kreeg de vorige klant 30 procent meer aanvragen.

Niet markeren: Elk van deze werkwoorden is in zijn eigen betekenis correct Nederlands: een archief of gebied wordt ontsloten, een zaal of sessie wordt gefaciliteerd, ruimte wordt benut, een schip en een gebruikersinterface worden genavigeerd, terrein wordt verkend. Het signaal is het abstracte lijdend voorwerp (potentieel, mogelijkheden, kansen, landschap, uitdagingen) en de dichtheid. Bij een echte, gedateerde transformatie met bewijs erbij is 'transformeren' gewoon het juiste woord.

### Zware voorzetseluitdrukking als leenvertaling `calqued-preposition-periphrasis`

Ernst: **cluster** · Herkomst: translationese · en: `calqued-preposition-periphrasis`

Een Engelse voorzetselgroep wordt telkens met een zwaar omschrijvend frame weergegeven waar het Nederlands hetzelfde verband met één voorzetsel legt: about wordt met betrekking tot in plaats van over, through wordt door middel van in plaats van door of met, related to wordt gerelateerd aan, for the purpose of wordt ten behoeve van. Daar hoort de basis-en-manier-formule bij: op een dagelijkse basis, op een consistente manier. Elk frame is op zichzelf Nederlands, dus de tell is dichtheid: drie of meer in één alinea.

Signalen: `met betrekking tot` · `door middel van` · `op basis van` · `gerelateerd aan` · `in relatie tot` · `ten behoeve van` · `met het oog op` · `in het licht van` · `ten aanzien van` · `op een dagelijkse basis` · `op een consistente manier` · `op een tijdige manier`

Voor: Door middel van data-analyse kunnen wij, met betrekking tot de doorlooptijd, verbeteringen realiseren.

Na: Uit de data blijkt waar de doorlooptijd blijft hangen, en dat lossen we op.

Niet markeren: In juridische, ambtelijke en beleidsteksten zijn 'met betrekking tot', 'ten behoeve van' en 'ten aanzien van' de gangbare vormen en geen signaal; ze bestonden ruim voor de modellen. 'Op basis van' is normaal Nederlands en staat daarom niet in de regex. Markeer pas bij drie of meer in dezelfde alinea, of als de omweg één bijwoord vervangt.

### Die-dat-verwarring uit het Engelse that `die-dat-confusion-nl`

Ernst: **cluster** · Herkomst: translationese

Het betrekkelijk voornaamwoord klopt niet met het geslacht van het antecedent, omdat het Engels maar één vorm heeft en het model die op goed geluk overzet: het model die, de tool dat. Bij dezelfde oorzaak horen de kleine Nederlandse missers waar het Engels niet stuurt, zoals hetgeen wat en een komma op de verkeerde plek.

Signalen: `het model die` · `de tool dat` · `het bedrijf die` · `de organisatie dat` · `hetgeen wat` · `het systeem die`

Voor: Het model die de tekst genereert, kent geen Nederlands.

Na: Het model dat de tekst genereert, kent geen Nederlands.

Niet markeren: Nederlandse schrijvers maken deze fout ook, en in gesproken taal en dialect is de afwijking normaal, dus dit telt alleen mee samen met andere signalen uit deze laag. Bij verwijzing naar personen achter een het-woord ('het meisje die') is 'die' een aparte kwestie en geen vertaalfout.

### Gedreven en aangedreven door als achtervoegsel `driven-powered-suffix-nl`

Ernst: **cluster** · Herkomst: translationese

Het Engelse -driven en -powered worden productief als Nederlands achtervoegsel op elk zelfstandig naamwoord geplakt: AI-gedreven, resultaatgedreven, aangedreven door machine learning. Het sierwoord zegt niet wat er aandrijft.

Signalen: `AI-gedreven` · `datagedreven` · `data-gedreven` · `resultaatgedreven` · `aangedreven door AI` · `door AI aangedreven` · `AI-powered`

Voor: Een AI-gedreven aanpak, aangedreven door machine learning.

Na: We gebruiken machine learning om de meldingen te sorteren.

Niet markeren: 'Marktgedreven' en 'vraaggedreven' zijn ingeburgerde economische termen en 'datagedreven' is in beleidstaal gewoon geworden; die staan daarom niet allemaal in de regex. Het signaal is de stapeling en het gebruik als sierwoord zonder dat duidelijk wordt wat er aandrijft.

### Engelse afkortingen, ampersand en bronvermelding `english-abbreviation-and-citation-nl`

Ernst: **cluster** · Herkomst: translationese

Engelse afkortingen en het en-teken staan in Nederlandse lopende tekst waar het Nederlands eigen vormen heeft. Dezelfde overzetting raakt de bronvermelding: Engelse signaalwoorden, Engelse datumvolgorde en Engelse verwijsafkortingen in een Nederlandse literatuurlijst.

Signalen: `e.g.` · `i.e.` · `ASAP` · `TL;DR` · `& in lopende tekst` · `Retrieved from` · `Accessed on` · `n.d.` · `pp. in plaats van p.` · `Ibid.` · `vol. 3, no. 2 zonder vertaling`

Voor: Kies een statische generator, e.g. Astro of Hugo, & test lokaal.

Na: Kies een statische generator, bijvoorbeeld Astro of Hugo, en test lokaal.

Niet markeren: De ampersand hoort in bedrijfsnamen, in codenotatie en in vaste combinaties, en staat daarom niet in de regex. 'vs.' is in sportuitslagen en vergelijkende koppen ingeburgerd, en 'et al.' is in wetenschappelijke literatuurlijsten de norm. In een Engelstalige bronvermelding horen de Engelse vormen gewoon.

### Er zijn X die-constructie `existential-there-are-nl`

Ernst: **cluster** · Herkomst: translationese

De zin opent met een bestaanszin naar Engels model, There are many X that, waar het Nederlands het onderwerp meteen voorop zet. Als vaste opening maakt hij elke alinea traag en zet hij het echte onderwerp achteraan.

Signalen: `Er zijn veel bedrijven die` · `Er zijn een aantal` · `Er zijn verschillende manieren om` · `Er is een groeiende behoefte aan` · `Er zijn talloze`

Voor: Er zijn veel organisaties die worstelen met dit probleem.

Na: Veel organisaties worstelen hiermee.

Niet markeren: De bestaanszin is gewoon Nederlands als er echt iets wordt geïntroduceerd dat de lezer nog niet kent ('Er staat iemand voor de deur') en in encyclopedische opsommingen. Het signaal is het gebruik als vaste opening, drie of meer keer per tekst.

### Bekend als en de zogenaamde `known-as-appositive-calque`

Ernst: **cluster** · Herkomst: translationese · en: `known-as-appositive-calque`

De Engelse bijstelling 'X, known as Y' of 'the so-called Y' wordt als volledige betrekkelijke constructie weergegeven: bekend als, wat bekendstaat als, ook wel Y genoemd, de zogenaamde Y. Het Nederlands zet de afkorting of de tweede naam gewoon tussen haakjes. Op zichzelf een zwakke tell, sterker zodra hij samen optreedt met de andere Engelse aanhaalgewoontes.

Signalen: `bekend als` · `wat bekendstaat als` · `de zogenaamde` · `ook wel ... genoemd`

Voor: Kunstmatige algemene intelligentie, bekend als AGI, is nog ver weg.

Na: Kunstmatige algemene intelligentie (AGI) is nog ver weg.

Niet markeren: 'Bekend als' en 'de zogenaamde' zijn gewoon Nederlands en staan daarom niet in de regex; in encyclopedische en historische tekst zijn het de normale vormen ('ook wel de Twentse Ooievaar genoemd'). Het signaal is de vaste bijstelling bij elke term, en 'zogenaamd' in de Engelse betekenis 'genaamd' in plaats van de Nederlandse betekenis 'zogenaamd, maar niet echt'.

### Lange voorbepaling voor het zelfstandig naamwoord `left-branching-modifier-stack`

Ernst: **cluster** · Herkomst: translationese · en: `left-branching-modifier-stack`

Een Engelse betrekkelijke bijzin achter het zelfstandig naamwoord wordt in het Nederlands als lange voorbepaling ervóór gezet: het vorig jaar in Europa gepubliceerde en door de commissie aangepaste rapport. De lezer moet de hele bepaling vasthouden voor hij weet waar ze bij hoort. Dit is de Nederlandse tangconstructie.

Signalen: `de vorig jaar gepubliceerde nieuwe regels` · `het door de commissie aangepaste rapport` · `drie of meer woorden voor het kernwoord` · `lange afstand tussen onderwerp en persoonsvorm`

Voor: Het vorig jaar in Europa gepubliceerde en door de commissie aangepaste rapport verscheen gisteren.

Na: Het rapport verscheen gisteren. Het kwam vorig jaar in Europa uit en de commissie paste het daarna aan.

Niet markeren: Een korte voorbepaling is gewoon Nederlands ('de vorig jaar gebouwde brug') en in juridische en wetenschappelijke tekst is de langere vorm gangbaar. Het signaal is de lengte, vier of meer woorden tussen lidwoord en kernwoord, en de herhaling ervan.

### Kan en kunnen op elk gezegde `modal-ability-overuse`

Ernst: **cluster** · Herkomst: translationese · en: `modal-ability-overuse`

Elk gezegde wordt verzacht met kan of kunnen omdat het Engelse origineel can, could of be able to zei: deze tool kan je tijd besparen, terwijl de bewering is dat hij tijd bespaart. Vaak staan er twee afzwakkers gestapeld: zou mogelijk kunnen bijdragen. Daardoor krijgen gerechtvaardigde beweringen en echte voorbehouden dezelfde vorm.

Signalen: `kan mogelijk` · `zou kunnen helpen` · `kan bijdragen aan` · `kunnen ervoor zorgen dat` · `kan een rol spelen bij` · `mogelijk zou kunnen` · `in sommige gevallen kan` · `kan je tijd besparen` · `kan zorgen voor`

Voor: Dit zou mogelijk kunnen bijdragen aan een betere doorlooptijd.

Na: Dit verkort de doorlooptijd met een dag.

Niet markeren: Eén afzwakking per bewering is normaal en in medische, juridische en wetenschappelijke tekst vaak verplicht. 'Kan leiden tot' is in risicobeschrijvingen de precieze formulering. Het signaal is de stapeling van twee afzwakkers op dezelfde bewering, en de afzwakking op een feit dat vaststaat.

### Bieden als vertaling van offer en provide `offer-verb-overuse-nl`

Ernst: **cluster** · Herkomst: nl-bron

Bied, biedt en bieden staan overal waar het Engels offer, provide of deliver zegt, met een abstract lijdend voorwerp erachter. In natuurlijk Nederlands staat er een concreter werkwoord of gewoon 'hebben'. Nederlandse waarnemers noemen dit een van de betrouwbaarste losse woordsignalen.

Signalen: `biedt een reeks` · `biedt een breed scala aan` · `wij bieden` · `biedt inzicht in` · `biedt de mogelijkheid om` · `biedt ondersteuning bij` · `biedt oplossingen voor`

Voor: Een dienstenbedrijf biedt een reeks software aan die inzicht biedt in je processen.

Na: Een dienstenbedrijf verkoopt software die laat zien waar je processen vastlopen.

Niet markeren: 'Bieden' is gewoon Nederlands bij een bod op een veiling of een huis, bij hulp bieden en bij een aanbod met een prijs erbij. Het signaal is de dichtheid, drie of meer vormen per tekst, telkens met een abstract lijdend voorwerp.

### Valse formaliteit en archaïsche voegwoorden `overformal-register-nl`

Ernst: **cluster** · Herkomst: translationese

Beleefdheid en blijdschap komen in een register dat in het Nederlands vrijwel niemand meer gebruikt, als overzetting van delighted, excited en pleased: wij zijn verheugd, het doet ons genoegen, wij informeren u graag. Dezelfde beweging kiest voor therefore, thus en nevertheless de zwaarste Nederlandse vorm: derhalve, teneinde, bijgevolg, desalniettemin. Het is het register van vertaalde Engelse bedrijfscommunicatie.

Signalen: `wij zijn verheugd` · `verheugd om aan te kondigen` · `wij zijn opgetogen` · `het doet ons genoegen` · `wij informeren u graag over` · `in de hedendaagse maatschappij` · `Beste klant` · `derhalve` · `zodoende` · `desalniettemin` · `voorts` · `teneinde` · `bijgevolg` · `aangaande` · `betreffende` · `voornoemd` · `welke als betrekkelijk voornaamwoord`

Voor: Wij zijn verheugd om aan te kondigen dat de nieuwe versie live is.

Na: De nieuwe versie staat live.

Niet markeren: In juridische stukken, notariële akten, jaarverslagen, overheidsbesluiten en officiële aanhef is dit register de norm en geen signaal. 'Aldus' bij een citaatattributie is normaal journalistiek Nederlands en staat daarom niet in de regex. In een blog, nieuwsbrief of post is het wel een signaal, zeker bij drie of meer van deze woorden bij elkaar.

### Engelse term tussen haakjes bij elke herhaling `parenthetical-english-gloss`

Ernst: **cluster** · Herkomst: translationese · en: `parenthetical-english-gloss`

Een Nederlandse term krijgt bij elke vermelding het Engelse origineel tussen haakjes mee, zodat 'soevereine AI (sovereign AI)' verderop opnieuw voluit met glos staat in plaats van kaal. De gewoonte breidt zich uit tot elke vakterm, waardoor de pagina als tweetalige woordenlijst leest. Licht één keer toe en gebruik daarna de Nederlandse term.

Signalen: `soevereine AI (sovereign AI)` · `aanbevelingssysteem (recommender system)` · `dezelfde haakjesglos twee keer` · `elke vakterm met Engels erbij`

Voor: Soevereine AI (sovereign AI) is beleid. Soevereine AI (sovereign AI) kost geld.

Na: Soevereine AI (sovereign AI) is beleid. Dat beleid kost geld.

Niet markeren: De eerste glos is normale zorgvuldigheid, zeker bij een term die de lezer alleen in het Engels kent. Het signaal is pas de tweede keer dezelfde glos. De regex is geschrapt omdat elke haakjesuitleg meetelde, ook in gewone Nederlandse tekst; poort dit op herhaling.

### Aan het doen zijn en wordt steeds `passive-progressive-calque`

Ernst: **cluster** · Herkomst: translationese · en: `passive-progressive-calque`

Een trend of toestand wordt beschreven met de omschreven duurvorm 'is aan het groeien' of met 'wordt steeds meer', als weergave van het Engelse is being done en is increasingly, waar een gewone tegenwoordige of verleden tijd dezelfde bewering draagt. De tell is drie of meer in één alinea, waardoor elke zin van een trendpassage dezelfde vorm krijgt.

Signalen: `is aan het groeien` · `zijn aan het toenemen` · `wordt steeds meer` · `wordt steeds vaker` · `wordt steeds belangrijker` · `is aan het veranderen`

Voor: De belangstelling is aan het groeien en de investeringen zijn aan het toenemen.

Na: De belangstelling groeide en er kwam meer geld bij.

Niet markeren: 'Aan het' plus infinitief is gewoon Nederlands in spreektaal en in een lopende handeling ('hij is aan het bellen'). Eén 'wordt steeds vaker' in een tekst is normaal. Het signaal is de vaste weergave van elke Engelse progressief in geschreven proza.

### Omschrijvende overtreffende trap met meest `periphrastic-superlative-nl`

Ernst: **cluster** · Herkomst: translationese

De trappen van vergelijking worden met 'meer' en 'meest' omschreven zoals in het Engels, terwijl het Nederlands het achtervoegsel -er en -ste gebruikt: de meest belangrijke stap in plaats van de belangrijkste stap.

Signalen: `meest belangrijke` · `meest simpele` · `meest snelle` · `meest makkelijke` · `meer simpel` · `een van de meest`

Voor: Dit is de meest belangrijke stap.

Na: Dit is de belangrijkste stap.

Niet markeren: 'Meest' is correct bij lange bijvoeglijke naamwoorden en deelwoorden ('de meest gebruikte tool', 'het meest voorkomende probleem') en waar de vorm met -ste niet bestaat of raar staat. Het signaal is 'meest' bij korte woorden die gewoon een -ste-vorm hebben.

### Kwantiteitscalques `quantity-calques-nl`

Ernst: **cluster** · Herkomst: translationese

Hoeveelheden worden met een Engelse omschrijving aangeduid: a wide range of wordt een breed scala aan, hundreds of wordt honderden van, a wealth of wordt een schat aan. De vage hoeveelheid komt in de plaats van een opsomming of een getal.

Signalen: `een breed scala aan` · `een verscheidenheid aan` · `honderden van` · `duizenden van` · `een schat aan` · `een overvloed aan` · `talloze` · `een breed spectrum`

Voor: We bieden een breed scala aan diensten en honderden van tevreden klanten.

Na: We doen e-mailmarketing en SEO, voor ruim tweehonderd klanten.

Niet markeren: 'Een schat aan ervaring' en 'talloze' bestaan als Nederlandse uitdrukking en staan niet in de regex. Een partitief 'van' na een telwoord is correct wanneer er een bepaalde groep achter staat ('honderden van de aanwezigen'). Het signaal is de vage hoeveelheid die een concrete opsomming vervangt.

### Van-ketens `stacked-particles`

Ernst: **cluster** · Herkomst: translationese · en: `stacked-particles`

Drie of meer keer 'van' in één naamwoordgroep, als spiegel van de Engelse of-keten: de uitkomst van de evaluatie van het beleid van de gemeente. Rol de keten uit tot een zin, of maak er een samenstelling van.

Signalen: `de uitkomst van de evaluatie van het beleid van` · `het rapport van de commissie van de raad` · `drie keer van achter elkaar`

Voor: De uitkomst van de evaluatie van het beleid van de gemeente is bekend.

Na: De gemeente liet haar beleid evalueren, en de uitkomst is bekend.

Niet markeren: Twee keer 'van' achter elkaar is gewoon Nederlands ('de voorzitter van de raad van bestuur' is zelfs een vaste term). In genealogische, juridische en bestuurlijke namen hoort de keten er nu eenmaal bij. Het signaal begint bij drie.

### Onvertaald Engels marketingwoord in Nederlandse tekst `untranslated-marketing-loanword`

Ernst: **cluster** · Herkomst: nl-bron · en: `untranslated-marketing-loanword`

Engelse marketing- en managementwoorden blijven onvertaald staan terwijl het Nederlands een even kort en gangbaar woord heeft: insights, learnings, seamless, key takeaways, deep dive, quick wins, alignment, gamechanger, cutting-edge. Het breekt het ritme van de zin en leest als vertoon. De tegenregel hoort erbij: gewone vaktermen blijven wél Engels, en die vertalen is zelf een fout.

Signalen: `insights` · `learnings` · `key takeaways` · `actionable` · `seamless` · `leverage` · `delve` · `tapestry` · `realm` · `cutting-edge` · `next-level` · `gamechanger` · `game-changer` · `value proposition` · `customer journey` · `best practices` · `deep dive` · `quick wins` (+9)

Voor: De key takeaways van deze deep dive: onze seamless customer journey is cutting-edge.

Na: Klanten hoeven nu geen formulier meer in te vullen.

Niet markeren: Vaktermen zonder Nederlands equivalent blijven staan: API, prompt, token, pipeline, container, repository, commit, deploy, meetup, framework, stakeholder. In een Engelstalig team is codeswitching de normale werktaal, en in citaten blijft het Engels staan. Het onderscheid is of een gewoon Nederlands woord hetzelfde zegt; 'mindset' en 'commitment' staan daarom niet in de regex.

### Engelse zin ingeplakt met de vertaling erbij `embedded-english-quotation`

Ernst: **context** · Herkomst: translationese · en: `embedded-english-quotation`

Een hele Engelse zin staat letterlijk als citaat in de lopende tekst, direct gevolgd door de vertaling, zodat de lezer dezelfde bewering twee keer in twee talen krijgt. Het is de brontekst die door de generatie heen lekt.

Signalen: `Engels citaat met vertaling erachter` · `(vrij vertaald: ...)` · `oftewel, in het Nederlands`

Voor: Het rapport schreef: "Adoption will accelerate over the next two years." (vrij vertaald: de invoering versnelt de komende twee jaar.)

Na: Volgens het rapport gaat de invoering de komende twee jaar sneller.

Niet markeren: Als de precieze bewoording ertoe doet, is het citaat plus vertaling juist zorgvuldig: in juridische, wetenschappelijke en journalistieke tekst hoort een letterlijk citaat bij de bronvermelding. Het signaal is de dubbeling zonder reden.

### Engelse volgorde in de bijzin `english-clause-order-nl`

Ernst: **context** · Herkomst: nl-bron

In een bijzin blijft de werkwoordsgroep niet aan het eind staan, of hij wordt in Engelse volgorde uit elkaar getrokken met de bepalingen erachter: 'zodat het team kan focussen op groei', 'omdat we moeten kijken naar de cijfers eerst'. Daarbij hoort het abstractieniveau van Engelse institutionele proza, met een reeks bijzinnen die elk op een vaag gevolg eindigen.

Signalen: `zodat het team kan focussen op groei` · `omdat we moeten kijken naar de cijfers eerst` · `die is ontworpen voor teams die willen groeien snel` · `bepaling systematisch achter de werkwoordsgroep` · `De onderzoekers suggereren…` · `wat bijdraagt aan`

Voor: Ik denk dat we moeten kijken naar de cijfers eerst.

Na: Ik denk dat we eerst naar de cijfers moeten kijken.

Niet markeren: Een bepaling achter de werkwoordsgroep komt in gesproken Nederlands en in journalistiek proza gewoon voor, en is bij lange bepalingen zelfs de leesbaarste keuze. Het signaal is de systematiek: elke bijzin volgt de Engelse volgorde. Geen regex, want de afwijking is alleen per zin te beoordelen.

### Lidwoord weg, bezittelijk voornaamwoord erbij `english-determiner-transfer-nl`

Ernst: **context** · Herkomst: translationese

De Engelse omgang met bepalers lekt twee kanten op. Het lidwoord verdwijnt voor een abstract of ontelbaar naamwoord, omdat het Engels daar geen lidwoord zet: dit verbetert workflow en verlaagt kosten. En bij lichaamsdelen, gereedschap en vaste onderdelen staat juist een bezittelijk voornaamwoord waar het Nederlands een lidwoord gebruikt: open je browser en typ je URL in je adresbalk.

Signalen: `verbetert workflow` · `verlaagt kosten` · `verhoogt performance` · `Team kan hierdoor sneller leveren` · `open je browser` · `typ je URL in` · `pak je telefoon` · `was je handen` · `in je adresbalk`

Voor: Dit verbetert workflow en verlaagt kosten.

Na: Dit verbetert de workflow en verlaagt de kosten.

Niet markeren: Het Nederlands laat het lidwoord ook weg in koppen, opsommingen, vaste combinaties ('op kantoor', 'in overleg') en bij stofnamen in algemene uitspraken ('Water kookt bij 100 graden'). In instructies aan één lezer is 'je' vaak juist de duidelijkste keuze, en bij echt bezit is het bezittelijk voornaamwoord verplicht. Het signaal is de stapeling van drie of meer in één zin of stap.

### Mechanisch meervoud op niet-telbare woorden `mechanical-plural-marking`

Ernst: **context** · Herkomst: translationese · en: `mechanical-plural-marking`

Het verplichte Engelse meervoud wordt meegenomen op woorden die in het Nederlands geen meervoud krijgen: informaties, feedbacks, researches. Of het Engelse meervoud blijft staan op een leenwoord waar het Nederlands een eigen vorm heeft: trainings in plaats van trainingen.

Signalen: `informaties` · `feedbacks` · `researches` · `trainings` · `learnings`

Voor: De informaties en de feedbacks zijn verwerkt.

Na: De informatie en de reacties zijn verwerkt.

Niet markeren: In Belgisch-Nederlands en in ambtelijke vertalingen uit het Frans komt 'informaties' voor als eigen vorm. 'Trainings' als eerste lid van een samenstelling ('trainingsschema') is correct en valt buiten de regex. Zwak patroon: gebruik het als observatie, nooit als dominant bewijs.

### Voornaamwoorden één op één overgezet `pronoun-over-translation`

Ernst: **context** · Herkomst: translationese · en: `pronoun-over-translation`

Elk Engels he, she, it en they wordt afzonderlijk vertaald. Het duidelijkste spoor is de sjabloonvorm hij of zij, hem of haar, zijn of haar; het tweede is de singular they die als 'hen' of 'hun' bij een grammaticaal enkelvoudig onderwerp opduikt. Daarnaast staan er rijen persoonlijke voornaamwoorden waar het Nederlands zou samentrekken of de persoon zou noemen.

Signalen: `hij of zij` · `hem of haar` · `zijn of haar` · `drie of meer hij-zinnen achter elkaar` · `als een gebruiker inlogt, ziet hen` · `de deelnemer krijgt hun bevestiging` · `elke gebruiker beheert hun profiel`

Voor: Elke gebruiker beheert hun eigen profiel.

Na: Gebruikers beheren hun eigen profiel.

Niet markeren: Nederlandse teksten gebruiken bewust 'die' of 'hen' als genderneutrale verwijzing naar een specifieke persoon die dat zelf zo wil; dat is een keuze en geen fout. In juridische tekst is 'hij of zij' een vaste formule. Het signaal is de meervoudsvorm bij een grammaticaal enkelvoudig onderwerp zonder persoon in beeld.

### Interferentie-index `translationese-interference-index`

Ernst: **context** · Herkomst: translationese · en: `translationese-interference-index`

Een maat, geen zinspatroon: de interferentie-as uit de vertaalwetenschap, uitgedrukt in negen telbare Nederlandse signalen die samen één index vormen. De negen assen zijn de structuurkaart van deze categorie en maken het overkoepelende effect telbaar dat Nederlandse lezers omschrijven als tekst die klinkt als vertaald Engels. De koppeling loopt twee kanten op: tellingen boven de drempel voeden de diagnose, en een index buiten de basislijn dwingt extra controle bij het afronden.

Signalen: `abstract_onderwerp_ratio` · `door_passief_aantal` · `hulpwerkwoordstapel_aantal` · `voornaamwoord_dichtheid` · `losse_samenstellingen_ratio` · `voorbepaling_diepte` · `licht_werkwoord_calques` · `van_keten_aantal` · `aan_het_progressief_ratio` · `interferentie_index`

Voor: De door de commissie opgestelde informaties kunnen in termen van beleid worden benut.

Na: De commissie schreef dit op. Het beleid kan het gebruiken.

Niet markeren: Geen markeerpatroon: gebruik de index nooit om één zin af te keuren. Vertaalde teksten scoren van nature hoger op interferentie, dus een echte vertaling is geen AI-signaal. Stel de basislijn per tekstsoort in, want ambtelijke en wetenschappelijke tekst ligt hoger dan blogtekst.
