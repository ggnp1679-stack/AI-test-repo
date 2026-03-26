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
