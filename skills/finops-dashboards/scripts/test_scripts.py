import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
UTC = ZoneInfo("UTC")


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


lint = load("dashboard_lint")
forecast = load("forecast")

UNFOLD_LIKE_INVENTORY = (
    [{"name": f"control-plane-{n}", "hourly": 0.0088, "monthly_cap": 5.49, "created": "2026-09-01T00:00:00Z"}
     for n in (1, 2, 3)]
    + [{"name": "worker-1", "hourly": 0.0136, "monthly_cap": 8.49, "created": "2026-09-01T00:00:00Z"},
       {"name": "headscale", "hourly": 0.0088, "monthly_cap": 5.49, "created": "2026-09-01T00:00:00Z"}]
    + [{"name": f"ipv4-{n}", "hourly": 0.0008, "monthly_cap": 0.50, "created": "2026-09-01T00:00:00Z"}
       for n in range(5)]
    + [{"name": "talos-snapshot", "hourly": 0.4289 * 0.0143 / 730, "monthly_cap": 0.4289 * 0.0143,
        "created": "2026-09-01T00:00:00Z"}]
)


def findings_for(dashboard: dict) -> set:
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "dashboard.json"
        path.write_text(json.dumps(dashboard))
        return {finding["rule"] for finding in lint.lint([str(path)])["findings"]}


def money_stat(**fields) -> dict:
    panel = {"id": 1, "type": "stat", "title": "Net cost", "description": "Net EUR.",
             "datasource": {"uid": "vm"}, "targets": [{"refId": "A", "expr": "sum(cost_eur)"}],
             "options": {"graphMode": "area"},
             "fieldConfig": {"defaults": {"unit": "currencyEUR", "decimals": 2}, "overrides": []}}
    panel.update(fields)
    return {"title": "t", "timezone": "utc", "panels": [panel]}


class PromqlHelpersTest(unittest.TestCase):
    def test_outer_aggregation_reads_by_before_and_after(self):
        self.assertEqual(lint.outer_aggregation("sum by (a, b) (x)"), ("sum", "by", {"a", "b"}))
        self.assertEqual(lint.outer_aggregation("sum(x) by (a)"), ("sum", "by", {"a"}))
        self.assertIsNone(lint.outer_aggregation("rate(x[5m])"))

    def test_metric_names_skip_labels_strings_and_functions(self):
        names = lint.metric_names('sum by (job) (rate(cost_eur_total{job="hcloud-cost"}[5m])) or vector(0)')
        self.assertEqual(names, ["cost_eur_total"])

    def test_enclosing_calls_see_through_by_clause(self):
        expr = "sum by (ns) (rate(x[5m]))"
        self.assertEqual(lint.enclosing_calls(expr, expr.index("rate")), ["sum"])

    def test_self_cancelling_ratio(self):
        self.assertTrue(lint.self_cancelling_ratio("sum(kube_pod_container_resource_requests) / sum(kube_node_status_allocatable)"))
        self.assertFalse(lint.self_cancelling_ratio("sum(kube_node_status_allocatable) * 0.03"))

    def test_unit_currency(self):
        self.assertEqual(lint.unit_currency("currencyEUR"), "EUR")
        self.assertEqual(lint.unit_currency("currency:financial:€"), "EUR")
        self.assertEqual(lint.unit_currency("currency:financial:€:suffix"), "EUR")
        self.assertEqual(lint.unit_currency("percent"), "")


