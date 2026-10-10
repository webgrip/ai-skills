# Hergebruik en releases in de estate

Welke machinerie er al staat om dingen niet twee keer te bouwen, en waar hij bijt. Geverifieerd
2026-09-03 en 2026-09-05. Bind nieuw extractiewerk aan deze mechanismen in plaats van er een
nieuw bij te verzinnen.

**De ladder, van sterk naar zwak:** genereren > refereren (`uses:@sha`, een `@webgrip`-package)
> sync-PR's > eenmalige kopie uit een template > een skill voor kennis. Wat per site een eigen
besluit is — budgetten, toegankelijkheidslijsten, verboden claims — dedupliceer je nooit.

## `webgrip/workflows`

Semantisch gereleased met onveranderlijke tags `v1.0.0` tot `v2.0.0`, en met opzet **geen**
meebewegende major-tag. Renovate houdt de `uses:`-pins van consumenten vers; de
github-actions-manager leest ook `.forgejo`-bomen, en de digest-pinregels staan in
`renovate-config/default.json`.

`sync-template-files.yml` in dezelfde repo is topic-gefilterd en werkt via PR's, met de
*aanroepende* templaterepo als canonieke kopie. Twee vallen: de input `paths` wordt gedeclareerd
maar nooit gelezen (de bestandslijst staat hardcoded), en niets plant hem in — hij is alleen
`workflow_call`.

## Het committype is de releasebeslissing

Waar releases uit conventional commits berekend worden, beslist het type van de commit of er
een release komt, en welke. Bij squash-merges is de PR-titel die commit: controleer de titel
vóór het mergen. Een verkeerd type geeft geen fout, alleen geen release.

- **`@webgrip/semantic-release-config`** (`index.cjs`, 1.3.3): breaking → major; `feat` →
  minor; `fix`, `perf`, `refactor`, `revert`, `chore(deps)` en `build(deps)` → patch. Al het
  andere (`docs`, `ci`, `test`, `style`, een kale `chore` of `build`) geeft geen release.
  Squash met een `chore:`-titel voor geen release; maak er `fix(<scope>): …` van om wel een
  patch te snijden.
- **`webgrip/ai-skills`** heeft een trein per skill: commits onder `skills/<naam>/` moeten
  `feat`, `fix`, `perf`, `refactor`, `revert` of breaking zijn, en `version` bewerk je nooit
  met de hand. De details staan in de `AGENTS.md` van die repo.
- Releasebots committen terug (`chore(release): … [skip ci]`). Pull vóór elke push.

## Een releasejob faalt als zijn eigen commit verdwenen is

Een releasejob die bij een retry `reset --hard` naar de remote-head doet, releaset stilletjes
zonder zijn triggerende commit als die intussen van de branch verdwenen is, bijvoorbeeld door
een push-mirror die refs terugschrijft ([forgejo-ci.md](forgejo-ci.md#een-push-mirror-kan-een-push-stilletjes-terugdraaien)).
Controleer vóór de reset en vóór de release dat de commit er nog op staat:

```bash
git merge-base --is-ancestor "$GITHUB_SHA" "origin/$GITHUB_REF_NAME" \
  || { echo "triggering commit $GITHUB_SHA is no longer on $GITHUB_REF_NAME"; exit 1; }
```

Meld de fout in de vorm die `webgrip/workflows` voorschrijft: `::error::`-annotaties zijn daar
bewust verwijderd.

## Packages

De Forgejo npm-registry werkt (`https://forgejo.webgrip.dev/api/packages/webgrip/npm/`, anoniem
leesbaar). Publiceren vereist `WEBGRIP_CI_TOKEN` met `write:package`; het per-run jobtoken geeft
401 op `reqPackageAccess`. Aan de consumentenkant volstaat één scope-regel in `.npmrc`.

`frontend-toolkit` heeft per package een eigen semantic-release-monorepo-trein: `feat(<pkg>)` is
een minor, de tag is `@webgrip/<pkg>-vX.Y.Z`. Het publiceert **eerst naar het publieke npmjs**,
waarna een `mirror-registry`-job het naar Forgejo kopieert. Consumenten hebben geen `.npmrc` en
halen van npmjs. Een rondje van push tot beschikbaar duurt ongeveer vijf minuten; pollen kan met
`npm view @webgrip/<pkg> version`. De runlijst toont vaak `failure` op de mirror-job terwijl de
treinen wel gereleased hebben.

### Twee vallen bij een eigen release op dezelfde dag

**`minimumReleaseAge` blokkeert je eigen verse package.** Die supply-chain-drempel van 24 uur
laat `pnpm install` slagen en elke `pnpm <script>` daarna falen met
`ERR_PNPM_MINIMUM_RELEASE_AGE_VIOLATION`. Pnpm 11 plakt er stilletjes een per-versieregel met
enkele aanhalingstekens bij in `minimumReleaseAgeExclude`. De juiste vorm is één regel voor het
hele scope:

```yaml
minimumReleaseAgeExclude:
  - "@webgrip/*"
```

Gooi de automatisch toegevoegde per-versieregel weg.

**Elke toolkit-release herschrijft `version` in `packages/<pkg>/package.json`**, dus de volgende
commit die datzelfde bestand raakt botst op `git pull --rebase`; op 2026-09-05 gebeurde dat drie
van de drie keer. Los het op door de `version` van de release te nemen en je eigen velden te
houden, nooit door een oude versie mee terug te dragen. Fetch en rebase *voordat* je een
package.json-wijziging commit, dan heb je het conflict niet.

## Losse eindjes om te weten

`comment-ban --report` schrijft `.comment-ban-ledger.json` in de repo-root. Gooi die weg voor je
commit, tenzij het grootboek zelf de deliverable is.

De `renovate.json` van app-repo's gebruikt de ongetagde vorm `local>webgrip/renovate-config`,
terwijl de gedocumenteerde vorm tag-gepind is via de GitHub-mirror
(`github>webgrip/renovate-config#vX.Y.Z`). Die twee lopen uiteen.
