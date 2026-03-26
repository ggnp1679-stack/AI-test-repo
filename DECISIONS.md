# 사용자 결정 항목 (체크리스트)

아래 항목을 확정하면 `config/user.yaml`에 반영한다.

## A. 데이터
- [ ] symbol: `SPY` 또는 `^GSPC`
- [ ] start_date: `YYYY-MM-DD`
- [ ] end_date: `YYYY-MM-DD`

## B. 전략
- [ ] strategy_name: `sma_cross`
- [ ] short_window: 정수 (예: 50)
- [ ] long_window: 정수 (예: 200)

## C. 체결
- [ ] execution_price: `next_open` 또는 `close`
- [ ] rebalance_frequency: `daily` (v1 고정 권장)

## D. 비용
- [ ] commission_bps: 예) 5 (0.05%)
- [ ] slippage_bps: 예) 5 (0.05%)

## E. 포지션
- [ ] long_only: true/false (v1은 true 권장)
- [ ] position_size: 0~1 (예: 1.0)

## F. 초기자본/출력
- [ ] initial_capital: 예) 100000
- [ ] output_dir: 예) `results`

## G. 리포팅
- [ ] benchmark: `buy_and_hold` 사용 여부
- [ ] 저장 형식: csv/json