class LintRulesTest(unittest.TestCase):
    def test_clean_money_stat_passes(self):
        self.assertEqual(findings_for(money_stat()), set())

    def test_count_of_cost_metric_is_not_money(self):
        dashboard = money_stat(targets=[{"refId": "A", "expr": "count(hcloud_cost_resource_hourly_eur)"}],
                               fieldConfig={"defaults": {"unit": "none"}, "overrides": []})
        self.assertEqual(findings_for(dashboard), set())

    def test_unit_price_may_carry_more_decimals(self):
        dashboard = money_stat(title="Cost per hour", fieldConfig={"defaults": {"unit": "currencyEUR", "decimals": 4}})
        self.assertEqual(findings_for(dashboard), set())

    def test_hourly_money_with_four_decimals_outside_unit_price_fires(self):
        dashboard = money_stat(fieldConfig={"defaults": {"unit": "currencyEUR", "decimals": 4}})
        self.assertEqual(findings_for(dashboard), {"currency-decimals"})

    def test_token_price_literal_is_not_vat(self):
        dashboard = money_stat(targets=[{"refId": "A", "expr": "sum(tokens_total) * 1.25 / 1e6 + sum(cost_eur)"}])
        self.assertNotIn("hardcoded-vat", findings_for(dashboard))

    def test_vat_word_makes_a_vat_literal(self):
        dashboard = money_stat(title="Spend incl. VAT", targets=[{"refId": "A", "expr": "sum(cost_eur) * 1.09"}])
        self.assertIn("hardcoded-vat", findings_for(dashboard))

    def test_topk_keeps_labels_for_the_legend(self):
        dashboard = money_stat(type="timeseries", title="Top pods",
                               targets=[{"refId": "A", "expr": "topk(5, cost_eur)", "legendFormat": "{{pod}}"}])
        self.assertNotIn("legend-label-dropped", findings_for(dashboard))

    def test_ksm_with_job_filter_is_not_double_counted(self):
        expr = 'sum(kube_node_status_allocatable{job="kube-state-metrics"}) * 0.03 + sum(cost_eur)'
        self.assertNotIn("double-counted-series", findings_for(money_stat(targets=[{"refId": "A", "expr": expr}])))

    def test_ratio_of_two_doubled_sums_is_exempt(self):
        expr = "sum(kube_pod_container_resource_requests) / sum(kube_node_status_allocatable)"
        dashboard = money_stat(title="Requests over allocatable", targets=[{"refId": "A", "expr": expr}],
                               fieldConfig={"defaults": {"unit": "percentunit"}, "overrides": []})
        self.assertNotIn("double-counted-series", findings_for(dashboard))

    def test_tile_that_shows_the_budget_needs_no_reference(self):
        dashboard = money_stat(title="Budget", targets=[{"refId": "A", "expr": "max(litellm_key_max_budget)"}])
        self.assertNotIn("budget-without-reference", findings_for(dashboard))

    def test_threshold_line_on_a_time_series_is_not_colour_only(self):
        dashboard = money_stat(type="timeseries", title="Hourly spend", fieldConfig={"defaults": {
            "unit": "currencyEUR", "decimals": 2, "custom": {"thresholdsStyle": {"mode": "line"}},
            "thresholds": {"steps": [{"color": "green", "value": None}, {"color": "red", "value": 5}]}}})
        self.assertNotIn("red-green-only", findings_for(dashboard))

    def test_sql_that_formats_money_as_text_is_not_a_money_panel(self):
        dashboard = money_stat(type="table", fieldConfig={"defaults": {}},
                               targets=[{"refId": "A", "rawSql": "SELECT 'spent ' || to_char(spend, '9.99') FROM t"}])
        self.assertEqual(findings_for(dashboard), set())

    def test_crd_block_scalar_and_unicode_titles_keep_line_numbers(self):
        dashboard = money_stat(title="Spend — net", fieldConfig={"defaults": {"unit": "currencyEUR"}})
        text = json.dumps(dashboard, indent=2)
        crd = "kind: GrafanaDashboard\nspec:\n  json: |-\n" + "\n".join("    " + line for line in text.split("\n"))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "d.yaml"
            path.write_text(crd)
            report = lint.lint([str(path)])
        finding = report["findings"][0]
        self.assertEqual(finding["rule"], "currency-decimals")
        self.assertIn("Spend", crd.split("\n")[finding["line"] - 1])

    def test_rule_table_is_unique(self):
        names = [name for name, _, _ in lint.RULES]
        self.assertEqual(len(names), len(set(names)))


class ForecastTest(unittest.TestCase):
    def test_linear_projection_halfway(self):
        moment = datetime(2026, 4, 16, 0, 0, tzinfo=UTC)
        result = forecast.linear_projection(15.0, moment)
        self.assertAlmostEqual(result["projected"], 30.0)

    def test_month_bounds_follow_the_billing_timezone(self):
        moment = forecast.parse_moment("2026-10-31T23:30:00Z", ZoneInfo("Europe/Amsterdam"))
        start, _ = forecast.month_bounds(moment)
        self.assertEqual(start.month, 11)

    def test_capped_projection_reproduces_a_full_month_of_the_inventory(self):
        moment = datetime(2026, 10, 25, 12, 30, tzinfo=UTC)
        result = forecast.capped_projection(UNFOLD_LIKE_INVENTORY, moment, UTC)
        self.assertAlmostEqual(result["full_month_run_rate"], 32.96, places=2)
        self.assertAlmostEqual(result["projected"], 32.96, places=2)
        self.assertLess(result["month_to_date"], result["projected"])

    def test_started_hours_round_up(self):
        created = datetime(2026, 10, 25, 8, 0, tzinfo=UTC)
        self.assertEqual(forecast.started_hours(created, datetime(2026, 10, 25, 12, 30, tzinfo=UTC)), 5)

    def test_cap_holds_for_a_server_created_on_the_first(self):
        resource = {"name": "s", "hourly": 0.0088, "monthly_cap": 5.49, "created": "2026-10-01T00:00:00Z"}
        row = forecast.capped_resource(resource, datetime(2026, 10, 31, 23, 0, tzinfo=UTC), UTC)
        self.assertEqual(row["month_to_date"], 5.49)

    def test_deleted_resource_stops_billing(self):
        resource = {"name": "tmp", "hourly": 1.0, "monthly_cap": 500, "created": "2026-10-02T00:00:00Z",
                    "deleted": "2026-10-02T03:10:00Z"}
        row = forecast.capped_resource(resource, datetime(2026, 10, 20, tzinfo=UTC), UTC)
        self.assertEqual((row["month_to_date"], row["projected"]), (4.0, 4.0))

    def test_daily_projection_band_and_anomaly(self):
        days = [(date(2026, 10, day), 10.0 + (day % 3) * 0.5) for day in range(1, 20)]
        days[9] = (date(2026, 10, 10), 60.0)
        result = forecast.daily_projection(days, datetime(2026, 10, 20, 9, tzinfo=UTC))
        self.assertEqual([a["day"] for a in result["anomalies"]], ["2026-10-10"])
        self.assertLess(result["low"], result["projected"])
        self.assertGreater(result["high"], result["projected"])

    def test_budget_breach_date(self):
        moment = datetime(2026, 10, 11, tzinfo=UTC)
        view = forecast.budget_view(62.0, 20.0, 40.0, moment)
        self.assertEqual(view["projected_breach"][:10], "2026-10-21")

    def test_money_uses_dutch_separators(self):
        self.assertEqual(forecast.money(1234.5), "€ 1.234,50")
        self.assertEqual(forecast.money(-0.456), "-€ 0,46")


if __name__ == "__main__":
    unittest.main()
