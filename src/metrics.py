from __future__ import annotations
import numpy as np
import pandas as pd


def _cagr(equity: pd.Series, periods_per_year: int = 252) -> float:
    if len(equity) < 2:
        return 0.0
    years = len(equity) / periods_per_year
    if years <= 0:
        return 0.0
    return float((equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1)


def _mdd(equity: pd.Series) -> float:
    running_max = equity.cummax()
    dd = equity / running_max - 1.0
    return float(dd.min())


def compute_metrics(result_df: pd.DataFrame) -> dict:
    r = result_df["strategy_net_ret"].fillna(0.0)

    vol = float(r.std(ddof=0) * np.sqrt(252))
    sharpe = float((r.mean() / r.std(ddof=0)) * np.sqrt(252)) if r.std(ddof=0) > 0 else 0.0

    wins = (r > 0).sum()
    non_zero = (r != 0).sum()
    win_rate = float(wins / non_zero) if non_zero > 0 else 0.0

    metrics = {
        "strategy_cagr": _cagr(result_df["equity"]),
        "strategy_mdd": _mdd(result_df["equity"]),
        "strategy_volatility": vol,
        "strategy_sharpe": sharpe,
        "strategy_total_return": float(result_df["equity"].iloc[-1] / result_df["equity"].iloc[0] - 1),
        "benchmark_total_return": float(result_df["benchmark_equity"].iloc[-1] / result_df["benchmark_equity"].iloc[0] - 1),
        "win_rate": win_rate,
        "num_trades": int((result_df["trade_size"] > 0).sum()),
    }
    return metrics
