# tools/prediction_tool.py
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def prediction_tool(df: pd.DataFrame) -> dict:
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")
    monthly = df.groupby("month")["amount"].sum().reset_index().sort_values("month")
    monthly["month_index"] = range(len(monthly))

    if len(monthly) < 2:
        return {"error": "Need at least 2 months of data.", "predicted_amount": None, "monthly_data": []}

    X = monthly[["month_index"]].values
    y = monthly["amount"].values

    # Linear regression component (40%)
    model = LinearRegression()
    model.fit(X, y)
    lr_pred = float(model.predict([[len(monthly)]])[0])

    # EMA component (60%) — weighted toward recent months
    weights = np.exp(np.linspace(0, 1, len(y)))
    weights /= weights.sum()
    ema_pred = float(np.dot(weights, y))

    # Blend: 60% EMA + 40% LR
    predicted_amount = max(0.6 * ema_pred + 0.4 * lr_pred, 0)

    last_month = monthly["month"].iloc[-1]
    next_month = last_month + 1
    next_label = str(next_month)

    r2 = model.score(X, y)
    slope = float(model.coef_[0])

    trend = "stable"
    if slope > 100:
        trend = "increasing"
    elif slope < -100:
        trend = "decreasing"

    last_actual = float(monthly["amount"].iloc[-1])
    change_pct = ((predicted_amount - last_actual) / last_actual) * 100
    avg = float(np.mean(y))
    vs_avg_pct = ((predicted_amount - avg) / avg) * 100

    # Confidence
    if r2 > 0.75:
        conf_label, conf_score = "High", 95
    elif r2 > 0.45:
        conf_label, conf_score = "Medium", 72
    else:
        conf_label, conf_score = "Low", 50

    return {
        "predicted_amount": predicted_amount,
        "next_month_label": next_label,
        "last_actual_amount": last_actual,
        "change_pct": change_pct,
        "vs_avg_pct": vs_avg_pct,
        "trend": trend,
        "r2_score": r2,
        "confidence_label": conf_label,
        "confidence_score": conf_score,
        "monthly_data": monthly[["month", "amount"]].assign(month=monthly["month"].astype(str)).to_dict(orient="records"),
        "model_slope": slope,
    }


def format_prediction_summary(prediction: dict) -> str:
    if prediction.get("error"):
        return f"Prediction Error: {prediction['error']}"
    lines = [
        f"Predicted for {prediction['next_month_label']}: ₹{prediction['predicted_amount']:,.0f}",
        f"Last Month Actual: ₹{prediction['last_actual_amount']:,.0f}",
        f"Change: {prediction['change_pct']:+.1f}%",
        f"vs Historical Average: {prediction['vs_avg_pct']:+.1f}%",
        f"Trend: {prediction['trend']}",
        f"Confidence: {prediction['confidence_label']} ({prediction['confidence_score']:.0f}%)",
        f"Model R²: {prediction['r2_score']:.2f}",
    ]
    return "\n".join(lines)
