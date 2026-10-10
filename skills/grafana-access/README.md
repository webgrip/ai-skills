# grafana-access

Decide and enforce who sees which data in Grafana OSS over VictoriaMetrics or Prometheus. Starts
from the question that decides whether any plumbing is needed (confidentiality or noise), then: one
org per confidentiality scope, because the org is the only data boundary in OSS; generic OAuth
`org_mapping` semantics, including the marker-group pattern that keeps staff in the default org
while a wall-screen kiosk sees only its scope; per-scope orgs from git with grafana-operator; a
kiosk identity per screen; snapshots and public dashboards off; major upgrades proven through the
API, including the Grafana 13 read-only plugin trap; and wall dashboards readable across the room.
The label-enforcing data proxy behind the scope orgs lives in the agent-platform skill.

Ships:

- `scripts/grafana_access_audit.py` — stdlib, read-only audit as a server admin: members by role,
  datasources and the credentials every member can use, snapshots and public dashboards per org,
  plus findings for OAuth mapping traps, kiosks outside their scope, missing plugins, misnamed
  Infinity keys and (with `--health`) failing datasources. Tested against fixtures recorded from
  Grafana 13.

**Install:**

```text
/plugin install grafana-access@ai-skills
```

or `npx skills add https://forgejo.webgrip.dev/webgrip/ai-skills.git -s grafana-access`.

**Try:** "team B must not see team C's Grafana data", "set up a wall TV for our team's playlist
without my account", "people lose the Main Org after login since we added org_mapping", "every
panel says Plugin not registered after the upgrade", "audit who can see what in our Grafana",
"make this wall dashboard readable from across the room".
