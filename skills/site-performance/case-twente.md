# Case: twente.dev through the procedure

twente.dev is a bilingual community site: Astro static output on an assets-only Worker, with its own web-vitals beacon to a telemetry collector and Lighthouse CI in its pipeline. This is what the procedure found on 2026-10-04 from a fresh build of the main branch and the live site. It is a fast site; the findings are about measuring it properly and keeping it fast.

## What the scans and the code showed

| Area | Found | Verdict |
| --- | --- | --- |
| Delivery | Zstandard compression, HTTP/3 advertised, hashed `/_astro/*` files with `max-age=31536000, immutable`, stable brand files without it; no live findings | right as is |
| Page weight | no page over the JavaScript or CSS budget; no render-blocking scripts; self-hosted fonts | right as is |
| LCP | on the companies page the first large image, a 480×165 partner logo directly under the heading, has `loading="lazy"` (`lcp-image-lazy`, warn) | check in DevTools whether it is the LCP element on a phone; if so, drop `loading="lazy"` and add `fetchpriority="high"` |
| Lab gate | Lighthouse CI asserts performance ≥ 0.95, CLS ≤ 0.05 and byte budgets, but with the **desktop** preset | add a mobile run: field data and ranking use phones, and a desktop preset hides mobile problems; assert metrics with `median-run` rather than the category score |
| Lighthouse version | assertions such as `unused-javascript` are Lighthouse 12 audit names, which `@lhci/cli` 0.15.1 still bundles | pin `@lhci/cli`; rewrite the assertions when it moves to Lighthouse 13 insights |
| Field data | no CrUX key configured; a small site likely has no CrUX data | missing is not passing: rely on the site's own RUM |
| RUM | `Rum.astro` sends each metric from the plain `web-vitals` build as its own beacon, with `location.href` and a constant `version: "prod"` | see below |

## Improving the beacon

The component already does the hard part (cookieless, `sendBeacon`, started at idle). Four changes make its data diagnosable and safer, following the kit in [assets/rum/](assets/rum/):

1. **`web-vitals/attribution`** instead of `web-vitals`: adds LCP subparts, INP phases with the Long Animation Frame script, and the element selector, so a slow p75 points at a cause.
2. **`location.pathname` or a template name, not `location.href`**: query strings can carry personal data and blow up cardinality ([monitoring.md](monitoring.md#privacy-in-the-eu)).
3. **A build id** (the git sha) instead of `"prod"`, so p75 can be grouped by deploy and a regression pinned to a release.
4. **One beacon per page view** on `visibilitychange`, carrying all metrics and the rating, which cuts requests five-fold and keeps the values of one visit together.

## What to take from it

1. A fast static site still needs field data, and a small one needs its own RUM because CrUX has nothing.
2. A strict lab gate on the wrong device class gives false confidence.
3. Lab gates are tied to a Lighthouse major version; pin and migrate deliberately.
4. RUM is only useful if it carries attribution and a build id.
