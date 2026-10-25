#!/usr/bin/env python3
import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

DESCRIPTION = (
    "Lint Grafana dashboards (raw JSON or GrafanaDashboard CRDs with spec.json) for defects that make "
    "a cost or FinOps panel wrong or misleading. Reads files only; contacts nothing."
)

SEVERITIES = ("note", "warn", "fail")

RULES = (
    ("currency-unit-missing", "fail", "money panel without a currency unit"),
    ("currency-mismatch", "fail", "currency unit disagrees with the metric's currency suffix"),
    ("cents-as-euros", "fail", "a cents series shown in a whole-currency unit without dividing by 100"),
    ("currency-decimals", "warn", "currency shown with automatic or non-standard decimals"),
    ("percent-scale", "fail", "a 0-1 ratio under unit percent, or a 0-100 value under percentunit"),
    ("no-value-as-zero", "fail", "missing data on a money panel renders as zero spend"),
    ("single-value-as-timeseries", "warn", "a period total or other single value drawn as a time series"),
    ("budget-without-reference", "fail", "a budget, forecast or run-rate figure with nothing to compare it to"),
    ("headline-without-comparison", "note", "a headline money number with no delta, threshold or trend"),
    ("missing-description", "warn", "money panel without a description of what the number includes"),
    ("rate-without-aggregation", "warn", "rate or increase returned per series instead of aggregated"),
    ("legend-label-dropped", "fail", "legend names a label the aggregation removed"),
    ("double-counted-series", "fail", "sum over a metric that two exporters publish under one name"),
    ("hardcoded-vat", "warn", "a VAT rate written into a query as a literal"),
    ("datasource-missing", "warn", "query without a datasource uid, or with an unresolved import input"),
    ("period-follows-picker", "warn", "a calendar-period figure computed over the time picker's range"),
    ("billing-timezone-browser", "note", "money dashboard whose period boundaries follow the viewer's browser"),
    ("missing-forecast", "warn", "spend-to-date dashboard with no forecast, run-rate or budget panel"),
    ("legacy-table-footer", "note", "table footer in the pre-12.2 options.footer shape"),
    ("non-additive-footer-sum", "fail", "table footer sums a percentage, ratio, average or unit price"),
    ("boolean-as-number", "note", "a 0/1 status shown as a bare number without value mappings"),
    ("red-green-only", "note", "red versus green is the only signal the panel gives"),
    ("gauge-for-money", "note", "radial gauge for a money figure"),
    ("pie-for-money", "note", "pie chart for comparing money amounts"),
)
RULE_SEVERITY = {name: severity for name, severity, _ in RULES}
RULE_SUMMARY = {name: summary for name, _, summary in RULES}
RULE_NUMBER = {name: index for index, (name, _, _) in enumerate(RULES, start=1)}

AGGREGATIONS = {"sum", "avg", "min", "max", "count", "group", "stddev", "stdvar", "count_values",
                "topk", "bottomk", "quantile", "limitk", "median"}
DEDUP_AGGREGATIONS = {"max", "min", "avg", "group", "median"}
COUNT_AGGREGATIONS = {"count", "count_values", "group"}
LABEL_DROPPING = {"sum", "avg", "min", "max", "count", "group", "stddev", "stdvar", "quantile", "median"}
VAT_RATES_ALONE = {"1.21", "1.19", "0.21", "0.19"}
VAT_WORDS = re.compile(r"\b(vat|btw|tax|gross|incl|bruto|mwst|ust)\b", re.IGNORECASE)
DATA_PANELS = {"stat", "gauge", "bargauge", "timeseries", "graph", "table", "barchart", "piechart", "singlestat",
               "state-timeline", "status-history", "xychart", "trend", "histogram", "heatmap"}
KEYWORDS = {"by", "without", "on", "ignoring", "group_left", "group_right", "offset", "bool", "and", "or",
            "unless", "inf", "nan", "keep_metric_names", "atan2"}
DUPLICATED_KSM_METRICS = re.compile(
    r"^kube_(node_status_(allocatable|capacity)|node_labels|pod_owner|pod_container_status_running"
    r"|pod_container_resource_requests|persistentvolume_capacity_bytes|persistentvolumeclaim_info)$")
MONEY_METRIC = re.compile(r"(^|_)(eur|euros?|usd|dollars?|gbp|cost|costs|spend|spent|price|prices|cents|billed)"
                          r"(_metric)?(_total|_sum)?$")
