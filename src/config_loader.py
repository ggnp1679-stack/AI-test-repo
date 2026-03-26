from __future__ import annotations
import copy
import yaml


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


def validate_config(cfg: dict) -> None:
    short_w = cfg["strategy"]["short_window"]
    long_w = cfg["strategy"]["long_window"]
    if short_w <= 0 or long_w <= 0:
        raise ValueError("short_window, long_window must be > 0")
    if short_w >= long_w:
        raise ValueError("short_window must be smaller than long_window")

    pos = cfg["portfolio"]["position_size"]
    if not (0 < pos <= 1):
        raise ValueError("position_size must be in (0, 1]")

    if cfg["execution"]["price"] not in {"next_open", "close"}:
        raise ValueError("execution.price must be one of: next_open, close")


def load_config(default_path: str, user_path: str | None = None) -> dict:
    cfg = load_yaml(default_path)
    if user_path:
        user_cfg = load_yaml(user_path)
        cfg = deep_update(cfg, user_cfg)
    validate_config(cfg)
    return cfg
