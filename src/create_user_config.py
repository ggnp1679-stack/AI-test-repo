from __future__ import annotations

import argparse
import os
import yaml


def _ask(prompt: str, default: str) -> str:
    val = input(f"{prompt} [{default}]: ").strip()
    return val if val else default


def _ask_float(prompt: str, default: float) -> float:
    while True:
        try:
            return float(_ask(prompt, str(default)))
        except ValueError:
            print("숫자를 입력하세요.")


def _ask_int(prompt: str, default: int) -> int:
    while True:
        try:
            return int(_ask(prompt, str(default)))
        except ValueError:
            print("정수를 입력하세요.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create config/user.yaml interactively")
    parser.add_argument("--output", default="config/user.yaml")
    args = parser.parse_args()

    print("=== 사용자 설정 입력 ===")
    symbol = _ask("symbol (SPY or ^GSPC)", "SPY")
    while symbol not in {"SPY", "^GSPC"}:
        print("symbol은 SPY 또는 ^GSPC 만 가능합니다.")
        symbol = _ask("symbol (SPY or ^GSPC)", "SPY")
    start_date = _ask("start_date (YYYY-MM-DD)", "2010-01-01")
    end_date = _ask("end_date (YYYY-MM-DD)", "2025-12-31")

    short_window = _ask_int("short_window", 50)
    long_window = _ask_int("long_window", 200)
    while short_window >= long_window:
        print("short_window는 long_window보다 작아야 합니다.")
        short_window = _ask_int("short_window", 50)
        long_window = _ask_int("long_window", 200)

    execution_price = _ask("execution.price (next_open or close)", "next_open")
    while execution_price not in {"next_open", "close"}:
        print("next_open 또는 close 만 가능합니다.")
        execution_price = _ask("execution.price (next_open or close)", "next_open")

    commission_bps = _ask_int("commission_bps", 5)
    slippage_bps = _ask_int("slippage_bps", 5)
    position_size = _ask_float("position_size (0~1)", 1.0)
    while not (0 < position_size <= 1):
        print("position_size는 0보다 크고 1 이하여야 합니다.")
        position_size = _ask_float("position_size (0~1)", 1.0)

    initial_capital = _ask_int("initial_capital", 100000)
    output_dir = _ask("report.output_dir", "results")

    cfg = {
        "data": {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
        },
        "strategy": {
            "short_window": short_window,
            "long_window": long_window,
        },
        "execution": {
            "price": execution_price,
        },
        "costs": {
            "commission_bps": commission_bps,
            "slippage_bps": slippage_bps,
        },
        "portfolio": {
            "initial_capital": initial_capital,
            "position_size": position_size,
        },
        "report": {
            "output_dir": output_dir,
        },
    }

    output_dirname = os.path.dirname(args.output)
    if output_dirname:
        os.makedirs(output_dirname, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)

    print(f"[Done] 사용자 설정 저장: {args.output}")


if __name__ == "__main__":
    main()
