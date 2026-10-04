# When another host wins

Cloudflare Workers + static assets is the default for a commercial static site: commercial use allowed, static requests unmetered, free DNS, Access for 50 users, KV/D1/R2/Queues/Durable Objects free tiers, and limits that fail with errors instead of invoicing. Its terms reserve the right to limit sites serving disproportionate video or large files: put media in R2 or Stream.

## Move away when

| Situation | Use |
|---|---|
| Client or company requires an EU-owned vendor and data path | **Bunny.net** (Slovenia): CDN + Storage + Edge Scripting, prepaid (≈ €1–5/month for a marketing site, no surprise invoice) |
| EU-owned, git-push, one small site, zero budget | **statichost.eu** (Sweden): free 1 site / 10 GB; previews and global CDN not finished |
| EU cloud, assemble it yourself | **Scaleway** (France): bucket website + Edge Services (€0.99/month) + Functions free allowance |
| Nameservers can't move to Cloudflare | Cloudflare **Pages** (external CNAME for subdomains) or any host below |
| Org already lives in AWS | **CloudFront flat-rate Free** (1M requests, 100 GB, no overage ever; not for accounts on the AWS Free Tier) |
| Needs built-in form handling and previews, low traffic | **Netlify** Free: 300 credits/month ≈ 15 GB, each production deploy costs 15; projects pause when credits run out |
| Open-source project docs | **GitHub Pages** / GitLab Pages / Codeberg Pages |

## Don't use for a company site

| Host | Reason |
|---|---|
| Vercel Hobby | non-commercial only, including a paid contractor building it |
| Codeberg Pages | free-licence content, FOSS projects |
| GitHub Pages | not for an online business, e-commerce or SaaS |
| Fly.io | no free tier for new orgs |
| Firebase Spark | no functions; ~10 GB/month transfer |
| Render / Fastly / Amplify with a card on file | overage bills automatically |

## Overage behaviour

| Hard stop (safe) | Auto-bills |
|---|---|
| Cloudflare, Netlify, Deno Deploy, Firebase Spark, Azure Static Web Apps, CloudFront flat-rate | Fastly, AWS Amplify, Render (card on file), Scaleway pay-as-you-go |

Bunny.net is prepaid: the account suspends at zero balance unless auto-recharge is on.

## Sources

cloudflare.com/terms · cloudflare.com/service-specific-terms-application-services · netlify.com/pricing · docs.netlify.com credit-based pricing · vercel.com/docs/plans/hobby · vercel.com/docs/limits/fair-use-guidelines · docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits · docs.codeberg.org/getting-started/faq · deno.com/deploy/pricing · firebase.google.com/pricing · render.com/docs/free · fastly.com/pricing · bunny.net/pricing · statichost.eu/pricing · scaleway.com/en/pricing · docs.aws.amazon.com CloudFront flat-rate-pricing-plan · learn.microsoft.com/azure/static-web-apps/plans · docs.fly.io/about/pricing
