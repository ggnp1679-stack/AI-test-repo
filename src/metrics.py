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


def _compute_roundtrip_returns(trades_df: pd.DataFrame) -> list[float]:
    if trades_df.empty:
        return []

    roundtrip_returns: list[float] = []
    open_entry: pd.Series | None = None

    for _, trade in trades_df.sort_values("trade_index").iterrows():
        direction = trade["trade_direction"]

        if direction == "BUY":
            open_entry = trade
            continue

        if direction != "SELL" or open_entry is None:
            continue

        entry_px = float(open_entry["fill_price"])
        exit_px = float(trade["fill_price"])

        if entry_px <= 0:
            open_entry = None
            continue

        gross_trade_return = (exit_px / entry_px) - 1.0
        roundtrip_cost = float(open_entry["trade_cost_rate"] + trade["trade_cost_rate"])
        roundtrip_returns.append(gross_trade_return - roundtrip_cost)
        open_entry = None

    return roundtrip_returns


def compute_metrics(result_df: pd.DataFrame, trades_df: pd.DataFrame) -> dict:
    r = result_df["strategy_net_ret"].fillna(0.0)

    vol = float(r.std(ddof=0) * np.sqrt(252))
    sharpe = float((r.mean() / r.std(ddof=0)) * np.sqrt(252)) if r.std(ddof=0) > 0 else 0.0

    wins = (r > 0).sum()
    active_days = (r != 0).sum()
    daily_win_rate = float(wins / active_days) if active_days > 0 else 0.0

    trade_returns = _compute_roundtrip_returns(trades_df)
    num_round_trips = len(trade_returns)
    trade_win_rate = float(sum(ret > 0 for ret in trade_returns) / num_round_trips) if num_round_trips > 0 else 0.0
    avg_trade_return = float(np.mean(trade_returns)) if num_round_trips > 0 else 0.0

    metrics = {
        "strategy_cagr": _cagr(result_df["equity"]),
        "strategy_mdd": _mdd(result_df["equity"]),
        "strategy_volatility": vol,
        "strategy_sharpe": sharpe,
        "strategy_total_return": float(result_df["equity"].iloc[-1] / result_df["equity"].iloc[0] - 1),
        "benchmark_total_return": float(result_df["benchmark_equity"].iloc[-1] / result_df["benchmark_equity"].iloc[0] - 1),
        "daily_win_rate": daily_win_rate,
        "trade_win_rate": trade_win_rate,
        "avg_trade_return": avg_trade_return,
        "num_trades": num_round_trips,
        "num_trade_events": int(len(trades_df)),
    }
    return metrics
