"""管理员后台接口。"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...auth import get_current_user
from ...database import get_db
from ...db_models import FavoritePlace, TripPlanRecord, TripPlanTask, User
from ...models.schemas import (
    AdminCityStat,
    AdminStats,
    AdminTaskSummary,
    AdminUserActiveUpdate,
    AdminUserRoleUpdate,
    AdminUserSummary,
)


router = APIRouter(prefix="/admin", tags=["管理员后台"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员权限。"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


def to_admin_user_summary(db: Session, user: User) -> AdminUserSummary:
    """组装后台用户摘要。"""
    return AdminUserSummary(
        id=user.id,
        email=user.email,
        username=user.username,
        is_admin=user.is_admin,
        is_active=user.is_active,
        trip_count=db.query(TripPlanRecord).filter(TripPlanRecord.user_id == user.id).count(),
        created_at=user.created_at.isoformat(),
    )


@router.get("/stats", response_model=AdminStats, summary="系统统计")
async def get_admin_stats(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """获取系统用户、行程、收藏和任务统计。"""
    task_count = db.query(TripPlanTask).count()
    succeeded_task_count = db.query(TripPlanTask).filter(TripPlanTask.status == "succeeded").count()
    failed_task_count = db.query(TripPlanTask).filter(TripPlanTask.status == "failed").count()
    running_task_count = db.query(TripPlanTask).filter(TripPlanTask.status.in_(["queued", "running"])).count()
    avg_task_progress = db.query(func.avg(TripPlanTask.progress)).scalar() or 0
    recent_since = datetime.utcnow() - timedelta(days=7)
    popular_cities = (
        db.query(TripPlanRecord.city, func.count(TripPlanRecord.id))
        .group_by(TripPlanRecord.city)
        .order_by(func.count(TripPlanRecord.id).desc())
        .limit(5)
        .all()
    )

    return AdminStats(
        user_count=db.query(User).count(),
        trip_count=db.query(TripPlanRecord).count(),
        favorite_count=db.query(FavoritePlace).count(),
        task_count=task_count,
        succeeded_task_count=succeeded_task_count,
        failed_task_count=failed_task_count,
        running_task_count=running_task_count,
        success_rate=round((succeeded_task_count / task_count * 100) if task_count else 0, 1),
        avg_task_progress=round(float(avg_task_progress), 1),
        recent_7d_task_count=db.query(TripPlanTask).filter(TripPlanTask.created_at >= recent_since).count(),
        popular_cities=[AdminCityStat(city=city or "未知城市", count=count) for city, count in popular_cities],
    )


@router.get("/tasks", response_model=list[AdminTaskSummary], summary="任务日志")
async def list_admin_tasks(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """查看最近的异步行程生成任务。"""
    query = db.query(TripPlanTask).order_by(TripPlanTask.updated_at.desc())
    if status:
        query = query.filter(TripPlanTask.status == status)
    tasks = query.limit(limit).all()
    users = {
        user.id: user.username
        for user in db.query(User).filter(User.id.in_([task.user_id for task in tasks] or [0])).all()
    }
    return [
        AdminTaskSummary(
            id=task.id,
            user_id=task.user_id,
            username=users.get(task.user_id, ""),
            city=task.city or "",
            status=task.status,
            progress=task.progress,
            stage=task.stage,
            trip_id=task.trip_id,
            error_message=task.error_message or "",
            created_at=task.created_at.isoformat(),
            updated_at=task.updated_at.isoformat(),
        )
        for task in tasks
    ]


@router.get("/users", response_model=list[AdminUserSummary], summary="用户列表")
async def list_admin_users(
    limit: int = Query(default=50, ge=1, le=200),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """查看系统用户及其行程数量。"""
    users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
    result = []
    for user in users:
        result.append(to_admin_user_summary(db, user))
    return result


@router.patch("/users/{user_id}/role", response_model=AdminUserSummary, summary="设置管理员权限")
async def update_user_admin_role(
    user_id: int,
    payload: AdminUserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """授予或取消用户的管理员权限。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.id == current_user.id and not payload.is_admin:
        raise HTTPException(status_code=400, detail="不能取消自己的管理员权限")

    if user.is_admin and not payload.is_admin:
        admin_count = db.query(User).filter(User.is_admin.is_(True), User.is_active.is_(True)).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="系统至少需要保留一个启用的管理员")

    user.is_admin = payload.is_admin
    db.commit()
    db.refresh(user)
    return to_admin_user_summary(db, user)


@router.patch("/users/{user_id}/active", response_model=AdminUserSummary, summary="启用或停用用户")
async def update_user_active_status(
    user_id: int,
    payload: AdminUserActiveUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """启用或停用用户账号。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if user.id == current_user.id and not payload.is_active:
        raise HTTPException(status_code=400, detail="不能停用自己的账号")

    if user.is_admin and user.is_active and not payload.is_active:
        admin_count = db.query(User).filter(User.is_admin.is_(True), User.is_active.is_(True)).count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="系统至少需要保留一个启用的管理员")

    user.is_active = payload.is_active
    db.commit()
    db.refresh(user)
    return to_admin_user_summary(db, user)