MONEY_WORDS = re.compile(r"\b(cost|costs|spend|spent|budget|price|prices|invoice|billing|billed|eur|euro|usd|"
                         r"kosten|uitgaven|factuur|prijs)\b|€", re.IGNORECASE)
SQL_MONEY_COLUMN = re.compile(r"\b(spend|spent|cost|costs|price|eur|usd|cents|\w+_(spend|cost|costs|price|eur|usd|cents))\b",
                              re.IGNORECASE)
SQL_MONEY_ALIAS = re.compile(r"\bas\s+\"?[\w ]*\b(spend|spent|cost|costs|price|eur|usd|cents)\b[\w ]*\"?",
                             re.IGNORECASE)
SQL_FORMATS_TEXT = re.compile(r"\|\||to_char\s*\(|chr\s*\(\s*36\s*\)|\bformat\s*\(|concat\s*\(", re.IGNORECASE)
UNIT_PRICE = re.compile(r"(\bper|/)\s*(hour|h|day|unit|token|tokens|1k|1m|million|gb|gib|tb|run|build|request|"
                        r"tenant|customer|core|vcpu|kwh|seat|user|ticket|session)\b|hourly|unit (cost|price)|"
                        r"price per|cost per|€\s*/|eur\s*/", re.IGNORECASE)
PERIOD_TOTAL = re.compile(r"month to date|month-to-date|\bmtd\b|this month|so far|\btotal\b|projected|forecast|"
                          r"end of month|run[- ]?rate|budget (left|remaining|used)|deze maand", re.IGNORECASE)
BUDGETISH = re.compile(r"budget|forecast|projected|projection|end of month|\beom\b|run[- ]?rate|burn[- ]?down|"
                       r"prognose", re.IGNORECASE)
MONTH_TO_DATE = re.compile(r"month to date|month-to-date|\bmtd\b|this month|month so far|deze maand",
                           re.IGNORECASE)
SPEND_TO_DATE = re.compile(r"month to date|month-to-date|\bmtd\b|this month|so far|spend|spent|kosten|uitgaven",
                           re.IGNORECASE)
FORECAST = re.compile(r"forecast|projected|projection|run[- ]?rate|end of month|\beom\b|budget|prognose|"
                      r"verwacht", re.IGNORECASE)
NON_ADDITIVE = re.compile(r"%|percent|ratio|share|\bavg\b|average|mean|efficiency|utili[sz]ation|"
                          r"unit (cost|price)|\bper\b|/", re.IGNORECASE)
VAT_LITERAL = re.compile(r"[*/]\s*(1\.(06|07|09|19|2|20|21|25|27)|0\.(09|19|21))(?![\d.])")
ZERO_TEXT = re.compile(r"^[^\d]*0+([.,]0+)?[^\d]*$")
CENTS_DIVISION = re.compile(r"/\s*100(\.0+)?\b|\*\s*0?\.01\b")
PERCENT_FACTOR = re.compile(r"\*\s*100\b|\b100\s*\*")
RED = re.compile(r"red|#(f2495c|e02f44|c4162a|ff7383|ffa6b0|d44a3a|bf1b00)", re.IGNORECASE)
GREEN = re.compile(r"green|#(73bf69|56a64b|37872d|96d98d|c8f2c2|299c46|7eb26d)", re.IGNORECASE)
NEUTRAL_COLOURS = {"transparent", "text", ""}
CURRENCY_SYMBOLS = {"€": "EUR", "$": "USD", "£": "GBP"}
METRIC_CURRENCY = (("_eur", "EUR"), ("_euro", "EUR"), ("_euros", "EUR"), ("_usd", "USD"), ("_dollars", "USD"),
                   ("_dollar", "USD"), ("_gbp", "GBP"))


@dataclass
class Finding:
    rule: str
    severity: str
    path: str
    line: int
    dashboard: str
    panel: str
    message: str


def strip_strings(expr: str) -> str:
    return re.sub(r'"(\\.|[^"\\])*"|\'(\\.|[^\'\\])*\'|`[^`]*`', '""', expr)


def matching_paren(text: str, open_index: int) -> int:
    depth = 0
    for index in range(open_index, len(text)):
        if text[index] == "(":
            depth += 1
        elif text[index] == ")":
            depth -= 1
            if depth == 0:
                return index
    return len(text) - 1


