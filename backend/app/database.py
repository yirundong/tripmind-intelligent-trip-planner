"""数据库连接和会话管理。"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import get_settings


settings = get_settings()

connect_args = {}
engine_options = {"pool_pre_ping": True}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # MySQL 连接长时间空闲后可能被服务端断开，回收连接可以减少演示时的偶发断连。
    engine_options["pool_recycle"] = 3600

engine = create_engine(settings.database_url, connect_args=connect_args, **engine_options)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI数据库会话依赖。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建数据库表。"""
    from . import db_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
