from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.user import UserAuthResponse, UserLoginRequest, UserSignupRequest
from backend.app.services.auth_service import AuthService

router = APIRouter()


@router.post("/signup", response_model=UserAuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: UserSignupRequest, db: Session = Depends(get_db)) -> UserAuthResponse:
    repository = UserRepository(db)
    if repository.get_by_email(payload.email):
        raise HTTPException(status_code=409, detail="이미 가입된 이메일입니다.")

    user = repository.create(
        name=payload.name,
        email=payload.email,
        password_hash=AuthService().hash_password(payload.password),
    )
    return UserAuthResponse(
        message="회원가입이 완료되었습니다.",
        user_id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/login", response_model=UserAuthResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)) -> UserAuthResponse:
    repository = UserRepository(db)
    user = repository.get_by_email(payload.email)
    if user is None or not AuthService().verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    return UserAuthResponse(
        message="로그인에 성공했습니다.",
        user_id=user.id,
        name=user.name,
        email=user.email,
        created_at=user.created_at,
    )
