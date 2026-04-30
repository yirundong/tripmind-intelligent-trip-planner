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


def _free_default_username(db, email: str, username: str) -> None:
    """确保默认管理员可以使用固定用户名。"""
    holder = db.query(User).filter(User.email != email, User.username == username).first()
    if holder:
        holder.username = _available_username(db, f"{username}用户")
        db.flush()


def seed_default_admin() -> None:
    """根据环境变量创建或修正默认管理员账号。

    如果邮箱已存在，会修正用户名、管理员权限和启用状态；
    如果邮箱不存在，则创建一个新的管理员。密码只在首次创建时写入，避免覆盖用户后续修改。
    同时会把其他管理员收敛为普通用户，保持“内置唯一管理员”的权限模型。
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
            if user.username != username:
                _free_default_username(db, email, username)
                user.username = username
                changed = True
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
            demoted_count = (
                db.query(User)
                .filter(User.email != email, User.is_admin.is_(True))
                .update({User.is_admin: False}, synchronize_session=False)
            )
            if demoted_count:
                db.commit()
                print(f"✅ 已收敛管理员账号数量，仅保留默认管理员: {email}")
            return

        _free_default_username(db, email, username)
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            is_active=True,
            is_admin=True,
        )
        db.add(user)
        db.commit()
        db.query(User).filter(User.email != email, User.is_admin.is_(True)).update(
            {User.is_admin: False},
            synchronize_session=False,
        )
        db.commit()
        print(f"✅ 默认管理员已创建: {email}")
    except IntegrityError:
        db.rollback()
        print("⚠️ 默认管理员初始化失败：邮箱或用户名冲突")
    finally:
        db.close()
