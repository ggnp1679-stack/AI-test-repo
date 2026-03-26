from __future__ import annotations
import pandas as pd


def generate_signals_sma_cross(df: pd.DataFrame, short_window: int, long_window: int) -> pd.DataFrame:
    out = df.copy()
    out["sma_short"] = out["Adj Close"].rolling(short_window).mean()
    out["sma_long"] = out["Adj Close"].rolling(long_window).mean()
    out["target_position"] = (out["sma_short"] > out["sma_long"]).astype(float)
    out["target_position"] = out["target_position"].fillna(0.0)
    return out
