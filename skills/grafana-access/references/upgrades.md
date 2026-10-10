# Grafana upgrades: version notes and API checks

The checklist itself is in SKILL.md. This file holds the version-specific facts it points to and the
API calls that prove an upgrade worked. Read the official upgrade guide for every minor version you
cross (`docs/sources/upgrade-guide/upgrade-vX.Y` in the Grafana repository); add to this file only
what that guide or a reproduced run confirms.

## Grafana 13

- **One-way storage migration.** The first 13.x start moves folders and dashboards from the legacy
  SQL tables into unified storage, once, recorded in `unifiedstorage_migration_log`. An older Grafana
  started afterwards reads the stale legacy tables; rolling back means restoring the database backup
  taken before the upgrade. Snapshot the volume first.
- **SQLite lock errors during that migration** (`database is locked`): Grafana retries with a Parquet
  buffer; if errors persist, raise `[unified_storage] migration_cache_size_kb` or enable
  `migration_parquet_buffer`, and give the pod the memory the cache needs.
- **Numeric-id datasource APIs are disabled** (deprecated since 9). Tools that address datasources by
  `id`, older operators and Terraform providers among them, break until upgraded; the feature flag
  `datasourceLegacyIdApi` re-enables them temporarily. Upgrade such clients before Grafana.
- **Bundled plugins on a read-only root filesystem.** With `[plugins] preinstall_auto_update` at its
  default `true`, Grafana 13 updates bundled plugins at startup by deleting them first; on a read-only
  filesystem that fails with `unlinkat …/plugins-bundled/<id>: read-only file system` and the plugin
  stays unregistered, so every panel on Prometheus, Loki, Tempo, PostgreSQL or MySQL answers "Plugin
  not registered". Set `preinstall_auto_update = false`; bundled plugins then move with the Grafana
  version.
- **Plugin install settings.** Pin external plugins as `id@version` in `[plugins] preinstall_sync`
  (`GF_PLUGINS_PREINSTALL_SYNC`) or `preinstall`. `GF_INSTALL_PLUGINS` is the deprecated older form;
  it still works and logs a warning.

## Plugin compatibility before a bump

No dependency bot reads the grafana.com plugin catalog, so check each pinned plugin by hand:

```sh
curl -s https://grafana.com/api/plugins/<plugin-id>/versions \
  | jq -r '.items[:6][] | "\(.version)  grafanaDependency=\(.grafanaDependency)"'
```

The pinned version's `grafanaDependency` range must include the target Grafana version. Panel plugins
that store `pluginVersion` inside the dashboard JSON (Business Text does) need the dashboards and the
install pin to move together.

## Prove the upgrade through the API

Over a port-forward, with a service-account token or the admin:

| Check | Call | Pass |
| --- | --- | --- |
| Version | `GET /api/health` | the target version, `database: ok` |
| Plugins loaded | `GET /api/plugins?embedded=0`, then `GET /api/plugins/<id>/settings` | every datasource type in use is listed; `.info.version` is the expected one |
| Datasources | `GET /api/datasources/uid/<uid>/health` | `status: OK` for each (the audit script's `--health`) |
| Real data | one `POST /api/ds/query` per datasource type | frames with values |
| Alertmanager | `GET /api/alertmanager/<uid>/api/v2/status` | 200; its health check always says "Plugin unavailable" because it has no backend |
| Operator sync | the `Grafana`, `GrafanaDashboard` and `GrafanaDatasource` status conditions | synchronised, no errors |
| Startup | logs | no `Failed to install plugin` |

`python3 scripts/grafana_access_audit.py --health` covers the plugin and datasource rows in one run
and flags any datasource whose plugin is missing.
