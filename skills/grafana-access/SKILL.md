---
name: grafana-access
description: Decides and enforces who sees which data in Grafana OSS - one org per confidentiality scope, generic OAuth org_mapping that keeps staff in the default org while a kiosk sees only its scope, per-scope orgs from git with grafana-operator, a kiosk identity per wall screen, snapshots and public dashboards off, safe major upgrades and plugin checks, and wall dashboards readable across the room, with a read-only access audit script. Use when asked who can see a Grafana dashboard or its data, to hide boards or data from a team, client or screen, to set up Grafana orgs, folders, teams or OAuth and SSO role or org mapping, when a user lands in the wrong org or loses access after login, a dashboard is not found for one person, when setting up a TV, wall display or kiosk, upgrading Grafana or grafana-operator, panels say Plugin not registered, an Infinity datasource says invalid API key, or when designing a wall or TV dashboard.
---

# Grafana access — who sees which data, and keeping it that way

## Decide first: confidentiality or noise?

- **Noise** (people want their own boards in front of them): home dashboards, folders, playlists.
  No orgs, no proxy.
- **Confidentiality** (clients, NDAs, per-person data): an enforced boundary per scope. In Grafana OSS
  the org is the only one, because every member, Viewers included, can query every datasource in
  the org. The scope model and the label-enforcing data proxy are in the agent-platform skill.

For confidentiality:

1. One org per scope (a team or client group, granted per person). Staff stay in the default org.
2. Each scope org's datasources reach data only through that scope's proxy credential. Boards whose
   source the proxy cannot filter stay out of scope orgs.
3. A credential stored in a datasource (token, password, header) is usable by every member of its
   org. Before adding or repairing one, decide whether every member should hold it.
