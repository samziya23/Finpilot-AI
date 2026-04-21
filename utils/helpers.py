# utils/helpers.py
import pandas as pd


def load_and_validate_csv(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
        df.columns = [c.strip().lower() for c in df.columns]
        required = {"date", "category", "amount"}
        missing = required - set(df.columns)
        if missing:
            return None, f"Missing columns: {', '.join(missing)}"
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if df["date"].isna().any():
            return None, "Some dates couldn't be parsed. Use YYYY-MM-DD format."
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        if df["amount"].isna().any():
            return None, "Some amount values are not valid numbers."
        df = df[df["amount"] > 0].reset_index(drop=True)
        if len(df) == 0:
            return None, "No valid rows found."
        return df, None
    except Exception as e:
        return None, f"Failed to read CSV: {str(e)}"


def format_currency(amount: float) -> str:
    return f"₹{amount:,.0f}"
