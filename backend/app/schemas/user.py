from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UserSignupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if "@" not in cleaned or "." not in cleaned.split("@")[-1]:
            raise ValueError("올바른 이메일 형식이 아닙니다.")
        return cleaned


class UserLoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if "@" not in cleaned or "." not in cleaned.split("@")[-1]:
            raise ValueError("올바른 이메일 형식이 아닙니다.")
        return cleaned


class UserAuthResponse(BaseModel):
    message: str
    user_id: int
    name: str
    email: str
    created_at: datetime
