import numpy as np
import pandas as pd

def calibration_table(df: pd.DataFrame, bucket_width: float = 0.10) -> pd.DataFrame:
    working = df.copy()
    edges = np.arange(0.0, 1.0 + bucket_width, bucket_width)
    labels = [f"{int(a*100)} to {int(b*100)}" for a, b in zip(edges[:-1], edges[1:])]
    working["probability_bucket"] = pd.cut(
        working["implied_probability"], bins=edges, labels=labels,
        include_lowest=True, right=True
    )
    result = (
        working.groupby("probability_bucket", observed=True)
        .agg(
            markets=("ticker", "count"),
            mean_implied_probability=("implied_probability", "mean"),
            realized_outcome_rate=("outcome", "mean"),
        )
        .reset_index()
    )
    result["calibration_gap"] = (
        result["realized_outcome_rate"] - result["mean_implied_probability"]
    )
    return result

def summary_metrics(df: pd.DataFrame) -> dict:
    return {
        "markets": int(df["ticker"].nunique()),
        "observations": int(len(df)),
        "mean_return_pct": float(df["return_pct"].mean()),
        "positive_return_rate": float((df["return_pct"] > 0).mean()),
    }

def feature_return_summary(df: pd.DataFrame, feature: str) -> pd.DataFrame:
    working = df.copy()
    if pd.api.types.is_numeric_dtype(working[feature]):
        working["feature_bucket"] = pd.qcut(
            working[feature], q=min(5, working[feature].nunique()), duplicates="drop"
        )
        group_key = "feature_bucket"
    else:
        group_key = feature
    return (
        working.groupby(group_key, observed=True)
        .agg(
            observations=("ticker", "count"),
            mean_return_pct=("return_pct", "mean"),
            positive_return_rate=("return_pct", lambda s: (s > 0).mean()),
        )
        .reset_index()
    )