def name_before(text: str, open_index: int) -> str:
    head = text[:open_index].rstrip()
    if head.endswith(")"):
        depth, index = 0, len(head) - 1
        while index >= 0:
            if head[index] == ")":
                depth += 1
            elif head[index] == "(":
                depth -= 1
                if depth == 0:
                    break
            index -= 1
        clause = re.search(r"(\w+)\s*(by|without)\s*$", head[:index])
        return clause.group(1).lower() if clause else ""
    word = re.search(r"(\w+)\s*$", head)
    return word.group(1).lower() if word else ""


def enclosing_calls(text: str, position: int) -> list:
    stack = []
    for index in range(position):
        if text[index] == "(":
            stack.append(index)
        elif text[index] == ")" and stack:
            stack.pop()
    return [name_before(text, open_index) for open_index in reversed(stack)]


def selector_body(text: str, end: int) -> str:
    rest = text[end:]
    found = re.match(r"\s*\{([^}]*)\}", rest)
    return found.group(1) if found else ""


def metric_names(expr: str) -> list:
    cleaned = strip_strings(expr)
    cleaned = re.sub(r"\{[^}]*\}", "{}", cleaned)
    cleaned = re.sub(r"\b(by|without|on|ignoring|group_left|group_right)\s*\([^)]*\)", " ", cleaned)
    cleaned = re.sub(r"\[[^\]]*\]", " ", cleaned)
    cleaned = re.sub(r"\$\{?\w+\}?", " ", cleaned)
    names = []
    for found in re.finditer(r"(?<![\w.$])([a-zA-Z_:][\w:]*)(?![\w:])(?!\s*\()", cleaned):
        name = found.group(1)
        if name.lower() in KEYWORDS or name.lower() in AGGREGATIONS:
            continue
        names.append(name)
    return names


def outer_aggregation(expr: str):
    text = strip_strings(expr).strip()
    head = re.match(r"(\w+)\s*(?:(by|without)\s*\(([^)]*)\))?\s*\(", text)
    if not head or head.group(1).lower() not in AGGREGATIONS:
        return None
    name, mode, labels = head.group(1).lower(), head.group(2), head.group(3)
    close = matching_paren(text, head.end() - 1)
    if not mode:
        tail = re.match(r"\s*(by|without)\s*\(([^)]*)\)", text[close + 1:])
        if tail:
            mode, labels = tail.group(1), tail.group(2)
    grouping = {label.strip() for label in (labels or "").split(",") if label.strip()}
    return name, (mode or "").lower(), grouping


def top_level_split(text: str, operator: str) -> list:
    parts, depth, start = [], 0, 0
    for index, char in enumerate(text):
        if char in "({[":
            depth += 1
        elif char in ")}]":
            depth -= 1
        elif char == operator and depth == 0:
            parts.append(text[start:index])
            start = index + 1
    parts.append(text[start:])
    return parts


def self_cancelling_ratio(expr: str) -> bool:
    sides = top_level_split(expr, "/")
    if len(sides) != 2:
        return False
    return all(any(DUPLICATED_KSM_METRICS.match(name) for name in metric_names(side)) for side in sides)


def is_count_like(expr: str) -> bool:
    aggregation = outer_aggregation(expr)
    return bool(aggregation) and aggregation[0] in COUNT_AGGREGATIONS


def expr_of(target: dict) -> str:
    return target.get("expr") or target.get("query") or ""


def sql_of(target: dict) -> str:
    return target.get("rawSql") or ""


def unit_currency(unit: str) -> str:
    if not unit:
        return ""
    if unit.startswith("currency") and len(unit) == len("currency") + 3 and unit[8:].isupper():
        return unit[8:]
    if unit.startswith("currency:"):
        symbol = unit.split(":")[-1] if unit.count(":") == 1 else unit.split(":")[2]
        return CURRENCY_SYMBOLS.get(symbol, symbol.upper())
    return ""


def metric_currencies(names: list) -> set:
    found = set()
    for name in names:
        bare = re.sub(r"(_metric)?(_total|_sum)?$", "", name.lower())
        for suffix, code in METRIC_CURRENCY:
            if bare.endswith(suffix):
                found.add(code)
    return found


def flatten_panels(panels: list) -> list:
    flat = []
    for panel in panels or []:
        flat.append(panel)
        if panel.get("type") == "row":
            flat.extend(panel.get("panels") or [])
    return flat


