# Exchange Rate Dashboard

한국수출입은행 환율 데이터를 기반으로 한 Full-Stack 환율 대시보드 프로젝트입니다.

- Backend: FastAPI
- Frontend: Streamlit
- DB: SQLite
- ORM: SQLAlchemy
- Settings: pydantic-settings
- HTTP 클라이언트: requests
- Dev tool: uv (uv run / uv sync)

## 프로젝트 구조

```text
.
|-- backend/
|   |-- app/
|   |   |-- api/           # REST API 라우터
|   |   |-- core/          # 설정
|   |   |-- db/            # DB 초기화, 세션
|   |   |-- models/        # SQLAlchemy 모델
|   |   |-- repositories/  # DB CRUD 로직
|   |   |-- schemas/       # Pydantic DTO
|   |   `-- services/      # 외부 API 연동 및 비즈니스 로직
|   |-- data/              # SQLite DB 파일 경로
|   `-- main.py            # FastAPI 앱 진입점
|-- frontend/
|   |-- app.py             # Streamlit 메인 앱
|   |-- components/        # 구성 요소 (현재 비어있음)
|   `-- services/          # 백엔드 호출용 API 클라이언트
|-- .env.example
`-- pyproject.toml
```

## 기능 요약

1. 회원 인증
   - `POST /api/v1/auth/signup`
   - `POST /api/v1/auth/login`
   - `POST /api/v1/auth/logout`
2. 환율 수집 & 상태
   - `GET /api/v1/rates/config-status`
   - `POST /api/v1/rates/sync`
   - `POST /api/v1/rates/backfill` (기간 단위 환율 적재)
3. 환율 조회
   - `GET /api/v1/rates/latest`
   - `GET /api/v1/rates/history/{cur_unit}?limit=30`
4. 헬스 체크
   - `GET /api/v1/health`
5. Streamlit 대시보드
   - 로그인/회원가입 UI
   - 최신 환율 조회 및 저장 버튼
   - 통화별 히스토리 차트 & 지도 시각화

## 필수 환경

- Python >= 3.13
- `.venv` 가상환경 (권장)
- `uv` (uv run, uv sync)

## 설치 및 실행

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install uv
uv sync
cp .env.example .env
# 백엔드 실행
uv run uvicorn backend.main:app --reload
# 다른 터미널에서 프론트엔드 실행
uv run streamlit run frontend/app.py
```

## 환경 변수

`.env`:

```bash
KOREA_EXIM_API_KEY=발급받은_API_KEY
EXCHANGE_DB_PATH=backend/data/exchange_rates.db
```

추가 설정 (선택)

```bash
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_HOST=127.0.0.1
FRONTEND_PORT=8501
```

## DB 스키마 (현재 구현)

- `exchange_rate_snapshots`: API 호출 일자/소스/저장 시각
- `exchange_rates`: `exchange_rate_snapshots` FK, 통화코드, 통화명, 매매기준율, TTB, TTS
- `users`: 아이디/이름/이메일/비밀번호 해시/생성일

## 개발 팁

- API 키를 못 넣었을 때 `GET /api/v1/rates/config-status` 로 상태 확인
- 이미 가입된 이메일로 `POST /api/v1/auth/signup` 시 409 반환
- `POST /api/v1/rates/sync` 는 최근 10일 내에서 가장 최신 데이터를 자동 조회
- `POST /api/v1/rates/backfill` 로 날짜 범위 데이터를 일괄 채움

## 현재 완료 상태

- FastAPI 백엔드 CRUD 및 API 완료
- Streamlit 대시보드 구현 완료
- 회원가입/로그인/로그아웃 기능 완성
- 한국수출입은행 Open API 기반 환율 수집 기능 구현
