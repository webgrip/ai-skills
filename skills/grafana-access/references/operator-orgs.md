# Per-scope Grafana orgs with grafana-operator

grafana-operator v5 has no org resource. Every API call it makes lands in the org of the credential
it uses, and it calls no server-admin endpoints. A scope org therefore needs its own credential and
its own `Grafana` resource pointing at the same server.

## 1. Converge job: org, service account, token

An idempotent CronJob (for example every 15 minutes) that never deletes an org. Per scope:

```sh
curl -fsS -u "$ADMIN" "$G/api/orgs/name/$SCOPE_NAME" \
  || curl -fsS -u "$ADMIN" -H 'Content-Type: application/json' -X POST "$G/api/orgs" -d "{\"name\":\"$SCOPE_NAME\"}"
curl -fsS -u "$ADMIN" -H "X-Grafana-Org-Id: $ORG_ID" -H 'Content-Type: application/json' \
  -X POST "$G/api/serviceaccounts" -d '{"name":"grafana-operator","role":"Admin"}'
curl -fsS -u "$ADMIN" -H "X-Grafana-Org-Id: $ORG_ID" -H 'Content-Type: application/json' \
  -X POST "$G/api/serviceaccounts/$SA_ID/tokens" -d "{\"name\":\"operator-$(date +%s)\"}"
```

- The admin that creates an org becomes its Admin, which is what lets the `X-Grafana-Org-Id` calls
  above work. A server admin who is not a member of an org gets 403 on that org's resources.
- The service account is **Admin** in its org, because the operator also writes datasources and
  folder permissions there.
- A token created without `secondsToLive` never expires. Test the stored token on each run and
  replace it when it fails.
- Write the token and the org id into a Secret per scope (`grafana-org-<scope>`).
- RBAC for the job: `create` on Secrets cannot be narrowed with `resourceNames`, so grant `create`
  alone and `get`, `patch`, `update` only on the named Secrets.
- First run: `kubectl create job --from=cronjob/<name> <name>-first-run`.

## 2. One external Grafana resource per scope org

```yaml
apiVersion: grafana.integreatly.org/v1beta1
kind: Grafana
metadata:
  name: grafana-org-scope-b
  labels:
    grafana.example.org/org: scope-b
spec:
  external:
    url: http://grafana-service.observability.svc.cluster.local:3000
    apiKey:
      name: grafana-org-scope-b
      key: token
```

Give it its own label and never the main instance's label: every dashboard, folder and datasource
whose `instanceSelector` matches the main label would otherwise also be written into the scope org.
An external resource only gets a health check from the operator (`/login/ping`,
`/api/frontend/settings`); read its status conditions after applying.

## 3. Pin the main instance to the default org

The main `Grafana` resource authenticates as the admin user and lands in whichever org that user has
active. Pin it:

```yaml
spec:
  client:
    headers:
      X-Grafana-Org-Id: "1"
```

Never reach a scope org by giving the operator server-admin credentials plus a different
`X-Grafana-Org-Id`; one credential per org keeps each resource in its org.
`GrafanaDatasource.spec.datasource.orgId` is deprecated and has no effect.

## 4. Fill each scope org

- Generate the scope's `GrafanaDashboard` resources from the one source: same JSON byte for byte,
  a name suffixed with the scope, `instanceSelector` on the scope label. Run the generator with
  `--check` in CI and in pre-commit so a copy never drifts.
- Give the scope's datasources the same `uid` as in the default org so the boards work unchanged,
  pointed at the filtering proxy with that scope's credential:

```yaml
apiVersion: grafana.integreatly.org/v1beta1
kind: GrafanaDatasource
metadata:
  name: prometheus-org-scope-b
spec:
  instanceSelector:
    matchLabels:
      grafana.example.org/org: scope-b
  valuesFrom:
    - targetPath: secureJsonData.basicAuthPassword
      valueFrom:
        secretKeyRef:
          name: proxy-user-boards-scope-b
          key: password
  datasource:
    uid: prometheus
    name: Prometheus
    type: prometheus
    access: proxy
    url: http://metrics-proxy.observability.svc.cluster.local:8427
    basicAuth: true
    basicAuthUser: boards-scope-b
    secureJsonData:
      basicAuthPassword: ${password}
```

  Where Flux post-build substitution runs over this manifest, write the placeholder `$${password}`.
- Leave out boards whose source the proxy cannot filter (an Alertmanager API, a SQL database
  without per-scope roles).
- Playlists are not operator resources; create them with the scope org's token from the same job.

## 5. Verify

- The scope org's health and datasources answer through its token.
- A query through the scope datasource returns only the scope (`count by (team) (...)`), and a
  query naming another scope returns nothing.
- The default org is unchanged: same dashboards, same datasources.
- `python3 scripts/grafana_access_audit.py` lists the scope org with only its members and its
  proxy credential.
