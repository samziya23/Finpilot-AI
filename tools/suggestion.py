# tools/suggestion_tool.py
import pandas as pd
import numpy as np


def savings_suggestion_tool(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    total = float(df["amount"].sum())
    num_months = df["month"].nunique()
    avg_monthly = total / max(num_months, 1)

    cat_totals = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    cat_monthly_avg = (cat_totals / num_months).to_dict()
    cat_pct = (cat_totals / total * 100).to_dict()

    # Compute per-category per-month variance for context
    cat_month = df.groupby(["category", "month"])["amount"].sum()
    cat_std = cat_month.groupby("category").std().fillna(0).to_dict()

    # Overall monthly average per category for comparison
    overall_cat_avg = avg_monthly / max(len(cat_totals), 1)

    suggestions = []
    savings_potential = 0.0

    # Food
    food_cats = [k for k in cat_pct if "food" in k.lower()]
    food_spend = sum(cat_totals.get(c, 0) for c in food_cats)
    if food_spend / total > 0.30:
        monthly_food = food_spend / num_months
        save = monthly_food * 0.20
        savings_potential += save
        pct_above = ((monthly_food - overall_cat_avg) / overall_cat_avg * 100) if overall_cat_avg else 0
        suggestions.append({
            "category": "Food", "monthly_avg": monthly_food,
            "insight": f"Food consumes {food_spend/total*100:.0f}% of your total budget.",
            "action": "Meal prep 3–4x/week and limit dining out to once weekly.",
            "estimated_saving": save, "pct_above_all_avg": pct_above,
        })

    # Shopping
    shop_cats = [k for k in cat_pct if "shop" in k.lower()]
    shop_spend = sum(cat_totals.get(c, 0) for c in shop_cats)
    if shop_spend / total > 0.18:
        monthly_shop = shop_spend / num_months
        save = monthly_shop * 0.30
        savings_potential += save
        pct_above = ((monthly_shop - overall_cat_avg) / overall_cat_avg * 100) if overall_cat_avg else 0
        suggestions.append({
            "category": "Shopping", "monthly_avg": monthly_shop,
            "insight": f"Shopping is {shop_spend/total*100:.0f}% of expenses — the 2nd biggest drain.",
            "action": "Apply the 48-hour rule before unplanned purchases.",
            "estimated_saving": save, "pct_above_all_avg": pct_above,
        })

    # Entertainment
    ent_cats = [k for k in cat_pct if "entertain" in k.lower()]
    ent_spend = sum(cat_totals.get(c, 0) for c in ent_cats)
    if ent_spend / total > 0.10:
        monthly_ent = ent_spend / num_months
        save = monthly_ent * 0.40
        savings_potential += save
        pct_above = ((monthly_ent - overall_cat_avg) / overall_cat_avg * 100) if overall_cat_avg else 0
        suggestions.append({
            "category": "Entertainment", "monthly_avg": monthly_ent,
            "insight": f"Entertainment at {ent_spend/total*100:.0f}% has high reduction potential.",
            "action": "Set a ₹{:.0f}/month cap. Explore free events.".format(monthly_ent * 0.6),
            "estimated_saving": save, "pct_above_all_avg": pct_above,
        })

    # Always: 50/30/20 budgeting advice
    save_general = avg_monthly * 0.20
    suggestions.append({
        "category": "Budgeting", "monthly_avg": avg_monthly,
        "insight": f"Your avg spend is ₹{avg_monthly:,.0f}/month — implement a structured budget.",
        "action": "Apply 50/30/20: needs 50%, wants 30%, savings 20%.",
        "estimated_saving": save_general, "pct_above_all_avg": 0,
    })

    suggestions = suggestions[:5]

    return {
        "suggestions": suggestions,
        "total_savings_potential": savings_potential,
        "avg_monthly_spend": avg_monthly,
        "num_months": num_months,
        "top_spending_category": list(cat_totals.index)[0] if len(cat_totals) > 0 else "N/A",
    }


def format_suggestions_summary(result: dict) -> str:
    lines = [
        f"Avg Monthly: ₹{result['avg_monthly_spend']:,.0f}",
        f"Savings Potential: ₹{result['total_savings_potential']:,.0f}/month",
        "",
    ]
    for i, s in enumerate(result["suggestions"], 1):
        lines.append(f"{i}. [{s['category']}] {s['insight']}")
        lines.append(f"   Action: {s['action']}")
        lines.append(f"   Save: ₹{s['estimated_saving']:,.0f}/mo")
    return "\n".join(lines)
