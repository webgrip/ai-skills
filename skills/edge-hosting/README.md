# edge-hosting

Ship static sites, small Workers and private pages on Cloudflare's free edge tier, deployed so
they stay up: an assets-only Worker as the default shape, routes vs custom domains, a claimant for
every hostname (the 522 trap), www→apex redirects, DNS as code (DNSControl, OpenTofu,
external-dns), Zero Trust Access gating at Worker or hostname level, release-driven staging and
previews, least-privilege CI tokens, the free-plan limits that change decisions, and the
situations where Bunny.net, statichost.eu, CloudFront or Netlify win instead.

Ships:

- `scripts/edge_check.py` — stdlib linter for `wrangler.toml`/`wrangler.jsonc` (dead targets,
  TOML table capture, staging bound to production data, secrets in `vars`, …) and a live prober
  for 522s, www/apex canonicalisation, soft 404s and missing security headers.
- `assets/private-pages/` — a Worker plus `share.py` that publish one HTML page per recipient
  list behind its own Access application, validate the Access JWT against that page's audience,
  answer 410 after expiry and let KV delete the copy; tested offline (`node --test`,
  `python3 -m unittest`).

**Install:**

```text
/plugin install edge-hosting@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s edge-hosting`.

**Try:** "deploy this Astro site to Cloudflare", "www.example.org gives a 522", "review our
wrangler.toml", "put Access in front of staging", "send this proposal to a client as a private
page that expires in 30 days", "which free host should this marketing site go on?".