4. Switch off snapshots and public dashboards (below); both carry data out of an org without login.
5. Audit the result: `python3 scripts/grafana_access_audit.py` (see [Audit](#audit)).

## Map OAuth groups to orgs

Generic OAuth `org_mapping` semantics in Grafana 13:

- Entries are `group:orgIdOrName[:Role]`, separated by spaces or commas; the role defaults to Viewer,
  `*` matches any group or every org, and `\:` escapes a colon.
- A user who matches any entry gets exactly the matched orgs and is **removed from every other org at
  each login** (an org's last admin is kept). A user who matches nothing lands in the default org with
  the `role_attribute_path` role.
- The `role_attribute_path` role is raised into **every** matched org (the higher role wins), so a
  `|| 'Editor'` fallback makes a kiosk Editor in its scope org. End the expression in `''`.
- Sync runs only at login. After a mapping change, revoke sessions: `POST /api/admin/users/<id>/logout`.
- Org names resolve once at startup and unresolved entries are skipped silently; Grafana never
  creates orgs from the mapping. Use numeric org ids.
- `role_attribute_strict = true` denies login when no role results, and one unresolvable entry
  empties the whole mapping. Keep it off until every entry resolves.

Keeping staff in org 1 while a kiosk sees only its scope needs a marker group, because by groups
alone a staff member who is also in a scope group looks exactly like the kiosk:

```ini
[auth.generic_oauth]
role_attribute_path = contains(groups, 'grafana-admins') && 'GrafanaAdmin' || ''
org_attribute_path = groups && [groups, [!contains(groups, 'grafana-kiosk') && 'grafana-org1-member' || 'none']][]
org_mapping = grafana-org1-member:1:Editor grafana-admins:1:Admin grafana-scope-b:2:Viewer
allow_assign_grafana_admin = true
```

`grafana-org1-member` and `none` are synthetic keys that must never be real IdP group names, and
`groups &&` stops a token without a groups claim from producing the staff key on its own.

## One org per scope, from git (grafana-operator)

grafana-operator v5 has no org resource: each `Grafana` resource writes into the org of its
credential. Manifests and API calls: [references/operator-orgs.md](references/operator-orgs.md).

1. An idempotent job per scope ensures the org, an **Admin** service account inside it and a token,
   stored with the org id in a Secret. It never deletes an org.
2. One external `Grafana` resource per scope org, using that token and carrying its **own** selector
   label, never the main instance's label.
3. Pin the main instance to the default org with `spec.client.headers: {X-Grafana-Org-Id: "1"}`.
4. Generate each scope's dashboard copies from one source with a CI check. Scope datasources keep
   the default org's uids and point at the proxy with the scope's credential.
5. Read the resources' status conditions after applying.

## Wall screens

- **Identity.** Each screen signs in as its own local IdP user holding only its scope group and the
  kiosk marker, never as a person's session. It then shows in audit logs as itself and disabling the
  user revokes it. Generate the password in-cluster into the vault, about 12 lowercase letters and
  digits so a TV remote can type it, and expect a sign-in per session lifetime.
- **Snapshots and public dashboards off** wherever access control matters. A snapshot copies data
  behind a URL without login (external snapshots upload it to another server) and any Editor can
  publish a public dashboard. List what exists first, per org (`GET /api/dashboard/snapshots`,
  `GET /api/dashboards/public-dashboards`), then:

  ```ini
  [snapshots]
  enabled = false
  external_enabled = false
  [public_dashboards]
  enabled = false
  ```

- **Readable from across the room.** Big numbers, not dense charts. One row per project, grouped
  under its client. Per environment, the deployed version and the time since that deploy. The age of
  the oldest item small beside each count. Zero as a faint dash.
- **Preview before it replaces a live board.** Push the JSON under a throwaway uid
  (`zz-preview-<uid>`) through the API, render it headlessly (Playwright) at the screen's resolution
  with `?kiosk` and a service-account bearer header, measure element boxes (`scrollHeight` greater
  than `clientHeight` means clipped), then delete the preview.
- **HTML panels** (Text, Business Text) inherit Grafana's CSS and variable interpolation: `.row` has
  `margin: 0 -16px`, so namespace your classes, and `$name` in panel content or CSS is replaced as a
  dashboard variable, so keep `$` out.

## Upgrades and plugins

- **Read-only root filesystem:** set `[plugins] preinstall_auto_update = false`. The default makes
  Grafana 13 delete bundled plugins at startup to update them, which fails and leaves Prometheus,
  Loki, Tempo and SQL datasources answering "Plugin not registered".
- **A major upgrade**, in order:
  1. Read the upgrade guide for every minor version crossed.
  2. Back up the database volume before the first start of the new major; some migrations are
     one-way.
  3. Upgrade the clients first (operator, Terraform provider, scripts) when the target removes an API
     they call.
  4. Check each pinned external plugin's `grafanaDependency` range on grafana.com; no dependency bot
     reads that catalog.
  5. Prove it through the API rather than "pod Running": version, loaded plugin versions, datasource
     health plus one real query per type, operator status conditions, no `Failed to install plugin`
     in the logs.

  Version notes and the exact calls: [references/upgrades.md](references/upgrades.md).
- **Secure field names.** A provisioned datasource with a misspelled secure field fails on every query
  and nothing warns at creation. Read the plugin's settings model: Infinity reads its key only from
  `secureJsonData.apiKeyValue`, with `jsonData.auth_method: apiKey`, `apiKeyKey` and `apiKeyType: header`.

## "I can't see it"

| Symptom | Meaning |
| --- | --- |
| A signed-in user opens `…?orgId=N` and gets "not found" (404) | not a member of org N; a membership question, not a missing board |
| API call with `X-Grafana-Org-Id: N` answers 403 | the same, through the API |
| Pages redirect to `/login` (302), `/api/*` answers 401 | not signed in |
| A user lost an org right after logging in | `org_mapping` matched them and removed the unmatched orgs |
| Every panel on one datasource says "Plugin not registered" | the plugin is not loaded (read-only update above, or never installed) |

Test as the target identity in a private window, so an existing IdP session does not answer instead.

## Audit

```bash
GRAFANA_ADMIN_AUTH='admin:…' python3 scripts/grafana_access_audit.py --url http://127.0.0.1:3000 \
  --kiosk-login '^tv-' [--health] [--json]
```

Read-only, as a server admin. It prints each org's members by role, its datasources with the
credentials every member can use, and its snapshots and public dashboards, then the findings. Exit 0
means no `error` or `warn` finding. `--health` also runs each datasource's health check.

| Finding | Fix |
| --- | --- |
| `snapshots-enabled`, `external-snapshots-enabled`, `public-dashboards-enabled` | switch them off as above |
| `snapshot-exists`, `public-dashboard-exists` | review and delete before switching the feature off |
| `org-mapping-by-name` | numeric org ids in `org_mapping` |
| `role-path-fallback` | end `role_attribute_path` in `''` |
| `kiosk-outside-scope` | the screen account is in the default org or above Viewer: fix its groups or the marker mapping |
| `org-not-audited` | the admin is not a member of that org; add it, then rerun |
| `datasource-plugin-missing`, `datasource-unhealthy` | install or unpin the plugin, fix the backend or credential |
| `infinity-api-key-field` | store the key as `secureJsonData.apiKeyValue`, or delete the datasource |
| `preinstall-auto-update` (note) | set it to false on a read-only image and pin plugin versions |
