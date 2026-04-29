"""用户行程、收藏和仪表盘接口。"""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...auth import get_current_user
from ...database import get_db
from ...db_models import FavoritePlace, TripPlanRecord, User
from ...models.schemas import (
    DashboardStats,
    FavoriteCreate,
    FavoriteResponse,
    SavedTripDetail,
    SavedTripSummary,
    TripPlan,
    TripSaveRequest,
    TripUpdateRequest,
)


router = APIRouter(tags=["用户行程"])


def _summary(record: TripPlanRecord) -> SavedTripSummary:
    return SavedTripSummary(
        id=record.id,
        title=record.title,
        city=record.city,
        start_date=record.start_date,
        end_date=record.end_date,
        travel_days=record.travel_days,
        status=record.status,
        notes=record.notes or "",
        created_at=record.created_at.isoformat(),
        updated_at=record.updated_at.isoformat(),
    )


def _detail(record: TripPlanRecord) -> SavedTripDetail:
    return SavedTripDetail(
        **_summary(record).model_dump(),
        request_data=json.loads(record.request_data or "{}"),
        plan_data=TripPlan(**json.loads(record.plan_data)),
    )


def _favorite(item: FavoritePlace) -> FavoriteResponse:
    return FavoriteResponse(
        id=item.id,
        name=item.name,
        city=item.city or "",
        address=item.address or "",
        category=item.category or "景点",
        longitude=item.longitude or "",
        latitude=item.latitude or "",
        notes=item.notes or "",
        created_at=item.created_at.isoformat(),
    )


@router.get("/dashboard", response_model=DashboardStats, summary="用户仪表盘")
async def dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的行程、收藏和城市统计。"""
    trip_count = db.query(TripPlanRecord).filter(TripPlanRecord.user_id == current_user.id).count()
    favorite_count = db.query(FavoritePlace).filter(FavoritePlace.user_id == current_user.id).count()
    city_count = (
        db.query(func.count(func.distinct(TripPlanRecord.city)))
        .filter(TripPlanRecord.user_id == current_user.id)
        .scalar()
        or 0
    )
    latest_records = (
        db.query(TripPlanRecord)
        .filter(TripPlanRecord.user_id == current_user.id)
        .order_by(TripPlanRecord.updated_at.desc())
        .limit(5)
        .all()
    )
    return DashboardStats(
        trip_count=trip_count,
        favorite_count=favorite_count,
        city_count=city_count,
        latest_trips=[_summary(item) for item in latest_records],
    )


@router.get("/trips", response_model=list[SavedTripSummary], summary="我的行程列表")
async def list_trips(
    city: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """按城市和状态筛选当前用户的行程。"""
    query = db.query(TripPlanRecord).filter(TripPlanRecord.user_id == current_user.id)
    if city:
        query = query.filter(TripPlanRecord.city.contains(city.strip()))
    if status:
        query = query.filter(TripPlanRecord.status == status)
    records = query.order_by(TripPlanRecord.updated_at.desc()).all()
    return [_summary(item) for item in records]


@router.post("/trips", response_model=SavedTripDetail, summary="保存行程")
async def save_trip(
    payload: TripSaveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """手动保存一个行程计划。"""
    plan = payload.plan_data
    title = payload.title or f"{plan.city}{plan.start_date}旅行计划"
    record = TripPlanRecord(
        user_id=current_user.id,
        title=title,
        city=plan.city,
        start_date=plan.start_date,
        end_date=plan.end_date,
        travel_days=len(plan.days),
        status=payload.status,
        request_data=json.dumps(payload.request_data or {}, ensure_ascii=False),
        plan_data=json.dumps(plan.model_dump(), ensure_ascii=False),
        notes=payload.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return _detail(record)


@router.get("/trips/{trip_id}", response_model=SavedTripDetail, summary="行程详情")
async def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """读取当前用户的行程详情。"""
    record = db.query(TripPlanRecord).filter(
        TripPlanRecord.id == trip_id,
        TripPlanRecord.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="行程不存在")
    return _detail(record)


@router.put("/trips/{trip_id}", response_model=SavedTripDetail, summary="更新行程")
async def update_trip(
    trip_id: int,
    payload: TripUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新行程标题、状态、备注或完整计划JSON。"""
    record = db.query(TripPlanRecord).filter(
        TripPlanRecord.id == trip_id,
        TripPlanRecord.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="行程不存在")
    if payload.title is not None:
        record.title = payload.title
    if payload.status is not None:
        record.status = payload.status
    if payload.notes is not None:
        record.notes = payload.notes
    if payload.plan_data is not None:
        plan = payload.plan_data
        record.plan_data = json.dumps(plan.model_dump(), ensure_ascii=False)
        record.city = plan.city
        record.start_date = plan.start_date
        record.end_date = plan.end_date
        record.travel_days = len(plan.days)
    db.commit()
    db.refresh(record)
    return _detail(record)


@router.post("/trips/{trip_id}/duplicate", response_model=SavedTripDetail, summary="复制行程")
async def duplicate_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """复制一份当前用户的行程。"""
    record = db.query(TripPlanRecord).filter(
        TripPlanRecord.id == trip_id,
        TripPlanRecord.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="行程不存在")
    copied = TripPlanRecord(
        user_id=current_user.id,
        title=f"{record.title} 副本",
        city=record.city,
        start_date=record.start_date,
        end_date=record.end_date,
        travel_days=record.travel_days,
        status="draft",
        request_data=record.request_data,
        plan_data=record.plan_data,
        notes=record.notes,
    )
    db.add(copied)
    db.commit()
    db.refresh(copied)
    return _detail(copied)


@router.delete("/trips/{trip_id}", summary="删除行程")
async def delete_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除当前用户的行程。"""
    record = db.query(TripPlanRecord).filter(
        TripPlanRecord.id == trip_id,
        TripPlanRecord.user_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="行程不存在")
    db.delete(record)
    db.commit()
    return {"success": True, "message": "行程已删除"}


@router.get("/favorites", response_model=list[FavoriteResponse], summary="收藏列表")
async def list_favorites(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户收藏地点。"""
    items = (
        db.query(FavoritePlace)
        .filter(FavoritePlace.user_id == current_user.id)
        .order_by(FavoritePlace.created_at.desc())
        .all()
    )
    return [_favorite(item) for item in items]


@router.post("/favorites", response_model=FavoriteResponse, summary="添加收藏")
async def create_favorite(
    payload: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """收藏景点、酒店或餐厅。"""
    existing = db.query(FavoritePlace).filter(
        FavoritePlace.user_id == current_user.id,
        FavoritePlace.name == payload.name,
        FavoritePlace.city == payload.city,
    ).first()
    if existing:
        return _favorite(existing)
    item = FavoritePlace(user_id=current_user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return _favorite(item)


@router.delete("/favorites/{favorite_id}", summary="删除收藏")
async def delete_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除当前用户的收藏地点。"""
    item = db.query(FavoritePlace).filter(
        FavoritePlace.id == favorite_id,
        FavoritePlace.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="收藏不存在")
    db.delete(item)
    db.commit()
    return {"success": True, "message": "收藏已删除"}
