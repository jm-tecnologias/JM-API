import os
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from database.schema.user_schema import UserSchema
from utils.data_base_engine import get_database


load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign-in", scheme_name="UserAccessToken")
SECRET_KEY = os.getenv("SECRET_KEY") or ""
ALGORITHM = os.getenv("ALGORITHM") or "HS256"


def get_current_user(
    token: str = Depends(oauth2_scheme),
    database: Session = Depends(get_database),
) -> UserSchema:
    return resolve_access_token(token, database)


def resolve_access_token(token: str, database: Session) -> UserSchema:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise credentials_error
        user_id = int(payload["sub"])
    except (JWTError, KeyError, TypeError, ValueError):
        raise credentials_error

    user = database.get(UserSchema, user_id)
    if not user or not user.status:
        raise credentials_error
    return user


def require_roles(*roles: str) -> Callable:
    allowed = set(roles)

    def dependency(user: UserSchema = Depends(get_current_user)) -> UserSchema:
        if user.user_type not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return user

    return dependency
