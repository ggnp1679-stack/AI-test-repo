from __future__ import annotations
import pandas as pd


def run_backtest(df: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()

    execution_price = cfg["execution"]["price"]
    commission_bps = cfg["costs"]["commission_bps"]
    slippage_bps = cfg["costs"]["slippage_bps"]
    position_size = cfg["portfolio"]["position_size"]
    initial_capital = cfg["portfolio"]["initial_capital"]
    mtm_basis = cfg["execution"].get("mark_to_market_price", "adj_close")

    mtm_price_map = {
        "adj_close": "Adj Close",
        "close": "Close",
    }
    mtm_price_col = mtm_price_map.get(mtm_basis.lower(), mtm_basis)
    if mtm_price_col not in out.columns:
        raise ValueError(f"mark_to_market_price column not found: {mtm_price_col}")

    if execution_price == "close":
        out["position"] = out["target_position"] * position_size
        out["exec_px"] = out["Close"]
        out["signal_date"] = out["Date"]
    elif execution_price == "next_open":
        # 신호 t -> 체결 t+1(Open) 정렬.
        out["position"] = out["target_position"].shift(1).fillna(0.0) * position_size
        out["exec_px"] = out["Open"]
        out["signal_date"] = out["Date"].shift(1)
    else:
        raise ValueError("execution.price must be one of: next_open, close")

    out["mtm_px"] = out[mtm_price_col]
    out["ret"] = out["mtm_px"].pct_change().fillna(0.0)

    out["position_prev"] = out["position"].shift(1).fillna(0.0)
    out["trade"] = out["position"] - out["position_prev"]
    out["trade_size"] = out["trade"].abs()

    # 보유 포지션의 마크투마켓 손익.
    out["holding_ret"] = out["position_prev"] * out["ret"]

    # 체결 가격(exec_px)과 당일 마크투마켓 가격(mtm_px) 차이로 발생한 거래일 손익.
    exec_move = (out["mtm_px"] / out["exec_px"]).replace([pd.NA, float("inf"), -float("inf")], 1.0)
    out["execution_ret"] = out["trade"] * (exec_move.fillna(1.0) - 1.0)
    out["strategy_gross_ret"] = out["holding_ret"] + out["execution_ret"]

    out["position_change"] = out["position"].diff().fillna(out["position"])
    out["trade_size"] = out["position_change"].abs()

    total_bps = commission_bps + slippage_bps
    out["trade_cost_rate"] = out["trade_size"] * (total_bps / 10000.0)
    out["cost_ret"] = out["trade_cost_rate"]

    out["strategy_net_ret"] = out["strategy_gross_ret"] - out["cost_ret"]

    out["equity"] = initial_capital * (1.0 + out["strategy_net_ret"]).cumprod()
    out["benchmark_equity"] = initial_capital * (1.0 + out["ret"]).cumprod()

    trades = out.loc[out["trade_size"] > 0, [
        "Date",
        "exec_px",
        "position",
        "position_change",
        "trade_size",
        "trade_cost_rate",
        "cost_ret",
    ]].copy()
    trades = trades.rename(columns={"exec_px": "fill_price"})
    trades["trade_index"] = trades.index
    trades["trade_direction"] = trades["position_change"].apply(lambda x: "BUY" if x > 0 else "SELL")
    trades["position_before"] = trades["position"] - trades["position_change"]
    trades["position_after"] = trades["position"]
    trades = trades[
        [
            "trade_index",
            "Date",
            "trade_direction",
            "fill_price",
            "position_before",
            "position_after",
            "position_change",
            "trade_size",
            "trade_cost_rate",
            "cost_ret",
        ]
    ]

    return out, trades