class Panel:
    def __init__(self, raw: dict):
        self.raw = raw
        self.type = raw.get("type", "")
        self.title = raw.get("title") or ""
        self.description = raw.get("description") or ""
        self.targets = [target for target in raw.get("targets") or [] if isinstance(target, dict)]
        field_config = raw.get("fieldConfig") or {}
        self.defaults = field_config.get("defaults") or {}
        self.overrides = field_config.get("overrides") or []
        self.options = raw.get("options") or {}

    @property
    def exprs(self) -> list:
        return [expr_of(target) for target in self.targets if expr_of(target)]

    @property
    def sqls(self) -> list:
        return [sql_of(target) for target in self.targets if sql_of(target)]

    def override_entries(self) -> list:
        entries = []
        for override in self.overrides:
            matcher = override.get("matcher") or {}
            properties = {prop.get("id"): prop.get("value") for prop in override.get("properties") or []}
            entries.append((matcher.get("id", ""), matcher.get("options"), properties))
        return entries

    def units(self) -> set:
        found = {self.defaults.get("unit") or ""}
        for _, _, properties in self.override_entries():
            if "unit" in properties:
                found.add(properties["unit"] or "")
        return found - {""}

    def currency_columns(self) -> list:
        columns = []
        default_unit = self.defaults.get("unit") or ""
        default_decimals = self.defaults.get("decimals")
        currency_matchers = []
        if unit_currency(default_unit):
            columns.append((self.title, default_unit, default_decimals))
        for matcher_id, matcher_options, properties in self.override_entries():
            if unit_currency(properties.get("unit") or ""):
                label = matcher_label(matcher_options)
                currency_matchers.append((matcher_id, matcher_options))
                columns.append((label, properties["unit"], properties.get("decimals", default_decimals)))
        for matcher_id, matcher_options, properties in self.override_entries():
            if "decimals" in properties and "unit" not in properties:
                label = matcher_label(matcher_options)
                covered = any(matcher_covers(matcher, options, label) for matcher, options in currency_matchers)
                if covered or unit_currency(default_unit):
                    columns.append((label, default_unit or "currency", properties["decimals"]))
        return columns

    def thresholds_steps(self) -> list:
        return ((self.defaults.get("thresholds") or {}).get("steps")) or []

    def reference_steps(self) -> list:
        return [step for step in self.thresholds_steps() if step.get("value") is not None]

    def money_metrics(self) -> bool:
        for expr in self.exprs:
            if is_count_like(expr):
                continue
            if any(MONEY_METRIC.search(name.lower()) for name in metric_names(expr)):
                return True
        return any(sql_returns_money(sql) for sql in self.sqls)

    def is_money(self) -> bool:
        if self.type not in DATA_PANELS:
            return False
        if any(unit_currency(unit) for unit in self.units()):
            return True
        if self.units() & {"percent", "percentunit", "none", "short", "s", "h", "d", "bytes", "decbytes"}:
            return False
        return self.money_metrics()

    def is_unit_price(self, label: str = "") -> bool:
        return bool(UNIT_PRICE.search(self.title) or (label and UNIT_PRICE.search(label)))


def sql_returns_money(sql: str) -> bool:
    if SQL_MONEY_ALIAS.search(sql):
        return True
    return bool(SQL_MONEY_COLUMN.search(sql)) and not SQL_FORMATS_TEXT.search(sql)


def matcher_label(options) -> str:
    if isinstance(options, dict):
        return ",".join(options.get("names") or []) or str(options.get("pattern") or "")
    return str(options or "")


def matcher_covers(matcher_id: str, options, label: str) -> bool:
    pattern = matcher_label(options)
    if matcher_id == "byRegexp":
        try:
            return re.fullmatch(pattern, label) is not None
        except re.error:
            return False
    if matcher_id in ("byName", "byNames"):
        return label in pattern.split(",")
    return False


