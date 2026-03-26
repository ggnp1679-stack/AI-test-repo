from __future__ import annotations
import yfinance as yf
import pandas as pd


def load_price_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = yf.download(symbol, start=start_date, end=end_date, auto_adjust=False, progress=False)
    if df.empty:
        raise ValueError(f"No data downloaded for symbol={symbol}")

    df = df.rename_axis("Date").reset_index()
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    required = ["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[required].copy()
    df = df.sort_values("Date").reset_index(drop=True)
    return df
