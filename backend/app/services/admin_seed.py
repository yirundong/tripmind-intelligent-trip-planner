"""默认管理员初始化。"""

from sqlalchemy.exc import IntegrityError

from ..auth import hash_password
from ..config import get_settings
from ..database import SessionLocal
from ..db_models import User


def _available_username(db, preferred: str) -> str:
    """返回一个未被占用的管理员用户名。"""
    base = preferred.strip() or "系统管理员"
    username = base
    index = 1
    while db.query(User).filter(User.username == username).first():
        index += 1
        username = f"{base}{index}"
    return username


def seed_default_admin() -> None:
    """根据环境变量创建或修正默认管理员账号。

    该逻辑只在启动时运行一次：如果邮箱已存在，只确保它拥有管理员权限；
    如果邮箱不存在，则创建一个新的管理员。密码只在首次创建时写入，避免覆盖用户后续修改。
    """
    settings = get_settings()
    email = settings.default_admin_email.strip().lower()
    password = settings.default_admin_password
    username = settings.default_admin_username.strip() or "系统管理员"

    if not email or not password:
        print("ℹ️ 默认管理员未配置，跳过初始化")
        return
    if "@" not in email:
        print("⚠️ DEFAULT_ADMIN_EMAIL格式不正确，跳过初始化")
        return
    if len(password) < 6:
        print("⚠️ DEFAULT_ADMIN_PASSWORD至少需要6位，跳过初始化")
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            changed = False
            if not user.is_admin:
                user.is_admin = True
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True
            if changed:
                db.commit()
                print(f"✅ 默认管理员已修正: {email}")
            else:
                print(f"✅ 默认管理员已存在: {email}")
            return

        user = User(
            email=email,
            username=_available_username(db, username),
            hashed_password=hash_password(password),
            is_active=True,
            is_admin=True,
        )
        db.add(user)
        db.commit()
        print(f"✅ 默认管理员已创建: {email}")
    except IntegrityError:
        db.rollback()
        print("⚠️ 默认管理员初始化失败：邮箱或用户名冲突")
    finally:
        db.close()
