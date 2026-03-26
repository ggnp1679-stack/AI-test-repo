from __future__ import annotations
import copy
from datetime import datetime

import yaml


REQUIRED_KEYS: dict[str, set[str]] = {
    "data": {"symbol", "start_date", "end_date", "source"},
    "strategy": {"name", "short_window", "long_window"},
    "execution": {"price", "rebalance_frequency"},
    "costs": {"commission_bps", "slippage_bps"},
    "portfolio": {"initial_capital", "long_only", "position_size"},
    "report": {
        "output_dir",
        "save_equity_curve_csv",
        "save_trades_csv",
        "save_summary_json",
        "benchmark",
    },
}


def deep_update(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_update(out[k], v)
        else:
            out[k] = v
    return out


def load_yaml(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _parse_date(value: object, key: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"Invalid config '{key}': expected string in YYYY-MM-DD, got {type(value).__name__}")

    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError(f"Invalid config '{key}': '{value}' is not in YYYY-MM-DD format") from exc


def _ensure_required_structure(cfg: dict) -> None:
    for section, required_keys in REQUIRED_KEYS.items():
        if section not in cfg:
            raise ValueError(f"Missing required section: '{section}'")
        if not isinstance(cfg[section], dict):
            raise ValueError(
                f"Invalid config '{section}': expected mapping/dict, got {type(cfg[section]).__name__}"
            )

        missing_keys = sorted(required_keys - set(cfg[section].keys()))
        if missing_keys:
            raise ValueError(f"Missing required key(s) in '{section}': {', '.join(missing_keys)}")


def validate_config(cfg: dict) -> None:
    _ensure_required_structure(cfg)

    start_dt = _parse_date(cfg["data"]["start_date"], "data.start_date")
    end_dt = _parse_date(cfg["data"]["end_date"], "data.end_date")
    if start_dt > end_dt:
        raise ValueError(
            "Invalid date range: 'data.start_date' must be <= 'data.end_date' "
            f"(got {cfg['data']['start_date']} > {cfg['data']['end_date']})"
        )

    strategy_name = cfg["strategy"]["name"]
    if strategy_name != "sma_cross":
        raise ValueError(
            "Invalid config 'strategy.name': expected 'sma_cross' "
            f"for current version, got '{strategy_name}'"
        )

    short_w = cfg["strategy"]["short_window"]
    long_w = cfg["strategy"]["long_window"]
    if short_w <= 0 or long_w <= 0:
        raise ValueError("Invalid config 'strategy.short_window/strategy.long_window': both must be > 0")
    if short_w >= long_w:
        raise ValueError("Invalid config: 'strategy.short_window' must be smaller than 'strategy.long_window'")

    pos = cfg["portfolio"]["position_size"]
    if not (0 < pos <= 1):
        raise ValueError("Invalid config 'portfolio.position_size': must be in (0, 1]")

    if cfg["execution"]["price"] not in {"next_open", "close"}:
        raise ValueError("Invalid config 'execution.price': must be one of ['next_open', 'close']")

    for key in ("commission_bps", "slippage_bps"):
        value = cfg["costs"][key]
        if value < 0:
            raise ValueError(f"Invalid config 'costs.{key}': must be >= 0 (got {value})")


def load_config(default_path: str, user_path: str | None = None) -> dict:
    cfg = load_yaml(default_path)
    if user_path:
        user_cfg = load_yaml(user_path)
        cfg = deep_update(cfg, user_cfg)
    validate_config(cfg)
    return cfg
