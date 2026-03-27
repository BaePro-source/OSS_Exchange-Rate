# Exchange Rate Dashboard

한국수출입은행 환율 정보를 기반으로 실시간 변동 사항을 보여주기 위한 Full-Stack 프로젝트 초기 구조입니다.

## Stack

- Frontend: Streamlit
- Backend: FastAPI
- Database: SQLite3
- Package / Python version management: uv

## Project Structure

```text
.
|-- backend/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- db/
|   |   |-- models/
|   |   `-- services/
|   |-- data/
|   `-- main.py
|-- frontend/
|   |-- components/
|   |-- pages/
|   |-- services/
|   `-- app.py
|-- .env.example
|-- .python-version
`-- pyproject.toml
```

## Quick Start

`uv`가 설치되어 있다면 아래 순서로 실행할 수 있습니다.

## Requirements

필수로 필요한 패키지/런타임은 아래와 같습니다.

- Python `>= 3.13`
- `uv`

프로젝트 의존성 목록:

- `fastapi`
- `httpx`
- `pandas`
- `pydantic-settings`
- `requests`
- `sqlalchemy`
- `streamlit`
- `uvicorn[standard]`

`uv sync`로 위 패키지가 자동 설치됩니다.

## Run

아래 명령으로 바로 실행할 수 있습니다. (터미널 2개 권장)

```bash
uv sync
cp .env.example .env
uv run uvicorn backend.main:app --reload
uv run streamlit run frontend/app.py
```

## Environment Variables

프로젝트 루트의 `.env` 파일에 API 키를 넣으면 됩니다. 이 파일은 `.gitignore`에 포함되어 Git에 올라가지 않습니다.

```bash
KOREA_EXIM_API_KEY=발급받은_API_KEY
EXCHANGE_DB_PATH=backend/data/exchange_rates.db
```

## SQLite Schema

현재 DB 구조는 아래처럼 두 테이블로 나뉩니다.

- `exchange_rate_snapshots`: 데이터를 수집한 날짜/시점
- `exchange_rates`: 해당 시점에 포함된 개별 통화 환율

이렇게 나누는 이유는 한 번 API를 호출할 때 여러 통화가 함께 오기 때문입니다. 즉 "수집 이벤트 1건"과 "그 안의 환율 목록 여러 건"을 분리해서 저장하는 구조입니다.

## Next Step

- 한국수출입은행 Open API 연동
- 환율 이력 저장용 SQLite 스키마 작성
- Streamlit 실시간 대시보드 구성

## Implemented API Endpoints

- `GET /api/v1/health`
- `GET /api/v1/rates/config-status`
- `POST /api/v1/rates/sync`
- `GET /api/v1/rates/latest`
- `GET /api/v1/rates/history/{cur_unit}?limit=30`

`POST /api/v1/rates/sync`는 오늘 날짜를 우선 조회하고, 데이터가 없으면 최근 날짜를 최대 10일 전까지 거슬러 올라가며 가장 최신 환율 데이터를 저장합니다.
