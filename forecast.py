"""Capacity forecast: demand hours vs. team capacity -> FTE gap and latest hire-by month.

Usage: python forecast.py --demand data/demand.csv --team data/team.csv --out output/forecast.csv
"""
import argparse, math
import pandas as pd

def forecast(demand: pd.DataFrame, team: pd.DataFrame, as_of: str = "2026-11") -> pd.DataFrame:
    df = demand.merge(team, on="tower", how="left")
    if df["current_fte"].isna().any():
        raise ValueError("Tower in demand.csv missing from team.csv")
    # Usable hours at the TARGET utilization (headroom for leave, meetings, spikes)
    df["capacity_hours"] = df["current_fte"] * df["productive_hours_per_fte_month"] * df["target_utilization"]
    df["utilization_pct"] = (df["demand_hours"] / (df["current_fte"] * df["productive_hours_per_fte_month"]) * 100).round(1)
    df["fte_required"] = df["demand_hours"] / (df["productive_hours_per_fte_month"] * df["target_utilization"])
    df["fte_gap"] = (df["fte_required"] - df["current_fte"]).round(2)
    df["hires_needed"] = df["fte_gap"].apply(lambda g: max(0, math.ceil(g - 1e-9)))
    df["status"] = df["utilization_pct"].apply(lambda u: "OVER" if u > 100 else ("AT_RISK" if u > 85 else "OK"))
    start = pd.PeriodIndex(df["month"], freq="M")
    df["hire_by"] = (start - df["hiring_lead_time_months"]).astype(str)
    df.loc[df["hires_needed"] == 0, "hire_by"] = ""
    df["hire_by_overdue"] = (df["hire_by"] != "") & (df["hire_by"] < as_of)
    cols = ["tower", "month", "demand_hours", "current_fte", "capacity_hours", "utilization_pct", "fte_required", "fte_gap", "hires_needed", "status", "hire_by", "hire_by_overdue"]
    return df[cols].round(2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demand", default="data/demand.csv"); ap.add_argument("--team", default="data/team.csv")
    ap.add_argument("--out", default="output/forecast.csv")
    ap.add_argument("--as-of", default="2026-11", help="YYYY-MM; hire-by dates earlier than this are flagged overdue")
    a = ap.parse_args()
    res = forecast(pd.read_csv(a.demand), pd.read_csv(a.team), a.as_of)
    res.to_csv(a.out, index=False)
    print(res.to_string(index=False))
    peak = res.groupby("tower").agg(peak_util=("utilization_pct", "max"), peak_hires=("hires_needed", "max"),
                                    first_hire_by=("hire_by", lambda s: min([x for x in s if x], default="none")))
    print("\nPer-tower summary:\n", peak.to_string())

if __name__ == "__main__":
    main()

# Created by Avash Mohanty, 2026
