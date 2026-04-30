"""旅行规划API路由"""

import json
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from ...auth import get_optional_current_user
from ...database import get_db
from ...database import SessionLocal
from ...db_models import TripPlanRecord, TripPlanTask, User
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    TripPlanTaskResponse,
)
from ...agents.trip_planner_agent import get_trip_planner_agent

router = APIRouter(prefix="/trip", tags=["旅行规划"])

# 本地演示环境用线程池即可避免阻塞 FastAPI 事件循环。
# 若部署到生产环境，可平滑替换为 Celery/RQ 等独立任务队列。
task_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="trip-plan-task")


def _task_response(task: TripPlanTask) -> TripPlanTaskResponse:
    """统一数据库任务模型到 API 响应模型的转换。"""
    return TripPlanTaskResponse(
        id=task.id,
        status=task.status,
        progress=task.progress,
        stage=task.stage,
        city=task.city or "",
        trip_id=task.trip_id,
        error_message=task.error_message or "",
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
    )


def _update_task(db: Session, task: TripPlanTask, *, status: str, progress: int, stage: str, error_message: str = ""):
    """写入任务进度，供前端轮询展示 Agent 工作流状态。"""
    task.status = status
    task.progress = progress
    task.stage = stage
    task.error_message = error_message
    db.commit()
    db.refresh(task)


def _update_task_by_id(task_id: int, *, status: str, progress: int, stage: str, error_message: str = "", trip_id: int | None = None):
    """用独立会话更新任务状态，避免后台工作流并发回调共享同一个 Session。"""
    db = SessionLocal()
    try:
        task = db.query(TripPlanTask).filter(TripPlanTask.id == task_id).first()
        if not task:
            return
        task.status = status
        task.progress = progress
        task.stage = stage
        task.error_message = error_message
        if trip_id is not None:
            task.trip_id = trip_id
        db.commit()
    finally:
        db.close()


def _run_trip_plan_task(task_id: int):
    """后台线程执行旅行规划任务，并把阶段进度持续落库。"""
    db = SessionLocal()
    try:
        task = db.query(TripPlanTask).filter(TripPlanTask.id == task_id).first()
        if not task:
            return
        request_data = task.request_data
        user_id = task.user_id
    finally:
        db.close()

    try:
        _update_task_by_id(task_id, status="running", progress=5, stage="任务启动: 初始化智能体工作流")
        request = TripRequest(**json.loads(request_data))

        def update_progress(progress: int, stage: str):
            _update_task_by_id(task_id, status="running", progress=progress, stage=stage)

        agent = get_trip_planner_agent()
        trip_plan = agent.plan_trip(request, progress_callback=update_progress)

        _update_task_by_id(task_id, status="running", progress=94, stage="数据保存: 写入用户行程库")
        db = SessionLocal()
        try:
            record = TripPlanRecord(
                user_id=user_id,
                title=f"{trip_plan.city}{trip_plan.start_date}旅行计划",
                city=trip_plan.city,
                start_date=trip_plan.start_date,
                end_date=trip_plan.end_date,
                travel_days=len(trip_plan.days),
                status="saved",
                request_data=json.dumps(request.model_dump(), ensure_ascii=False),
                plan_data=json.dumps(trip_plan.model_dump(), ensure_ascii=False),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            record_id = record.id
        finally:
            db.close()

        _update_task_by_id(task_id, status="succeeded", progress=100, stage="行程生成完成", trip_id=record_id)
    except Exception as exc:
        _update_task_by_id(
            task_id,
            status="failed",
            progress=100,
            stage="行程生成失败",
            error_message=str(exc),
        )


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(
    request: TripRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """兼容旧前端的同步规划接口；新页面默认使用 /tasks 异步任务。"""
    try:
        agent = get_trip_planner_agent()
        trip_plan = await run_in_threadpool(agent.plan_trip, request)
        trip_id = None

        if current_user:
            record = TripPlanRecord(
                user_id=current_user.id,
                title=f"{trip_plan.city}{trip_plan.start_date}旅行计划",
                city=trip_plan.city,
                start_date=trip_plan.start_date,
                end_date=trip_plan.end_date,
                travel_days=len(trip_plan.days),
                status="saved",
                request_data=json.dumps(request.model_dump(), ensure_ascii=False),
                plan_data=json.dumps(trip_plan.model_dump(), ensure_ascii=False),
            )
            db.add(record)
            db.commit()
            db.refresh(record)
            trip_id = record.id

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan,
            trip_id=trip_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {str(e)}"
        )


@router.post(
    "/tasks",
    response_model=TripPlanTaskResponse,
    summary="创建异步旅行规划任务",
    description="提交旅行需求并立即返回任务ID,前端可轮询任务状态"
)
async def create_plan_task(
    request: TripRequest,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """创建长耗时旅行规划任务。"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录后再生成行程")

    task = TripPlanTask(
        user_id=current_user.id,
        status="queued",
        progress=0,
        stage="任务已创建,等待执行",
        city=request.city,
        request_data=json.dumps(request.model_dump(), ensure_ascii=False),
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    task_executor.submit(_run_trip_plan_task, task.id)
    return _task_response(task)


@router.get(
    "/tasks/{task_id}",
    response_model=TripPlanTaskResponse,
    summary="查询旅行规划任务",
    description="查询异步旅行规划任务的状态、进度和结果行程ID"
)
async def get_plan_task(
    task_id: int,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """查询当前用户的旅行规划任务状态。"""
    if not current_user:
        raise HTTPException(status_code=401, detail="请先登录")

    task = db.query(TripPlanTask).filter(
        TripPlanTask.id == task_id,
        TripPlanTask.user_id == current_user.id,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return _task_response(task)


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        # 检查Agent是否可用
        agent = get_trip_planner_agent()
        workflow = agent.get_workflow_summary()

        return {
            "status": "healthy",
            "service": "trip-planner",
            "framework": workflow["framework"],
            "nodes": workflow["nodes"],
            "tools": workflow["tools"],
            "execution": workflow["execution"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用: {str(e)}"
        )
