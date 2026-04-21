# tools/analysis_tool.py
import pandas as pd


def expense_analysis_tool(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    total = float(df["amount"].sum())
    cat_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False).to_dict()
    monthly_totals = df.groupby("month")["amount"].sum().sort_index().to_dict()
    cat_pct = {k: v / total * 100 for k, v in cat_totals.items()}

    top_cat = list(cat_totals.keys())[0]
    num_months = len(monthly_totals)
    avg_monthly = total / max(num_months, 1)

    months_list = sorted(monthly_totals.keys())
    monthly_mom = {}
    for i, m in enumerate(months_list):
        if i == 0:
            monthly_mom[m] = None
        else:
            prev = monthly_totals[months_list[i - 1]]
            curr = monthly_totals[m]
            monthly_mom[m] = ((curr - prev) / prev) * 100 if prev else 0

    last_mom = monthly_mom.get(months_list[-1]) if months_list else None

    trend = "stable"
    if len(months_list) >= 2:
        last = monthly_totals[months_list[-1]]
        prev = monthly_totals[months_list[-2]]
        if last > prev * 1.05:
            trend = "increasing"
        elif last < prev * 0.95:
            trend = "decreasing"

    overspending = {c: a for c, a in cat_totals.items() if (a / total) > 0.30}

    return {
        "total_spending": total,
        "category_totals": cat_totals,
        "category_pct_share": cat_pct,
        "monthly_totals": monthly_totals,
        "monthly_mom_change": monthly_mom,
        "top_category": top_cat,
        "top_amount": cat_totals[top_cat],
        "top_category_pct_total": cat_pct[top_cat],
        "avg_monthly": avg_monthly,
        "overspending_categories": overspending,
        "spending_trend": trend,
        "num_months": num_months,
        "last_month_change_pct": last_mom,
    }


def format_analysis_summary(analysis: dict) -> str:
    lines = [
        f"Total Spending: ₹{analysis['total_spending']:,.0f}",
        f"Average Monthly Spending: ₹{analysis['avg_monthly']:,.0f}",
        f"Top Category: {analysis['top_category']} (₹{analysis['top_amount']:,.0f}, {analysis['top_category_pct_total']:.1f}%)",
        f"Spending Trend: {analysis['spending_trend']}",
        "",
        "Category Breakdown:",
    ]
    for cat, amt in analysis["category_totals"].items():
        pct = analysis["category_pct_share"].get(cat, 0)
        lines.append(f"  - {cat}: ₹{amt:,.0f} ({pct:.1f}%)")
    if analysis["overspending_categories"]:
        lines.append("")
        lines.append("Overspending Alert (>30% of budget):")
        for c, a in analysis["overspending_categories"].items():
            lines.append(f"  - {c}: ₹{a:,.0f}")
    return "\n".join(lines)
