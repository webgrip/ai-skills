#!/usr/bin/env python3
import argparse
import csv
import json
import math
import statistics
import sys
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

DESCRIPTION = (
    "Project month-end spend three ways: linear run-rate from month to date, per-resource hourly billing "
    "capped at a monthly price (Hetzner Cloud style), and a daily-series projection with an uncertainty band "
    "and robust anomaly flags. Reads local input only."
)
SECONDS_PER_HOUR = 3600
MODIFIED_Z_CONSTANT = 0.6745
MODIFIED_Z_THRESHOLD = 3.5
NORMAL_95 = 1.96


def parse_moment(value: str, zone: ZoneInfo) -> datetime:
    moment = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return moment.replace(tzinfo=zone) if moment.tzinfo is None else moment.astimezone(zone)


def month_bounds(moment: datetime) -> tuple:
    start = moment.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    following = (start + timedelta(days=32)).replace(day=1)
    return start, following


def money(value: float, symbol: str = "€") -> str:
    sign = "-" if value < 0 else ""
    whole, cents = f"{abs(value):,.2f}".split(".")
    return f"{sign}{symbol} {whole.replace(',', '.')},{cents}"


def linear_projection(month_to_date: float, moment: datetime) -> dict:
    start, end = month_bounds(moment)
    elapsed = (moment - start).total_seconds()
    length = (end - start).total_seconds()
    if elapsed <= 0:
        raise ValueError("the moment is at the start of the month; nothing to extrapolate")
    return {"month_start": start.isoformat(), "month_end": end.isoformat(),
            "elapsed_fraction": elapsed / length, "projected": month_to_date * length / elapsed}


def budget_view(projected: float, month_to_date: float, budget: float, moment: datetime) -> dict:
    start, end = month_bounds(moment)
    view = {"budget": budget, "used_fraction": month_to_date / budget, "projected_fraction": projected / budget}
    if projected > budget and month_to_date > 0:
        rate = month_to_date / (moment - start).total_seconds()
        breach = start + timedelta(seconds=budget / rate)
        view["projected_breach"] = min(breach, end).isoformat()
    return view


def started_hours(start: datetime, end: datetime) -> int:
    if end <= start:
        return 0
    return math.ceil((end - start).total_seconds() / SECONDS_PER_HOUR)


def capped_resource(resource: dict, moment: datetime, zone: ZoneInfo) -> dict:
    start, end = month_bounds(moment)
    created = parse_moment(resource["created"], zone)
    deleted = parse_moment(resource["deleted"], zone) if resource.get("deleted") else None
    billing_start = max(created, start)
    hourly, cap = float(resource["hourly"]), float(resource["monthly_cap"])
    so_far_end = min(moment, deleted) if deleted else moment
    month_end = min(end, deleted) if deleted else end
    return {
        "name": resource["name"],
        "billable_hours": started_hours(billing_start, so_far_end),
        "month_to_date": min(started_hours(billing_start, so_far_end) * hourly, cap),
        "projected": min(started_hours(billing_start, month_end) * hourly, cap),
        "monthly_cap": cap,
    }


def capped_projection(resources: list, moment: datetime, zone: ZoneInfo) -> dict:
    rows = [capped_resource(resource, moment, zone) for resource in resources]
    return {"resources": rows,
            "month_to_date": sum(row["month_to_date"] for row in rows),
            "projected": sum(row["projected"] for row in rows),
            "full_month_run_rate": sum(row["monthly_cap"] for row in rows)}


def modified_z_scores(values: list) -> list:
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    if mad == 0:
        return [0.0 if value == median else math.inf for value in values]
    return [MODIFIED_Z_CONSTANT * (value - median) / mad for value in values]


def daily_projection(days: list, moment: datetime) -> dict:
    start, end = month_bounds(moment)
    this_month = [(day, amount) for day, amount in days if start.date() <= day < moment.date()]
    if len(this_month) < 2:
        raise ValueError("need at least two complete days this month")
    amounts = [amount for _, amount in this_month]
    remaining = (end.date() - moment.date()).days
    mean, spread = statistics.mean(amounts), statistics.stdev(amounts)
    projected = sum(amounts) + mean * remaining
    margin = NORMAL_95 * spread * math.sqrt(remaining)
    scores = modified_z_scores([amount for _, amount in days])
    anomalies = [{"day": day.isoformat(), "amount": amount, "modified_z": round(score, 2)}
                 for (day, amount), score in zip(days, scores) if abs(score) > MODIFIED_Z_THRESHOLD]
    return {"complete_days": len(amounts), "remaining_days": remaining, "month_to_date": sum(amounts),
            "projected": projected, "low": max(sum(amounts), projected - margin), "high": projected + margin,
            "anomalies": anomalies}


def read_daily(path: str) -> list:
    with open(path, newline="", encoding="utf-8") as handle:
        rows = [row for row in csv.reader(handle) if row and not row[0].startswith("date")]
    return sorted((date.fromisoformat(row[0]), float(row[1])) for row in rows)


def render(result: dict, symbol: str) -> str:
    lines = []
    for key, value in result.items():
        if key == "resources":
            for row in value:
                lines.append(f"  {row['name']:<28} {row['billable_hours']:>4} h  "
                             f"mtd {money(row['month_to_date'], symbol):>12}  "
                             f"projected {money(row['projected'], symbol):>12}")
        elif key == "anomalies":
            for row in value:
                lines.append(f"  anomaly {row['day']}: {money(row['amount'], symbol)} (modified z {row['modified_z']})")
        elif key.endswith("fraction"):
            lines.append(f"{key.replace('_', ' ')}: {value * 100:.1f} %".replace(".", ","))
        elif isinstance(value, float) and key not in ("elapsed_fraction",):
            lines.append(f"{key.replace('_', ' ')}: {money(value, symbol)}")
        else:
            lines.append(f"{key.replace('_', ' ')}: {value}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--at", default=None, help="moment to project from, ISO 8601; default now")
    parser.add_argument("--tz", default="UTC", help="billing timezone; month boundaries follow it")
    parser.add_argument("--budget", type=float)
    parser.add_argument("--symbol", default="€")
    parser.add_argument("--json", action="store_true")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("linear").add_argument("--mtd", type=float, required=True)
    commands.add_parser("capped").add_argument("--inventory", required=True)
    commands.add_parser("daily").add_argument("--csv", required=True)
    args = parser.parse_args()
    zone = ZoneInfo(args.tz)
    moment = parse_moment(args.at, zone) if args.at else datetime.now(timezone.utc).astimezone(zone)
    try:
        if args.command == "linear":
            result = {"month_to_date": args.mtd, **linear_projection(args.mtd, moment)}
        elif args.command == "capped":
            with open(args.inventory, encoding="utf-8") as handle:
                result = capped_projection(json.load(handle), moment, zone)
        else:
            result = daily_projection(read_daily(args.csv), moment)
        if args.budget:
            result.update(budget_view(result["projected"], result["month_to_date"], args.budget, moment))
    except (ValueError, KeyError, OSError) as error:
        print(f"forecast: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else render(result, args.symbol))
    return 0


if __name__ == "__main__":
    sys.exit(main())