class Linter:
    def __init__(self, path: str, line_offset: int, text: str, dashboard: dict, decimals: int):
        self.path = path
        self.line_offset = line_offset
        self.text = text
        self.dashboard = dashboard
        self.decimals = decimals
        self.findings = []
        self.search_from = 0
        self.title = dashboard.get("title") or dashboard.get("uid") or "untitled"

    def line_of(self, panel: Panel) -> int:
        if panel.title:
            for ascii_only in (False, True):
                encoded = json.dumps(panel.title, ensure_ascii=ascii_only)
                found = re.compile(r'"title"\s*:\s*' + re.escape(encoded)).search(self.text, self.search_from)
                if found:
                    self.search_from = found.end()
                    return self.line_offset + self.text.count("\n", 0, found.start()) + 1
        return self.line_offset + 1

    def add(self, rule: str, line: int, panel: str, message: str) -> None:
        self.findings.append(Finding(rule, RULE_SEVERITY[rule], self.path, line, self.title, panel, message))

    def run(self) -> list:
        panels = [Panel(raw) for raw in flatten_panels(self.dashboard.get("panels"))]
        money_panels = []
        for panel in panels:
            line = self.line_of(panel)
            label = panel.title or f"panel {panel.raw.get('id', '?')}"
            if panel.is_money():
                money_panels.append(panel)
                self.money_rules(panel, line, label)
            self.query_rules(panel, line, label)
            self.display_rules(panel, line, label)
        self.dashboard_rules(panels, money_panels)
        return self.findings

    def money_rules(self, panel: Panel, line: int, label: str) -> None:
        units = panel.units()
        currencies = {unit_currency(unit) for unit in units} - {""}
        if not currencies and panel.type not in ("row", "text"):
            if not units & {"percent", "percentunit"}:
                self.add("currency-unit-missing", line, label,
                         f"shows money but unit is {sorted(units) or 'unset'}; set currencyEUR or "
                         "currency:financial:€ on the money fields")
        names = [name for expr in panel.exprs for name in metric_names(expr)]
        declared = metric_currencies(names)
        if currencies and declared and not currencies & declared and not any("*" in e for e in panel.exprs):
            self.add("currency-mismatch", line, label,
                     f"metric is in {sorted(declared)} but the unit shows {sorted(currencies)}")
        sources = panel.exprs + panel.sqls
        if currencies and any(re.search(r"cents?\b|_cents?_", source, re.IGNORECASE) for source in sources):
            if not any(CENTS_DIVISION.search(source) for source in sources):
                self.add("cents-as-euros", line, label, "a cents series under a currency unit; divide by 100")
        for column, unit, decimals in panel.currency_columns():
            unit_price = panel.is_unit_price(column)
            if decimals is None:
                self.add("currency-decimals", line, label,
                         f"{column or 'value'} uses automatic decimals, which Grafana truncates (100.456 shows as 100)")
            elif unit_price and decimals < self.decimals:
                self.add("currency-decimals", line, label, f"unit price {column} with {decimals} decimals")
            elif not unit_price and decimals != self.decimals:
                self.add("currency-decimals", line, label,
                         f"{column or 'value'} shows {decimals} decimals; money uses {self.decimals}")
        no_value = str(panel.defaults.get("noValue", "")).strip()
        if no_value and ZERO_TEXT.match(no_value):
            self.add("no-value-as-zero", line, label,
                     f'noValue "{no_value}" makes missing data look like zero spend')
        context = f"{panel.title} {panel.description}"
        has_reference = (len(panel.reference_steps()) >= 1 or len(panel.targets) >= 2
                         or panel.defaults.get("max") is not None)
        budget_flagged = False
        shows_the_budget = any("budget" in name.lower() for e in panel.exprs for name in metric_names(e))
        if (panel.type in ("stat", "gauge", "bargauge") and BUDGETISH.search(panel.title)
                and not has_reference and not shows_the_budget):
            budget_flagged = True
            self.add("budget-without-reference", line, label,
                     "a forecast or budget figure needs the budget as a threshold, a max or a second query")
        if (panel.type == "stat" and not budget_flagged and not panel.is_unit_price()
                and len(panel.targets) <= 1 and not panel.reference_steps()
                and not panel.options.get("showPercentChange")
                and panel.options.get("graphMode", "area") == "none"):
            self.add("headline-without-comparison", line, label,
                     "add a delta against the same point last period, a budget threshold or a sparkline")
        if not panel.description.strip():
            self.add("missing-description", line, label,
                     "say what the number includes: net or gross, amortized or billed, which period")
        if panel.type in ("timeseries", "graph"):
            instant = panel.targets and all(target.get("instant") and not target.get("range")
                                            for target in panel.targets)
            single = panel.exprs and all((outer_aggregation(e) or ("", "", {"x"}))[2] == set()
                                         and (outer_aggregation(e) or ("", "x", set()))[1] == ""
                                         for e in panel.exprs)
            if instant or (PERIOD_TOTAL.search(context) and single):
                self.add("single-value-as-timeseries", line, label,
                         "a period total is one number; use a stat (with a sparkline if the trend matters)")
        if MONTH_TO_DATE.search(panel.title) and any("$__range" in e for e in panel.exprs + panel.sqls):
            panel_from = str(panel.raw.get("timeFrom") or "")
            dashboard_from = str((self.dashboard.get("time") or {}).get("from") or "")
            if not panel_from.startswith("now/M") and dashboard_from != "now/M":
                self.add("period-follows-picker", line, label,
                         "the month-to-date figure changes with the time picker; pin timeFrom now/M or "
                         "compute it from day_of_month()")
        if panel.type == "gauge":
            self.add("gauge-for-money", line, label, "use a bar gauge or a stat with budget thresholds")
        if panel.type == "piechart":
            self.add("pie-for-money", line, label, "compare amounts in a sorted table or bar chart")

    def query_rules(self, panel: Panel, line: int, label: str) -> None:
        for target in panel.targets:
            expr = expr_of(target)
            sql = sql_of(target)
            if self.vat_literal(panel, strip_strings(expr) + " " + sql):
                self.add("hardcoded-vat", line, label,
                         "a VAT factor is a literal; keep money net and apply VAT from a labelled constant or variable")
            if not expr:
                continue
            cleaned = strip_strings(expr)
            for found in re.finditer(r"\b(rate|irate|increase)\s*\(", cleaned if panel.is_money() else ""):
                calls = enclosing_calls(cleaned, found.start())
                if not any(call in AGGREGATIONS for call in calls):
                    self.add("rate-without-aggregation", line, label,
                             f"{found.group(1)}() is not aggregated; series churn per pod and footers or stacks add them up")
                    break
            for found in re.finditer(r"(?<![\w:])([a-zA-Z_:][\w:]*)", "" if self_cancelling_ratio(cleaned) else cleaned):
                if not DUPLICATED_KSM_METRICS.match(found.group(1)):
                    continue
                if "job" in selector_body(cleaned, found.end()):
                    continue
                calls = [call for call in enclosing_calls(cleaned, found.start()) if call in AGGREGATIONS]
                if calls and calls[0] in {"sum", "count"}:
                    self.add("double-counted-series", line, label,
                             f"{found.group(1)} can be published by kube-state-metrics and by OpenCost; "
                             "filter on job (check count by (job)) or deduplicate with max by before summing")
                    break
            legend = target.get("legendFormat") or ""
            wanted = set(re.findall(r"\{\{\s*(\w+)\s*\}\}", legend))
            aggregation = outer_aggregation(expr)
            if wanted and aggregation and aggregation[0] in LABEL_DROPPING and aggregation[1] != "without":
                dropped = wanted - aggregation[2]
                if dropped:
                    self.add("legend-label-dropped", line, label,
                             f"legend uses {sorted(dropped)} but {aggregation[0]} keeps only {sorted(aggregation[2])}")
        self.datasource_rule(panel, line, label)
        units = panel.units()
        for expr in panel.exprs:
            cleaned = strip_strings(re.sub(r"\[[^\]]*\]", "", expr))
            divides = re.search(r"\)\s*/|\}\s*/|\w\s*/\s*[\w(]", cleaned) is not None
            if "percent" in units and divides and not PERCENT_FACTOR.search(cleaned):
                self.add("percent-scale", line, label, "a ratio under unit percent shows 0.8 as 0.8 %; use percentunit")
                break
            if "percentunit" in units and PERCENT_FACTOR.search(cleaned):
                self.add("percent-scale", line, label, "a value multiplied by 100 under percentunit shows 80 as 8000 %")
                break

    def vat_literal(self, panel: Panel, source: str) -> bool:
        context = f"{panel.title} {panel.description} {source}"
        for found in VAT_LITERAL.finditer(source):
            if found.group(1) in VAT_RATES_ALONE or VAT_WORDS.search(context):
                return True
        return False

    def datasource_rule(self, panel: Panel, line: int, label: str) -> None:
        if not panel.targets:
            return
        variables = {variable.get("name") for variable in (self.dashboard.get("templating") or {}).get("list") or []}
        for target in panel.targets:
            source = target.get("datasource") or panel.raw.get("datasource")
            uid = source.get("uid") if isinstance(source, dict) else None
            if isinstance(source, dict) and source.get("uid") in ("-- Mixed --",):
                uid = None
            if not uid:
                self.add("datasource-missing", line, label,
                         "pin the datasource by uid so the panel survives a datasource rename")
                return
            reference = re.fullmatch(r"\$\{?(\w+)(:\w+)?\}?", str(uid))
            if reference and reference.group(1) not in variables:
                self.add("datasource-missing", line, label,
                         f"uid {uid} is an import input with no matching variable; map it to a real uid")
                return

    def display_rules(self, panel: Panel, line: int, label: str) -> None:
        if panel.type == "table":
            legacy = panel.options.get("footer")
            if isinstance(legacy, dict):
                self.add("legacy-table-footer", line, label,
                         "Grafana 12.2+ rewrites options.footer on load; keep fieldConfig custom.footer.reducers in git")
            summed = self.summed_footer_fields(panel)
            offending = sorted(name for name in summed if NON_ADDITIVE.search(name) and not
                               re.search(r"hourly|per hour", name, re.IGNORECASE))
            percent_columns = [name for name in self.percent_columns(panel) if name in summed or "*" in summed]
            if offending or percent_columns:
                self.add("non-additive-footer-sum", line, label,
                         f"footer sums {sorted(set(offending + percent_columns))}; use mean or no reducer for those")
        mappings = panel.raw.get("fieldConfig", {}).get("defaults", {}).get("mappings") or []
        steps = panel.thresholds_steps()
        if panel.type == "stat" and not mappings:
            values = {step.get("value") for step in steps if step.get("value") is not None}
            looks_boolean = (re.search(r"\b[01]\s*=", panel.description) or
                             any(re.match(r"\s*(min|max)?\s*\(?\s*up\b", e) for e in panel.exprs))
            if values and values <= {0, 1} and looks_boolean:
                self.add("boolean-as-number", line, label,
                         "map 0 and 1 to words (OK, Rejected) so the tile reads without its description")
        colours = [str(step.get("color", "")).lower() for step in steps]
        meaningful = [colour for colour in colours if colour not in NEUTRAL_COLOURS]
        only_red_green = (meaningful and any(RED.search(c) for c in meaningful)
                          and any(GREEN.search(c) for c in meaningful)
                          and all(RED.search(c) or GREEN.search(c) for c in meaningful))
        colour_carries = (
            (panel.type == "stat" and panel.options.get("textMode") == "none")
            or panel.type in ("state-timeline", "status-history")
            or (panel.type in ("timeseries", "graph") and
                "area" in ((panel.defaults.get("custom") or {}).get("thresholdsStyle") or {}).get("mode", "off"))
        )
        if only_red_green and colour_carries:
            self.add("red-green-only", line, label,
                     "about 1 in 12 men cannot tell these apart; add text, a shape, or a blue/orange pair")

    def summed_footer_fields(self, panel: Panel) -> set:
        summed = set()
        legacy = panel.options.get("footer")
        if isinstance(legacy, dict) and legacy.get("show") and "sum" in (legacy.get("reducer") or []):
            fields = legacy.get("fields")
            if isinstance(fields, list) and fields:
                summed.update(fields)
            else:
                summed.add("*")
        default_footer = ((panel.defaults.get("custom") or {}).get("footer") or {}).get("reducers") or []
        if "sum" in default_footer:
            summed.add("*")
        for _, matcher_options, properties in panel.override_entries():
            if "sum" in (properties.get("custom.footer.reducers") or []):
                summed.update(matcher_label(matcher_options).split(","))
        if "*" in summed:
            summed.update(self.renamed_columns(panel))
        return summed

    def renamed_columns(self, panel: Panel) -> set:
        names = set()
        for transformation in panel.raw.get("transformations") or []:
            renames = (transformation.get("options") or {}).get("renameByName") or {}
            names.update(renames.values())
        return names

    def percent_columns(self, panel: Panel) -> list:
        names = []
        for _, matcher_options, properties in panel.override_entries():
            if properties.get("unit") in ("percent", "percentunit"):
                names.append(matcher_label(matcher_options))
        return names

    def dashboard_rules(self, panels: list, money_panels: list) -> None:
        if not money_panels:
            return
        line = self.line_offset + 1
        timezone = self.dashboard.get("timezone")
        if timezone in (None, "", "browser"):
            self.add("billing-timezone-browser", line, "(dashboard)",
                     "month boundaries follow each viewer's browser; set timezone to the billing timezone (often utc)")
        spend = [panel for panel in money_panels if SPEND_TO_DATE.search(panel.title)]
        forecast = [panel for panel in panels if FORECAST.search(panel.title)]
        if spend and not forecast:
            self.add("missing-forecast", line, "(dashboard)",
                     "spend to date without a projection; add projected end of period against the budget")


