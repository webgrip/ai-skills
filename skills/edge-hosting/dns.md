# DNS, hostnames, redirects and tokens

Contents: [hostname claimants](#every-hostname-needs-a-claimant) · [routes vs custom domains](#routes-vs-custom-domains) · [www and apex](#www-and-apex) · [DNS as code](#dns-as-code) · [zone settings](#free-zone-settings-worth-turning-on) · [API tokens](#api-tokens)

## Every hostname needs a claimant

A proxied record (orange cloud) sends traffic to Cloudflare's edge. Something at the edge must answer:

| Claimant | Use for |
|---|---|
| Worker route (`example.org/*`) | the site, on a zone that may still hold leftover records |
| Worker custom domain | the site, on a clean zone (DNS record and certificate managed for you) |
| Single redirect rule | `www`, old domains, vanity hosts |
| Tunnel CNAME (`<uuid>.cfargotunnel.com`) | a service in a private network → [access.md](access.md) |

No claimant → Cloudflare forwards to the record's origin. For a placeholder that is a **522 after ~20 s**; for a stale real IP it is someone else's server. Probe every hostname after a change: `python3 scripts/edge_check.py live example.org`.

Placeholder records: proxied `AAAA 100::` (discard prefix) or `A 192.0.2.1` (documentation range). Never a parking or registrar IP.

## Routes vs custom domains

- **Custom domain**: `{"pattern": "app.example.org", "custom_domain": true}`. Exact hostname, no wildcards, no path. Creates the proxied record and an Advanced Certificate (the certificate stays after the domain is removed). Fails with error 100117 when any A/AAAA/CNAME already exists on that name: delete the record first.
- **Route**: `{"pattern": "example.org/*", "zone_name": "example.org"}`. Needs a proxied record to exist. Intercepts in front of whatever that record points at, so it works on a zone mid-migration.
- A route that only covers `example.org/*` does not cover `www.example.org` or `mta-sts.example.org`; a route that does cover an extra hostname serves the whole site there (duplicate content).
- A fresh route can take a minute to propagate: smoke tests poll before asserting.
- Workers on custom domains in the same zone can `fetch()` each other directly.

## www and apex

Pick one canonical host (usually the apex). The other gets a **301** single redirect rule, keeping the path:

```
when:   http.host eq "www.example.org"
then:   301 → concat("https://example.org", http.request.uri.path)   preserve query string
```

`www` still needs a proxied record (placeholder) so the rule sees the request. DNSControl expresses this as `CF_SINGLE_REDIRECT(name, 301, when, then)` with the `cloudflare` provider's `manage_single_redirects: true`; the token then needs Zone › Single Redirect › Edit. Page Rules are deprecated and reject account-owned tokens.

## DNS as code

**One writer per record set.** Every tool diffs against the Cloudflare API, not `dig`, and deletes what it doesn't declare unless told to ignore it. Records Cloudflare manages itself (some CAA, `_domainconnect`) don't appear in the API; don't declare them.

| Tool | Fits | Notes |
|---|---|---|
| **DNSControl** | zone records + redirects in a JS file, preview on PR, push on main, nightly drift check | `IGNORE('@', 'A,AAAA,CNAME')` for names a Worker custom domain or route owns |
| **OpenTofu / Terraform** provider v5 | account objects: Access apps/policies, tunnels, zone settings, rulesets | v5 renamed 40+ resources (`cloudflare_record` → `cloudflare_dns_record`); `tf-migrate` + `moved` blocks; Access/Gateway resources still show plan drift after apply — pin the provider |
| **external-dns** | records for Kubernetes ingress/gateway hosts | annotation prefix is `external-dns.kubernetes.io/` (v0.22+); `--cloudflare-proxied`; `--zone-id-filter`; `txtPrefix` registry; token Zone Read + DNS Edit |
| **wrangler** | custom-domain records only | implicit; don't also declare them elsewhere |
| `cf-terraforming` | one-off import of click-ops state | not for CI |

A homelab external-dns owning a public site's apex couples the site's DNS to the cluster; keep public-site records in the DNS-as-code repo.

## Free zone settings worth turning on

- SSL/TLS Full (strict), Always Use HTTPS, minimum TLS 1.2, **HSTS** once every subdomain serves HTTPS (skip on HSTS-preloaded TLDs like `.dev`/`.app`, already enforced by browsers). HSTS is a zone setting, not code: record it in the DNS-as-code repo or a runbook.
- **DNSSEC** (free; add the DS record at the registrar).
- Web Analytics (cookieless) instead of a tracking script; Turnstile instead of a CAPTCHA.
- Email Routing for inbound aliases; SPF/DKIM/DMARC records in DNS as code.
- Bot Fight Mode only after checking API and form clients: it can't be skipped per path.
- Network Error Logging adds `report-to`/`nel` headers that report client errors to Cloudflare; turn it off if the privacy statement doesn't cover it.
- Registrar sells at cost but not every TLD (`.nl`, `.eu`, `.de`, `.be` are not offered); keep those at the current registrar and only move the nameservers.

## API tokens

Account-owned tokens (`cfat_` prefix) for CI: they survive the person leaving. They don't work for Page Rules or Registrar.

| Job | Permissions |
|---|---|
| Deploy a Worker with routes/custom domain | Account › Workers Scripts › Edit; Zone › Workers Routes › Edit on each zone (missing zone scope: upload succeeds, route binding fails) |
| + D1 / KV / R2 bindings | Account › D1 Edit / Workers KV Storage Edit / R2 Edit |
| DNS as code for one zone | Zone › Zone Read + DNS Edit on that zone (+ Single Redirect Edit if it manages redirects) |
| Access apps (private pages) | Account › Access: Apps and Policies Edit |
| external-dns | Zone › Zone Read + DNS Edit, zones filtered |

One token per consuming system, named after it; scoped to the zones it touches; rotated on a schedule. Where the token is stored and how CI receives it → the `secrets-levels` skill.
