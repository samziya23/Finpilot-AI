# tools/anomaly_tool.py
import pandas as pd
import numpy as np


def anomaly_detection_tool(df: pd.DataFrame) -> dict:
    """
    Detects spending anomalies at monthly and category level.
    Flags entries with Z-score > 1.5 (>1.5 standard deviations from mean).
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    monthly = df.groupby("month")["amount"].sum().reset_index().sort_values("month")
    monthly_anomalies = []

    if len(monthly) >= 3:
        mean = monthly["amount"].mean()
        std = monthly["amount"].std()
        if std > 0:
            for _, row in monthly.iterrows():
                z = (row["amount"] - mean) / std
                if z > 1.5:
                    pct_above = ((row["amount"] - mean) / mean) * 100
                    severity = "high" if z > 2.5 else "medium"
                    monthly_anomalies.append({
                        "month": row["month"],
                        "amount": float(row["amount"]),
                        "z_score": float(z),
                        "mean": float(mean),
                        "pct_above_avg": float(pct_above),
                        "severity": severity,
                    })

    # Category-level anomalies
    cat_month = df.groupby(["category", "month"])["amount"].sum().reset_index()
    category_anomalies = []

    for cat in cat_month["category"].unique():
        cat_data = cat_month[cat_month["category"] == cat]
        if len(cat_data) < 3:
            continue
        mean = cat_data["amount"].mean()
        std = cat_data["amount"].std()
        if std == 0:
            continue
        for _, row in cat_data.iterrows():
            z = (row["amount"] - mean) / std
            if z > 1.5:
                pct_above = ((row["amount"] - mean) / mean) * 100
                severity = "high" if z > 2.5 else "medium"
                category_anomalies.append({
                    "category": row["category"],
                    "month": row["month"],
                    "amount": float(row["amount"]),
                    "z_score": float(z),
                    "mean": float(mean),
                    "pct_above_avg": float(pct_above),
                    "severity": severity,
                })

    # Sort by z_score descending
    monthly_anomalies.sort(key=lambda x: x["z_score"], reverse=True)
    category_anomalies.sort(key=lambda x: x["z_score"], reverse=True)

    total = len(monthly_anomalies) + len(category_anomalies)
    has_anomalies = total > 0

    if has_anomalies:
        parts = []
        if monthly_anomalies:
            parts.append(f"{len(monthly_anomalies)} monthly spike(s)")
        if category_anomalies:
            parts.append(f"{len(category_anomalies)} category spike(s)")
        summary = "Detected " + " and ".join(parts) + " above normal range."
    else:
        summary = "No anomalies detected — spending patterns are consistent."

    return {
        "has_anomalies": has_anomalies,
        "total_anomalies": total,
        "monthly_anomalies": monthly_anomalies,
        "category_anomalies": category_anomalies,
        "summary_text": summary,
    }


def format_anomaly_summary(data: dict) -> str:
    if not data["has_anomalies"]:
        return "No anomalies detected."
    lines = [data["summary_text"], ""]
    if data["monthly_anomalies"]:
        lines.append("Monthly Anomalies:")
        for a in data["monthly_anomalies"]:
            lines.append(f"  - {a['month']}: ₹{a['amount']:,.0f} ({a['pct_above_avg']:+.0f}% above avg, Z={a['z_score']:.1f})")
    if data["category_anomalies"]:
        lines.append("Category Anomalies:")
        for a in data["category_anomalies"]:
            lines.append(f"  - {a['category']} in {a['month']}: ₹{a['amount']:,.0f} (Z={a['z_score']:.1f})")
    return "\n".join(lines)
