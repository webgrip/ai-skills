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
| Checkout | `actions/checkout@v5`, nooit `@v6` | v6 is stuk op niet-GitHub-runners |
| Node-ondergrens | `^22.14.0 \|\| >=24.10.0` | org-breed |
| Tijdzone | `Europe/Amsterdam` | ook voor elk cron-schema |
| Releases | `@webgrip/semantic-release-config` | uit de Forgejo npm-registry |

## Wat geen Forgejo-equivalent heeft

GitHub App-tokens, GitHub Models, GitHub Pages-hosting en GitHub Advanced Security. Die zijn
allemaal vervangen of geschrapt. Stel nooit een patroon uit de GitHub Actions-marketplace voor
in een Forgejo-repo zonder te controleren dat het op forgejo-runner werkt.
