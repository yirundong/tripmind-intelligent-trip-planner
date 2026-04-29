"""用户注册、登录和个人资料接口。"""

import json
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...auth import create_access_token, get_current_user, get_user_by_identity, hash_password, verify_password
from ...config import get_settings
from ...database import get_db
from ...db_models import User
from ...models.schemas import TokenResponse, UserCreate, UserLogin, UserProfile, UserUpdate


router = APIRouter(prefix="/auth", tags=["用户认证"])


def to_user_profile(user: User) -> UserProfile:
    """ORM用户转接口模型。"""
    try:
        preferences = json.loads(user.default_preferences or "[]")
    except json.JSONDecodeError:
        preferences = []
    return UserProfile(
        id=user.id,
        email=user.email,
        username=user.username,
        avatar_url=user.avatar_url or "",
        default_city=user.default_city or "",
        default_transportation=user.default_transportation or "公共交通",
        default_accommodation=user.default_accommodation or "经济型酒店",
        default_preferences=preferences,
        is_admin=user.is_admin,
    )


@router.post("/register", response_model=TokenResponse, summary="注册")
async def register(payload: UserCreate, db: Session = Depends(get_db)):
    """注册新用户并直接返回登录Token。"""
    email = payload.email.strip().lower()
    username = payload.username.strip()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="邮箱格式不正确")

    is_first_user = db.query(User).count() == 0
    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(payload.password),
        is_admin=is_first_user,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="邮箱或用户名已被使用") from exc
    db.refresh(user)

    settings = get_settings()
    token = create_access_token(str(user.id), timedelta(minutes=settings.jwt_expire_minutes))
    return TokenResponse(access_token=token, user=to_user_profile(user))


@router.post("/login", response_model=TokenResponse, summary="登录")
async def login(payload: UserLogin, db: Session = Depends(get_db)):
    """使用邮箱或用户名登录。"""
    user = get_user_by_identity(db, payload.identity.strip().lower()) or get_user_by_identity(db, payload.identity.strip())
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已停用")

    settings = get_settings()
    token = create_access_token(str(user.id), timedelta(minutes=settings.jwt_expire_minutes))
    return TokenResponse(access_token=token, user=to_user_profile(user))


@router.get("/me", response_model=UserProfile, summary="当前用户")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户资料。"""
    return to_user_profile(current_user)


@router.put("/me", response_model=UserProfile, summary="更新个人资料")
async def update_me(
    payload: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新当前用户资料和默认旅行偏好。"""
    if payload.username is not None:
        current_user.username = payload.username.strip()
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url.strip()
    if payload.default_city is not None:
        current_user.default_city = payload.default_city.strip()
    if payload.default_transportation is not None:
        current_user.default_transportation = payload.default_transportation
    if payload.default_accommodation is not None:
        current_user.default_accommodation = payload.default_accommodation
    if payload.default_preferences is not None:
        current_user.default_preferences = json.dumps(payload.default_preferences, ensure_ascii=False)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="用户名已被使用") from exc
    db.refresh(current_user)
    return to_user_profile(current_user)
