from __future__ import annotations
import pandas as pd


def run_backtest(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()

    execution_price = cfg["execution"]["price"]
    commission_bps = cfg["costs"]["commission_bps"]
    slippage_bps = cfg["costs"]["slippage_bps"]
    position_size = cfg["portfolio"]["position_size"]
    initial_capital = cfg["portfolio"]["initial_capital"]

    if execution_price == "close":
        out["position"] = out["target_position"] * position_size
        out["exec_px"] = out["Close"]
    else:
        out["position"] = out["target_position"].shift(1).fillna(0.0) * position_size
        out["exec_px"] = out["Open"]

    out["ret"] = out["Adj Close"].pct_change().fillna(0.0)
    out["strategy_gross_ret"] = out["position"] * out["ret"]

    out["trade_size"] = out["position"].diff().abs().fillna(out["position"].abs())
    total_bps = commission_bps + slippage_bps
    out["cost_ret"] = out["trade_size"] * (total_bps / 10000.0)

    out["strategy_net_ret"] = out["strategy_gross_ret"] - out["cost_ret"]

    out["equity"] = initial_capital * (1.0 + out["strategy_net_ret"]).cumprod()
    out["benchmark_equity"] = initial_capital * (1.0 + out["ret"]).cumprod()

    trades = out.loc[out["trade_size"] > 0, ["Date", "position", "trade_size", "cost_ret"]].copy()
    return out, trades
