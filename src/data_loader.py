from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {
    "ticker", "resolved_at", "implied_probability", "outcome", "direction",
    "entry_price", "atr", "normalized_distance", "time_to_expiry_minutes",
    "return_pct", "sample",
}

def load_market_data(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path, parse_dates=["resolved_at"])
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df = df.sort_values("resolved_at").reset_index(drop=True)
    return df
