# AI-test-repo

S&P 500(SPY/^GSPC) 백테스트 MVP 프로젝트입니다. 설정 파일을 수정하거나 대화형 스크립트로 `config/user.yaml`을 생성해 실행할 수 있습니다.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python src/create_user_config.py --output config/user.yaml
python src/main.py --default-config config/default.yaml --user-config config/user.yaml
```

## Summary 지표 키 정의
- `daily_win_rate`: 일별 수익률(`strategy_net_ret`) 기준 승률
- `trade_win_rate`: 라운드트립(진입/청산 1쌍) 기준 승률
- `avg_trade_return`: 라운드트립 평균 수익률(왕복 비용 반영)
- `num_trades`: 라운드트립 개수
- `num_trade_events`: 개별 체결 이벤트(진입/청산 각각 1건) 개수

## 주요 파일
- `PLAN.md`: 구현 계획
- `DECISIONS.md`: 사용자가 선택해야 하는 항목 정리
- `src/create_user_config.py`: 입력 기반 사용자 설정 파일 생성 스크립트

## 백테스트 체결/수익률 기준
- `execution.mark_to_market_price`(기본값: `adj_close`)로 보유 포지션의 일별 마크투마켓 기준 가격을 분리합니다.
  - `adj_close` → `Adj Close`
  - `close` → `Close`
- `execution.price`는 체결 가격(`exec_px`) 기준입니다.
  - `close`: 신호일(`t`) 종가 체결
  - `next_open`: 신호일(`t`)의 다음 거래일(`t+1`) 시가 체결
- 성과 계산은 다음 3개로 분해됩니다.
  - `holding_ret`: 전일 보유분(`position_prev`)의 마크투마켓 손익
  - `execution_ret`: 거래일 체결가(`exec_px`)와 당일 마크투마켓 가격(`mtm_px`) 차이 손익
  - `cost_ret`: 체결가 기준 비용(커미션+슬리피지) 차감

## 검증 절차(샘플 데이터)
아래 스니펫으로 `execution.price=close`와 `next_open`이 합리적으로 다른 결과를 내는지 확인할 수 있습니다.

```bash
python - <<'PY'
import copy
import pandas as pd
from src.backtest_engine import run_backtest

df = pd.DataFrame(
    {
        "Date": pd.to_datetime(["2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"]),
        "Open": [100, 106, 101, 108],
        "Close": [105, 102, 107, 106],
        "Adj Close": [105, 102, 107, 106],
        "target_position": [0.0, 1.0, 1.0, 0.0],
    }
)

base_cfg = {
    "execution": {"price": "close", "mark_to_market_price": "close"},
    "costs": {"commission_bps": 5, "slippage_bps": 5},
    "portfolio": {"position_size": 1.0, "initial_capital": 10000},
}

cfg_close = copy.deepcopy(base_cfg)
res_close, tr_close = run_backtest(df, cfg_close)

cfg_open = copy.deepcopy(base_cfg)
cfg_open["execution"]["price"] = "next_open"
res_open, tr_open = run_backtest(df, cfg_open)

print("=== close ===")
print(res_close[["Date", "position", "ret", "holding_ret", "execution_ret", "cost_ret", "strategy_net_ret", "equity"]])
print(tr_close)

print("=== next_open ===")
print(res_open[["Date", "position", "ret", "holding_ret", "execution_ret", "cost_ret", "strategy_net_ret", "equity"]])
print(tr_open)
PY
```

체크 포인트:
- `next_open`에서는 진입/청산 거래의 `signal_date`와 `execution_date`가 하루 차이(`t -> t+1`)인지 확인
- 동일 신호라도 `exec_px`가 달라 `execution_ret`, `cost_ret`, 최종 `equity`가 `close`와 다르게 나오는지 확인
