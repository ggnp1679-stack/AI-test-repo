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

## 주요 파일
- `PLAN.md`: 구현 계획
- `DECISIONS.md`: 사용자가 선택해야 하는 항목 정리
- `src/create_user_config.py`: 입력 기반 사용자 설정 파일 생성 스크립트
