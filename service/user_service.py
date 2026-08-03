from sqlalchemy.exc import IntegrityError
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from dao.user_dao import UserDao
from database.schema.user_schema import UserSchema
from database.schema.refresh_session_schema import RefreshSessionSchema
from models.user_history_model import UserHistoryCreate
from models.user_model import UserCreate, UserUpdate, UserResponse
from service.user_history_service import UserHistoryService

from jose import jwt, JWTError
from service.security_service import oauth2_scheme as oauth2_schema
import bcrypt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

SECRET_KEY = str(os.getenv("SECRET_KEY"))
ALGORITHM = str(os.getenv("ALGORITHM"))
TOKEN_EXPIRE_MINUTES = str(os.getenv("TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_HOURS = int(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS", "8"))


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)




class UserService:

    def __init__(self, database: Session):
        self.database = database
        self.dao = UserDao(database)
        self.history_service = UserHistoryService(database)

    def create(self, user: UserCreate) -> UserResponse:
        """
        Validate and Create a new user
        :param user: UserCreate that extend to UserModel
        :return:
        """
        existing_username = self.dao.find_by_username(user.username)
        if existing_username:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that username already exists")

        existing_email = self.dao.find_by_email(user.email)
        if existing_email:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that email already exists")

        if user.phone:
            existing_phone = self.dao.find_by_phone(user.phone)
            if existing_phone:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with that phone already exists")

        new_user_data = UserSchema(
            username=user.username,
            password=self._hash_password(user.password),
            name=user.name,
            last_name=user.last_name,
            email=user.email,
            phone=user.phone
        )
        try:
            user_created = self.dao.create(new_user_data)
            res = UserResponse.model_validate(user_created)
            return res.model_copy(
                update={"token":self.create_token(user_created.id, res)}
            )
            # return user_created

        except IntegrityError:
            self.dao.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User or data already exists")

    def get_user(self, user_id: int) -> UserSchema:
        user = self.dao.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    def get_user_login(self, username: str, password: str) -> UserResponse:
        user = self.dao.find_by_username(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        elif not self._verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Password is incorrect")

        history_data = UserHistoryCreate(
            user_id=user.id,
            action="LOGIN"
        )
        self.history_service.create_history(history_data)
        res = UserResponse.model_validate(user)
        return res.model_copy(
            update={"token":self.create_token(res.id, res)}
        )
        # return user

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserSchema]:
        return self.dao.find_all(skip=skip, limit=limit)

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserSchema:
        user = self.get_user(user_id)
        update_data = user_data.model_dump(exclude_unset=True)
        # Role and restaurant assignment are administrative operations.
        update_data.pop("user_type", None)

        if "username" in update_data:
            username = update_data["username"]
            if username == user.username:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
            update_data["username"] = username

        if "email" in update_data:
            email = update_data["email"]
            if email == user.email:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
            update_data["email"] = email

        if "phone" in update_data:
            phone = update_data["phone"]
            if phone == user.phone:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already exists")
            update_data["phone"] = phone

        if "password" in update_data:
            update_data["password"] = self._hash_password(update_data["password"])

        if "profile_pic_url" in update_data:
            update_data["profile_pic_url"] = update_data["profile_pic_url"]

        if "user_type" in update_data:
            update_data["user_type"] = update_data["user_type"]
        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            return self.dao.update(user)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Was not possible to update user data")

    def delete_user(self, user_id: int) -> None:
        user = self.dao.find_by_id(user_id)
        self.dao.delete(user)

    def bootstrap_admin(self, username: str, supplied_key: str) -> UserSchema:
        import secrets

        expected_key = os.getenv("BOOTSTRAP_ADMIN_KEY")
        if not expected_key:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="BOOTSTRAP_ADMIN_KEY is not configured")
        if not secrets.compare_digest(supplied_key, expected_key):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid bootstrap key")
        existing_admin = self.database.scalar(select(UserSchema).where(UserSchema.user_type == "admin"))
        if existing_admin:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An administrator already exists; bootstrap is disabled")
        user = self.dao.find_by_username(username)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user.user_type = "admin"
        user.restaurant_id = None
        return self.dao.update(user)


    @staticmethod
    def _hash_password(password: str) -> str:
        password_bytes = password.encode("utf-8")
        hashed_bytes = bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt(rounds=12),
        )
        return hashed_bytes.decode("utf-8")

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8"),
        )

    @staticmethod
    def create_token(user_id:int, user: UserResponse, token_duration=timedelta(minutes=int(TOKEN_EXPIRE_MINUTES)), token_type="access") -> str:
        token_date_expires = datetime.now(timezone.utc) + token_duration
        token_json = {
            "sub": str(user_id),
            "type": token_type,
            "exp": token_date_expires,
            "iat": datetime.now(timezone.utc),
            "role": user.user_type,
        }
        return jwt.encode(token_json, SECRET_KEY, ALGORITHM)

    def verify_token(self, token: str, expected_type: str = "access"):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != expected_type:
                raise ValueError
            user_id = int(str(payload.get("sub")))

            if user_id is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token without user ID")

            # user_id = int(user_id)

        except (JWTError, TypeError, ValueError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or expired")

        user = self.dao.find_by_id(user_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token user not found")
        return user

    def issue_refresh_token(
        self,
        user: UserSchema | UserResponse,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> str:
        now = _utcnow()
        expires_at = now + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
        jti = str(uuid.uuid4())
        family_id = str(uuid.uuid4())
        refresh_session = RefreshSessionSchema(
            jti=jti,
            family_id=family_id,
            user_id=user.id,
            issued_at=now,
            expires_at=expires_at,
            user_agent=(user_agent or "")[:255] or None,
            ip_address=(ip_address or "")[:64] or None,
        )
        self.database.add(refresh_session)
        self.database.commit()
        return self._encode_refresh_token(user.id, jti, family_id, expires_at)

    def rotate_refresh_token(
        self,
        token: str,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> tuple[UserSchema, str]:
        payload = self._decode_refresh_token(token)
        jti = payload["jti"]
        refresh_session = self.database.scalar(
            select(RefreshSessionSchema).where(RefreshSessionSchema.jti == jti)
        )
        if not refresh_session:
            raise HTTPException(status_code=401, detail="Refresh session not found")
        if refresh_session.revoked_at is not None:
            self._revoke_family(refresh_session.family_id)
            self.database.commit()
            raise HTTPException(status_code=401, detail="Refresh token reuse detected; session family revoked")
        now = _utcnow()
        if refresh_session.expires_at <= now:
            refresh_session.revoked_at = now
            self.database.commit()
            raise HTTPException(status_code=401, detail="Refresh token expired")

        user = self.dao.find_by_id(refresh_session.user_id)
        if not user or not user.status:
            raise HTTPException(status_code=401, detail="Refresh token user not found")

        new_jti = str(uuid.uuid4())
        expires_at = now + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
        replacement = RefreshSessionSchema(
            jti=new_jti,
            family_id=refresh_session.family_id,
            user_id=user.id,
            issued_at=now,
            expires_at=expires_at,
            user_agent=(user_agent or refresh_session.user_agent or "")[:255] or None,
            ip_address=(ip_address or refresh_session.ip_address or "")[:64] or None,
        )
        refresh_session.revoked_at = now
        refresh_session.last_used_at = now
        refresh_session.replaced_by_jti = new_jti
        try:
            self.database.add(replacement)
            self.database.commit()
        except Exception:
            self.database.rollback()
            raise
        return user, self._encode_refresh_token(user.id, new_jti, refresh_session.family_id, expires_at)

    def revoke_refresh_token(self, token: str) -> None:
        payload = self._decode_refresh_token(token, verify_exp=False)
        refresh_session = self.database.scalar(
            select(RefreshSessionSchema).where(RefreshSessionSchema.jti == payload["jti"])
        )
        if refresh_session and refresh_session.revoked_at is None:
            refresh_session.revoked_at = _utcnow()
            self.database.commit()

    def revoke_all_refresh_sessions(self, user_id: int) -> int:
        sessions = list(self.database.scalars(select(RefreshSessionSchema).where(
            RefreshSessionSchema.user_id == user_id,
            RefreshSessionSchema.revoked_at.is_(None),
        )).all())
        now = _utcnow()
        for refresh_session in sessions:
            refresh_session.revoked_at = now
        self.database.commit()
        return len(sessions)

    def list_refresh_sessions(self, user_id: int) -> list[RefreshSessionSchema]:
        now = _utcnow()
        return list(self.database.scalars(
            select(RefreshSessionSchema).where(
                RefreshSessionSchema.user_id == user_id,
                RefreshSessionSchema.revoked_at.is_(None),
                RefreshSessionSchema.expires_at > now,
            ).order_by(RefreshSessionSchema.issued_at.desc())
        ).all())

    def revoke_refresh_session_by_public_id(self, user_id: int, public_id: str) -> None:
        refresh_session = self.database.scalar(select(RefreshSessionSchema).where(
            RefreshSessionSchema.public_id == public_id,
            RefreshSessionSchema.user_id == user_id,
        ))
        if not refresh_session:
            raise HTTPException(status_code=404, detail="Refresh session not found")
        if refresh_session.revoked_at is None:
            refresh_session.revoked_at = _utcnow()
            self.database.commit()

    def _revoke_family(self, family_id: str) -> None:
        now = _utcnow()
        family = self.database.scalars(select(RefreshSessionSchema).where(
            RefreshSessionSchema.family_id == family_id,
            RefreshSessionSchema.revoked_at.is_(None),
        )).all()
        for refresh_session in family:
            refresh_session.revoked_at = now

    @staticmethod
    def _encode_refresh_token(user_id: int, jti: str, family_id: str, expires_at: datetime) -> str:
        return jwt.encode(
            {
                "sub": str(user_id),
                "type": "refresh",
                "jti": jti,
                "family": family_id,
                "iat": _utcnow(),
                "exp": expires_at,
            },
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

    @staticmethod
    def _decode_refresh_token(token: str, verify_exp: bool = True) -> dict:
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_exp": verify_exp},
            )
            if payload.get("type") != "refresh" or not payload.get("jti") or not payload.get("family"):
                raise ValueError
            return payload
        except (JWTError, TypeError, ValueError):
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")






