# S&P500 백테스트 프로젝트 계획 (v1)

## 1. 목적
S&P500 관련 자산(SPY 또는 ^GSPC)에 대해 설정 기반 백테스트 시스템을 구축한다.
코드 수정 없이 설정 파일만 바꿔 전략/기간/비용 가정 등을 변경할 수 있어야 한다.

## 2. 범위 (v1)
- 단일 자산
- 롱 온리(Long-only)
- 일봉 데이터
- 기본 전략: SMA 크로스오버 (short/long)

## 3. 산출물
- 실행 가능한 CLI 프로그램 (`src/main.py`)
- 설정 파일 (`config/default.yaml`, `config/user.yaml`)
- 결과물:
  - `results/equity_curve.csv`
  - `results/trades.csv`
  - `results/summary.json`

## 4. 시스템 구조
- `src/config_loader.py` : 설정 로딩/검증
- `src/data_loader.py` : 데이터 다운로드 및 정리
- `src/strategy_ma.py` : SMA 전략 신호 생성
- `src/backtest_engine.py` : 체결/비용 반영/자산곡선 계산
- `src/metrics.py` : 성과지표 계산
- `src/main.py` : 실행 진입점

## 5. 데이터 정책
- 기본 소스: yfinance
- 자산 코드:
  - SPY (ETF)
  - ^GSPC (지수)
- 사용 컬럼: Date, Open, High, Low, Close, Adj Close, Volume
- 누수 방지:
  - 신호는 t일 데이터로 생성
  - 체결은 t+1 시가(기본값)

## 6. 전략 정책
- SMA Cross:
  - 매수: SMA(short) > SMA(long)
  - 청산: SMA(short) <= SMA(long)
- 포지션:
  - in/out (1 또는 0)
  - 기본 비중 100%

## 7. 거래/비용 가정
- 체결 규칙: next_open (기본)
- 비용:
  - commission_bps
  - slippage_bps
- 총 거래비용 = (commission + slippage) * 거래대금

## 8. 성과 지표
- CAGR
- MDD
- Sharpe Ratio (연 252일 기준)
- Volatility (연환산)
- Win Rate
- Number of Trades
- Buy&Hold 대비 수익률

## 9. 검증 계획
- 기본: 단일 기간 백테스트
- 확장:
  - 인샘플/아웃샘플 분리
  - 파라미터 민감도(예: 20/100, 50/200)
  - Walk-forward 분석

## 10. 일정 (권장)
1) Day 1: 설정/데이터/전략 인터페이스 구현  
2) Day 2: 엔진/지표 구현 + 기본 실행  
3) Day 3: 결과 저장/리포트 정리 + 검증 케이스 추가