def block_scalar(lines: list, start: int, indent: int) -> tuple:
    body = []
    index = start
    while index < len(lines):
        line = lines[index]
        if line.strip() and len(line) - len(line.lstrip()) <= indent:
            break
        body.append(line)
        index += 1
    content = [line for line in body if line.strip()]
    if not content:
        return "", index
    margin = min(len(line) - len(line.lstrip()) for line in content)
    return "\n".join(line[margin:] for line in body), index


def dashboards_in_yaml(text: str) -> tuple:
    lines = text.split("\n")
    found, skipped = [], []
    for index, line in enumerate(lines):
        header = re.match(r"^(\s*)(json|gzipJson):\s*(.*)$", line)
        if not header:
            continue
        indent, key, rest = len(header.group(1)), header.group(2), header.group(3).strip()
        if key == "gzipJson":
            skipped.append((index + 1, "gzipJson is compressed; decompress to lint"))
            continue
        if re.fullmatch(r"[|>][-+]?\d*", rest):
            body, _ = block_scalar(lines, index + 1, indent)
            found.append((index + 1, body))
        elif rest.startswith("{"):
            found.append((index, rest))
        else:
            skipped.append((index + 1, "json value is not a block scalar"))
    return found, skipped


def load_targets(path: Path) -> tuple:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return [(0, text)], []
    return dashboards_in_yaml(text)


