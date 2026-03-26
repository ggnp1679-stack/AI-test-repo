from __future__ import annotations
import argparse
import json
import os

from config_loader import load_config
from data_loader import load_price_data
from strategy_ma import generate_signals_sma_cross
from backtest_engine import run_backtest
from metrics import compute_metrics


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="S&P500 Backtest Runner")
    parser.add_argument("--default-config", default="config/default.yaml")
    parser.add_argument("--user-config", default="config/user.yaml")
    args = parser.parse_args()

    cfg = load_config(args.default_config, args.user_config)

    df = load_price_data(
        symbol=cfg["data"]["symbol"],
        start_date=cfg["data"]["start_date"],
        end_date=cfg["data"]["end_date"],
    )

    if cfg["strategy"]["name"] != "sma_cross":
        raise ValueError("v1 supports only strategy.name = sma_cross")

    df_sig = generate_signals_sma_cross(
        df,
        short_window=cfg["strategy"]["short_window"],
        long_window=cfg["strategy"]["long_window"],
    )

    result_df, trades_df = run_backtest(df_sig, cfg)
    summary = compute_metrics(result_df)

    out_dir = cfg["report"]["output_dir"]
    ensure_dir(out_dir)

    if cfg["report"]["save_equity_curve_csv"]:
        result_df.to_csv(os.path.join(out_dir, "equity_curve.csv"), index=False)

    if cfg["report"]["save_trades_csv"]:
        trades_df.to_csv(os.path.join(out_dir, "trades.csv"), index=False)

    if cfg["report"]["save_summary_json"]:
        with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

    print("[Done] Backtest completed.")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
