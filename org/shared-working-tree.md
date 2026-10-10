# Meerdere sessies, één working tree

Er draaien regelmatig meerdere Claude-sessies tegen dezelfde projectmap tegelijk; op 2026-08-30
waren dat er zes, drie daarvan op twente.dev. Ze delen één working tree, één index en één lokale
git-repo. Drie gevolgen, alle drie op de harde manier geleerd.

## 1. `git commit` neemt de hele index, niet jouw paden

Het werk dat een andere sessie heeft gestaged, rijdt stilletjes mee. Op 2026-08-30 belandden zo
zes verwijderingen van een peer in een commit die over een CI-check ging. Daardoor stond `main`
even met twee perspagina's die naar drie merkassets linkten die niet meer bestonden, zonder
redirects: 404's op precies de pagina waar journalisten heen gestuurd worden. Net op tijd
gezien.

**Dus: commit op pathspec (`git commit -- <paden>`), nooit een kale `git commit` na `git add`.**
Draai eerst `git status` en behandel alles wat je niet zelf hebt geschreven als lopend werk van
iemand anders.

**Maar een pathspec neemt de working-tree-inhoud van die paden mee.** `git commit -- <pad>`
(`--only`) houdt wat een peer elders gestaged heeft buiten je commit, maar commit het genoemde
bestand zoals het op schijf staat, inclusief een wijziging die een andere sessie in datzelfde
bestand heeft gemaakt en nog niet gestaged heeft. Toont `git diff -- <pad>` meer dan jouw
wijziging, zet dan alleen jouw wijziging in de index (`git apply --cached jouw.patch`, of een
blob uit `HEAD` plus jouw wijziging via `git hash-object -w` en
`git update-index --cacheinfo "100644,<blob>,<pad>"`) en commit **zonder** pathspec, met een
index die verder leeg is (`git diff --cached --name-only` toont alleen jouw paden).

## 2. Een lokale commit blijft niet lokaal

Elke `git push` van een peer duwt alles wat er op de lokale branch staat, inclusief jouw
commits. Een commit achterhouden om een draaiende CI-job niet te annuleren werkt niet; een peer
pusht en annuleert de deploy alsnog.

**Dus: reken niet op "ik push later".** Is het gecommit, ga er dan van uit dat het elk moment
kan uitgaan, en dus moet het op het moment van committen al kloppen en compleet zijn.

## 3. Andersom kan een peer de helft van jouw wijziging meenemen

Op 2026-09-04 committe een andere sessie `src/config/site.ts`, waar een export was verwijderd,
zonder `src/templates/HomePage.astro`, waar de bijbehorende import weg moest. `main` brak op
`ts(2305)`. De helft die landde was niet fout, hij was onvolledig, en in geen van beide lokale
bomen was iets te zien omdat daar allebei de bestanden klopten.

**Dus: een wijziging over meerdere bestanden is pas veilig als hij gecommit is.** Land zo'n
verandering snel in plaats van hem in de tree te laten liggen, en als CI breekt op iets dat je
herkent, kijk dan met `git show <sha>:<bestand>` naar *beide* helften voor je aanneemt dat het
van iemand anders is.

## De routine

Voor je commit in een gedeelde repo: `git status` op vreemde wijzigingen, daarna committen op
pathspec. Moet je toch andermans werk meenemen omdat er "commit alles" gevraagd wordt,
controleer dan eerst of de gecombineerde boom klopt — draai de volledige gate en kijk of wat de
wijzigingen noemen ook echt bestaat — en land het dan als één samenhangende commit in plaats van
een halve.

Sinds 2026-09-05 staat de twente.dev-boom op een `development`-branch. Doe in zo'n gedeelde tree
nooit `git checkout`, `git rebase` of `git stash`; commit op pathspec op de branch die uitstaat,
en zeg erbij op welke branch het geland is. `refs/stash` is één lijst voor alle sessies en
worktrees: `git stash && <lint>; git stash pop` kan de stash van een ander poppen. Zet
onaf werk liever in een commit op een eigen branch.

Binnenhalen wat op de remote veranderde gaat in de gedeelde tree met een merge: fetch, check dat
de index leeg is en dat de remote-wijzigingen geen van de bestanden raken waar iemand nog aan
werkt, dan `git merge --no-edit origin/<trunk>`. Draai de gate daarna in een schone, detached
worktree op die merge-commit, niet in de gedeelde tree: daar kan andermans lopende werk
(een submodule op een andere versie, een half bestand) de gate vals laten falen. Je eigen
werk doe je het liefst in zo'n detached worktree vanaf `origin/<trunk>`, en je pusht alleen
commits waarvan `git log origin/<trunk>..HEAD` laat zien dat ze van jou zijn.