def collect_files(paths: list) -> list:
    files = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*") if p.suffix in (".json", ".yaml", ".yml") and p.is_file()))
        elif path.is_file():
            files.append(path)
    return files


def lint(paths: list, decimals: int = 2) -> dict:
    findings, skipped, dashboards, panels = [], [], 0, 0
    for path in collect_files(paths):
        try:
            sources, unreadable = load_targets(path)
        except (OSError, UnicodeDecodeError) as error:
            skipped.append({"path": str(path), "reason": f"unreadable: {error}"})
            continue
        skipped.extend({"path": f"{path}:{line}", "reason": reason} for line, reason in unreadable)
        if not sources and path.suffix != ".json":
            skipped.append({"path": str(path), "reason": "no GrafanaDashboard json found"})
        for offset, body in sources:
            try:
                dashboard = json.loads(body)
            except json.JSONDecodeError as error:
                skipped.append({"path": f"{path}:{offset + error.lineno}", "reason": f"not parsed: {error.msg}"})
                continue
            if isinstance(dashboard, dict) and "dashboard" in dashboard and "panels" not in dashboard:
                dashboard = dashboard["dashboard"]
            if not isinstance(dashboard, dict) or "panels" not in dashboard:
                skipped.append({"path": str(path), "reason": "json is not a dashboard"})
                continue
            dashboards += 1
            panels += len(flatten_panels(dashboard.get("panels")))
            findings.extend(Linter(str(path), offset, body, dashboard, decimals).run())
    return {
        "findings": [asdict(finding) for finding in findings],
        "coverage": {"files": len(collect_files(paths)), "dashboards": dashboards, "panels": panels,
                     "skipped": skipped},
        "cannot_see": [
            "whether the query returns data, or the right data: run it against the datasource",
            "whether a budget literal matches the alert rule that enforces it",
            "how the panel renders: check the dashboard in a browser at the width people use",
        ],
    }


