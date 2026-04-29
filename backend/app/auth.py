"""认证、密码哈希和Token工具。"""

import base64
import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .config import get_settings
from .database import get_db
from .db_models import User


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    """使用PBKDF2-HMAC-SHA256生成密码哈希。"""
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return f"pbkdf2_sha256${_b64url_encode(salt)}${_b64url_encode(digest)}"


def verify_password(password: str, stored_hash: str) -> bool:
    """校验密码。"""
    try:
        algorithm, salt_text, digest_text = stored_hash.split("$", 2)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = _b64url_decode(salt_text)
        expected = _b64url_decode(digest_text)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return secrets.compare_digest(actual, expected)
    except Exception:
        return False


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """创建HS256访问Token。"""
    settings = get_settings()
    now = datetime.utcnow()
    expires = now + (expires_delta or timedelta(minutes=settings.jwt_expire_minutes))
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    signing_input = ".".join([
        _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8")),
        _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
    ])
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{signing_input}.{_b64url_encode(signature)}"


def decode_access_token(token: str) -> dict:
    """解码并校验HS256访问Token。"""
    settings = get_settings()
    try:
        header_text, payload_text, signature_text = token.split(".")
        signing_input = f"{header_text}.{payload_text}"
        expected = hmac.new(
            settings.jwt_secret_key.encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not secrets.compare_digest(_b64url_decode(signature_text), expected):
            raise ValueError("invalid signature")
        payload = json.loads(_b64url_decode(payload_text))
        if int(payload.get("exp", 0)) < int(datetime.utcnow().timestamp()):
            raise ValueError("token expired")
        return payload
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态已失效,请重新登录",
        ) from exc


def get_user_by_identity(db: Session, identity: str) -> Optional[User]:
    """按邮箱或用户名查找用户。"""
    return db.query(User).filter((User.email == identity) | (User.username == identity)).first()


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> User:
    """要求用户登录。"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_access_token(token)
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已停用")
    return user


def get_optional_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """用户可选登录依赖。"""
    if not authorization.startswith("Bearer "):
        return None
    return get_current_user(authorization=authorization, db=db)
