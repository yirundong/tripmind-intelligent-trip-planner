"""LangGraph旅行规划状态定义"""

from typing import Any, Dict, List, Optional, TypedDict

from ..models.schemas import TripPlan, TripRequest


class TripGraphState(TypedDict, total=False):
    """旅行规划图在各节点之间共享的状态。"""

    request: TripRequest
    attraction_results: List[Dict[str, Any]]
    weather_results: List[Dict[str, Any]]
    hotel_results: List[Dict[str, Any]]
    planner_response: str
    trip_plan: Optional[TripPlan]
    validation_error: str
    repair_attempts: int
    needs_repair: bool
    node_logs: List[str]
    progress_callback: Any
