# Forgejo als release-autoriteit

Webgrip host Forgejo zelf op [forgejo.webgrip.dev](https://forgejo.webgrip.dev) en behandelt het
als de enige release-autoriteit. Wat hieronder staat is geverifieerd tegen de live repo's
`webgrip/workflows`, `webgrip/semantic-release-config` en `webgrip/renovate-config`. De
bibliotheek verandert; controleer de inputs van een specifieke workflow tegen de bron voordat je
erop leunt.

## Twee bomen, kies de goede

`webgrip/workflows` houdt er twee naast elkaar (zijn eigen ADR-0002). `.github/workflows/` ligt
byte-voor-byte vast voor GitHub-consumenten; `.forgejo/workflows/` is de volledige,
Forgejo-aangepaste spiegel. Neem de boom die bij de host van de consument hoort.

## `uses:` is de shorthand, nooit een volledige URL

```yaml
uses: webgrip/workflows/.forgejo/workflows/<naam>.yml@<sha> # main
```

De vorm met `https://forgejo.webgrip.dev/...` breekt het inplannen: Forgejo kan de `runs-on` van
de aangeroepen workflow dan niet naar runnerlabels herleiden, en de job wacht eeuwig met een lege
labellijst. Op twente.dev werd daardoor nooit één taak opgepakt, tot het omgezet werd naar de
shorthand.

## `if:` op een `uses:`-job doet niets

Sinds Forgejo v15.0.0 wordt een `uses:`-job uitgeklapt naar de losse jobs van de aangeroepen
workflow, zolang die job geen eigen `runs-on` heeft en de workflow op dezelfde server staat
([PR #10525](https://codeberg.org/forgejo/forgejo/pulls/10525), gemerged 2025-12-24). De `if:`
van de aanroepende job gaat bij dat uitklappen **niet** mee naar de binnenste jobs, en dat is in
die PR nooit geïmplementeerd. Een branchgate op een aangeroepen workflow doet dus niets.

Gemeten op twente.dev in september 2026: een docs-deploy met
`if: github.ref == 'refs/heads/main'` publiceerde vanaf `development`. Een expliciete `runs-on`
op de aanroepende job onderdrukt het uitklappen en herstelt het gedrag.

Controleer een repo hierop met:

```bash
grep -rn -A4 "uses:" .forgejo/workflows/ | grep -B2 "if:"
```

En let op de bijwerking: validatie die de aangeroepen workflow op andere branches deed, verdwijnt
met de expansie mee. Vervang die door een eigen, lokale check.

## Vaste waarden

| Wat | Waarde | Waarom |
| --- | --- | --- |
| Runnerlabel | `runs-on: docker` | |
| Checkout | `actions/checkout@v5` als default, `@v6`/`@v7` mag | zie hieronder — de oude "v6 is stuk"-regel is op 2026-09-18 weerlegd |
| Node-ondergrens | `^22.14.0 \|\| >=24.10.0` | org-breed |
| Tijdzone | `Europe/Amsterdam` | ook voor elk cron-schema |
| Releases | `@webgrip/semantic-release-config` | uit de Forgejo npm-registry |

## De checkout-majors zijn niet stuk (gemeten 2026-09-18)

Hier stond jarenlang "v6 is stuk op niet-GitHub-runners", zonder dat iemand de foutmelding had
opgeschreven. Dat blokkeerde estate-breed elke `actions/checkout`- en `actions/setup-node`-major.

Een canary op de echte runner
([homelab-cluster run 1710](https://forgejo.webgrip.dev/webgrip/homelab-cluster/actions/runs/1710),
workflow `.forgejo/workflows/runner-node-canary.yml`) draait checkout v5.1.0, v6 en v7 en
setup-node v4.4.0, v5 en v7 naast elkaar. **Alles groen**, en geen no-ops: de v6-stap doet echt
`git init`/`git config` en fetcht van de in-cluster Forgejo, setup-node v5 meldt `node: v24.21.0`.

De onderliggende aanname — dat `using: node24` niet draait omdat de runner node20 aanreikt —
klopt ook niet. De runner kiest per JS-actie de node uit `externals/` die de actie declareert, en
daar staat een glibc `node24` (v24.16.0) naast `node20` (v20.19.5). De `PATH`-prepend naar
`externals/node20/bin` in de runner-ScaledJob raakt alleen **shell-stappen**: een `run:`-stap die
`node` aanroept krijgt v20 terwijl de image v24 aan boord heeft. Aparte, kleinere kwestie.

Praktisch: majors mogen voorgesteld worden, maar zet ze niet op automerge. Eén canary-job is geen
hele pipeline; een echte PR die de complete gate draait is het bewijs dat telt.

**Les voor deze hele pagina.** Een "X is stuk"-regel zonder de logregel erbij houdt zichzelf jaren
in stand. Kost één workflow en één run om te controleren.

## Wat geen Forgejo-equivalent heeft

GitHub App-tokens, GitHub Models, GitHub Pages-hosting en GitHub Advanced Security. Die zijn
allemaal vervangen of geschrapt. Stel nooit een patroon uit de GitHub Actions-marketplace voor
in een Forgejo-repo zonder te controleren dat het op forgejo-runner werkt.
