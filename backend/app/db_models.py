"""SQLAlchemy ORM模型。"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    """系统用户。"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str] = mapped_column(String(500), default="")
    default_city: Mapped[str] = mapped_column(String(80), default="")
    default_transportation: Mapped[str] = mapped_column(String(80), default="公共交通")
    default_accommodation: Mapped[str] = mapped_column(String(80), default="经济型酒店")
    default_preferences: Mapped[str] = mapped_column(Text, default="[]")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    trip_plans: Mapped[list["TripPlanRecord"]] = relationship(
        "TripPlanRecord",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    favorites: Mapped[list["FavoritePlace"]] = relationship(
        "FavoritePlace",
        back_populates="owner",
        cascade="all, delete-orphan",
    )


class TripPlanRecord(Base):
    """用户保存的旅行计划。"""

    __tablename__ = "trip_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    start_date: Mapped[str] = mapped_column(String(20), nullable=False)
    end_date: Mapped[str] = mapped_column(String(20), nullable=False)
    travel_days: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(30), default="saved")
    request_data: Mapped[str] = mapped_column(Text, default="{}")
    plan_data: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped[User] = relationship("User", back_populates="trip_plans")


class TripPlanTask(Base):
    """长耗时旅行规划任务。"""

    __tablename__ = "trip_plan_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="queued", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    stage: Mapped[str] = mapped_column(String(120), default="任务已创建")
    city: Mapped[str] = mapped_column(String(80), default="", index=True)
    request_data: Mapped[str] = mapped_column(Text, default="{}")
    trip_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("trip_plans.id"), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FavoritePlace(Base):
    """用户收藏的地点。"""

    __tablename__ = "favorite_places"
    __table_args__ = (
        UniqueConstraint("user_id", "name", "city", name="uq_favorite_user_name_city"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(80), default="")
    address: Mapped[str] = mapped_column(String(500), default="")
    category: Mapped[str] = mapped_column(String(80), default="景点")
    longitude: Mapped[str] = mapped_column(String(50), default="")
    latitude: Mapped[str] = mapped_column(String(50), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner: Mapped[User] = relationship("User", back_populates="favorites")