def print_text(report: dict) -> None:
    for finding in report["findings"]:
        print(f"{finding['severity']:<4} {finding['rule']:<28} {finding['path']}:{finding['line']}  "
              f"[{finding['panel']}] {finding['message']}  -> checks.md#{finding['rule']}")
    coverage = report["coverage"]
    print(f"\n{len(report['findings'])} findings in {coverage['dashboards']} dashboards, "
          f"{coverage['panels']} panels, {coverage['files']} files")
    for entry in coverage["skipped"]:
        print(f"skipped {entry['path']}: {entry['reason']}")
    print("cannot see: " + "; ".join(report["cannot_see"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on", choices=SEVERITIES + ("never",), default="fail")
    parser.add_argument("--decimals", type=int, default=2)
    parser.add_argument("--rules", action="store_true")
    args = parser.parse_args()
    if args.rules:
        rules = [{"number": RULE_NUMBER[name], "name": name, "severity": severity, "summary": summary}
                 for name, severity, summary in RULES]
        print(json.dumps(rules, indent=2) if args.json else
              "\n".join(f"{r['number']:>2} {r['severity']:<4} {r['name']:<28} {r['summary']}" for r in rules))
        return 0
    if not args.paths:
        parser.error("give at least one file or directory")
    report = lint(args.paths, args.decimals)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    if args.fail_on == "never":
        return 0
    threshold = SEVERITIES.index(args.fail_on)
    return 1 if any(SEVERITIES.index(f["severity"]) >= threshold for f in report["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
