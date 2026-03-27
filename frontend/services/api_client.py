import requests


BACKEND_ROOT_URL = "http://127.0.0.1:8000"


def get_backend_status() -> dict:
    try:
        response = requests.get(f"{BACKEND_ROOT_URL}/api/v1/health", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"status": "unreachable", "detail": str(exc)}


def get_config_status() -> dict:
    try:
        response = requests.get(f"{BACKEND_ROOT_URL}/api/v1/rates/config-status", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"api_key_configured": False, "detail": str(exc)}


def get_latest_rates() -> dict:
    try:
        response = requests.get(f"{BACKEND_ROOT_URL}/api/v1/rates/latest", timeout=3)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"source": "koreaexim", "announcement_date": None, "rates": [], "detail": str(exc)}


def sync_latest_rates() -> dict:
    try:
        response = requests.post(f"{BACKEND_ROOT_URL}/api/v1/rates/sync", timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            try:
                detail = exc.response.json().get("detail", "")
            except ValueError:
                detail = exc.response.text
        return {"message": "sync_failed", "detail": detail or str(exc)}


def get_currency_history(cur_unit: str, limit: int = 30) -> dict:
    try:
        response = requests.get(
            f"{BACKEND_ROOT_URL}/api/v1/rates/history/{cur_unit}",
            params={"limit": limit},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        return {"cur_unit": cur_unit.upper(), "history": [], "detail": str(exc)}


def signup_user(name: str, email: str, password: str) -> dict:
    try:
        response = requests.post(
            f"{BACKEND_ROOT_URL}/api/v1/auth/signup",
            json={"name": name, "email": email, "password": password},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            try:
                detail = exc.response.json().get("detail", "")
            except ValueError:
                detail = exc.response.text
        return {"message": "signup_failed", "detail": detail or str(exc)}


def login_user(email: str, password: str) -> dict:
    try:
        response = requests.post(
            f"{BACKEND_ROOT_URL}/api/v1/auth/login",
            json={"email": email, "password": password},
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            try:
                detail = exc.response.json().get("detail", "")
            except ValueError:
                detail = exc.response.text
        return {"message": "login_failed", "detail": detail or str(exc)}


def logout_user() -> dict:
    try:
        response = requests.post(
            f"{BACKEND_ROOT_URL}/api/v1/auth/logout",
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            try:
                detail = exc.response.json().get("detail", "")
            except ValueError:
                detail = exc.response.text
        return {"message": "logout_failed", "detail": detail or str(exc)}
