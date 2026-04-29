"""基于LangGraph的多智能体旅行规划系统"""

import json
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from ..models.schemas import TripPlan, TripRequest
from ..services.llm_service import get_llm
from ..tools.amap_tools import query_weather, search_attractions, search_hotels
from .state import TripGraphState


PLANNER_SYSTEM_PROMPT = """你是智能旅行规划系统中的行程规划智能体。

你会收到用户需求、景点工具结果、天气工具结果和酒店工具结果。
请只基于输入信息进行规划,不要编造不存在的地点坐标。

输出要求:
1. 只返回JSON,不要返回Markdown代码块和解释文字。
2. JSON必须符合TripPlan结构。
3. 每天安排2-3个景点。
4. 每天包含早餐、午餐、晚餐。
5. weather_info尽量覆盖每天日期。
6. 预算字段必须包含景点、酒店、餐饮、交通和总计。
"""

REPAIR_SYSTEM_PROMPT = """你是JSON修复智能体。

你的任务是把上一次模型输出修复为合法TripPlan JSON。
只允许返回JSON对象,不要返回说明文字。
"""


class MultiAgentTripPlanner:
    """基于LangGraph状态图的旅行规划系统。"""

    def __init__(self):
        """初始化LangGraph工作流。"""
        print("🔄 开始初始化LangGraph旅行规划系统...")
        self.llm = get_llm()
        self.tools = {
            "search_attractions": search_attractions,
            "query_weather": query_weather,
            "search_hotels": search_hotels,
        }
        self.workflow_nodes = [
            "normalize_request",
            "search_attractions",
            "query_weather",
            "search_hotels",
            "plan_itinerary",
            "validate_plan",
            "repair_plan",
        ]
        self.graph = self._build_graph()
        print("✅ LangGraph旅行规划系统初始化成功")
        print(f"   工作流节点: {', '.join(self.workflow_nodes)}")
        print(f"   工具数量: {len(self.tools)}")

    def _build_graph(self):
        """构建旅行规划状态图。"""
        workflow = StateGraph(TripGraphState)

        workflow.add_node("normalize_request", self._normalize_request_node)
        workflow.add_node("search_attractions", self._search_attractions_node)
        workflow.add_node("query_weather", self._query_weather_node)
        workflow.add_node("search_hotels", self._search_hotels_node)
        workflow.add_node("plan_itinerary", self._plan_itinerary_node)
        workflow.add_node("validate_plan", self._validate_plan_node)
        workflow.add_node("repair_plan", self._repair_plan_node)

        workflow.add_edge(START, "normalize_request")
        workflow.add_edge("normalize_request", "search_attractions")
        workflow.add_edge("normalize_request", "query_weather")
        workflow.add_edge("normalize_request", "search_hotels")
        workflow.add_edge(
            ["search_attractions", "query_weather", "search_hotels"],
            "plan_itinerary",
        )
        workflow.add_edge("plan_itinerary", "validate_plan")
        workflow.add_conditional_edges(
            "validate_plan",
            self._route_after_validation,
            {
                "repair": "repair_plan",
                "end": END,
            },
        )
        workflow.add_edge("repair_plan", "validate_plan")

        return workflow.compile()

    def plan_trip(self, request: TripRequest, progress_callback=None) -> TripPlan:
        """
        使用LangGraph多节点协作生成旅行计划。

        Args:
            request: 旅行请求

        Returns:
            旅行计划
        """
        print(f"\n{'=' * 60}")
        print("🚀 开始LangGraph旅行规划工作流...")
        print(f"目的地: {request.city}")
        print(f"日期: {request.start_date} 至 {request.end_date}")
        print(f"天数: {request.travel_days}天")
        print(f"偏好: {', '.join(request.preferences) if request.preferences else '无'}")
        print(f"{'=' * 60}\n")

        state: TripGraphState = {
            "request": request,
            "repair_attempts": 0,
            "needs_repair": False,
            "progress_callback": progress_callback,
        }
        result = self.graph.invoke(state)
        trip_plan = result.get("trip_plan")
        if not trip_plan:
            error = result.get("validation_error") or "未知错误"
            raise RuntimeError(f"旅行计划生成失败: {error}")

        print(f"{'=' * 60}")
        print("✅ LangGraph旅行计划生成完成")
        print(f"{'=' * 60}\n")
        return trip_plan

    def _emit_progress(self, state: TripGraphState, progress: int, stage: str):
        callback = state.get("progress_callback")
        if callable(callback):
            callback(progress, stage)

    def get_workflow_summary(self) -> Dict[str, Any]:
        """返回工作流摘要,用于健康检查和论文说明。"""
        return {
            "framework": "LangGraph + LangChain",
            "nodes": self.workflow_nodes,
            "tools": list(self.tools.keys()),
            "execution": "fan-out information collection + planner + validator + repair",
        }

    def _normalize_request_node(self, state: TripGraphState) -> Dict[str, Any]:
        request = state["request"]
        print("🧭 节点 normalize_request: 校验和标准化用户需求")
        self._emit_progress(state, 12, "需求解析: 校验和标准化用户需求")
        if not request.city.strip():
            raise ValueError("目的地城市不能为空")
        return {
            "repair_attempts": state.get("repair_attempts", 0),
            "needs_repair": False,
        }

    def _search_attractions_node(self, state: TripGraphState) -> Dict[str, Any]:
        request = state["request"]
        print("📍 节点 search_attractions: 调用景点搜索工具")
        self._emit_progress(state, 25, "景点搜索: 调用高德POI检索")
        keywords = request.preferences[0] if request.preferences else "景点"
        results = self.tools["search_attractions"].invoke({
            "city": request.city,
            "keywords": keywords,
        })
        return {"attraction_results": results[:10]}

    def _query_weather_node(self, state: TripGraphState) -> Dict[str, Any]:
        request = state["request"]
        print("🌤️ 节点 query_weather: 调用天气查询工具")
        self._emit_progress(state, 38, "天气查询: 获取目的地天气预报")
        results = self.tools["query_weather"].invoke({"city": request.city})
        return {"weather_results": results[: max(request.travel_days, 1)]}

    def _search_hotels_node(self, state: TripGraphState) -> Dict[str, Any]:
        request = state["request"]
        print("🏨 节点 search_hotels: 调用酒店搜索工具")
        self._emit_progress(state, 50, "酒店查询: 根据住宿偏好检索酒店")
        results = self.tools["search_hotels"].invoke({
            "city": request.city,
            "accommodation": request.accommodation,
        })
        return {"hotel_results": results[:8]}

    def _plan_itinerary_node(self, state: TripGraphState) -> Dict[str, Any]:
        request = state["request"]
        print("📋 节点 plan_itinerary: LLM整合工具结果生成TripPlan JSON")
        self._emit_progress(state, 68, "行程生成: LLM整合工具结果")
        prompt = self._build_planner_prompt(state)
        response = self.llm.invoke([
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        content = str(response.content)
        print(f"LLM规划输出预览: {content[:300]}...")
        return {"planner_response": content}

    def _validate_plan_node(self, state: TripGraphState) -> Dict[str, Any]:
        print("✅ 节点 validate_plan: Pydantic校验TripPlan结构")
        self._emit_progress(state, 84, "结构校验: Pydantic校验TripPlan")
        try:
            trip_plan = self._parse_response(state.get("planner_response", ""))
            return {
                "trip_plan": trip_plan,
                "validation_error": "",
                "needs_repair": False,
            }
        except Exception as e:
            error = str(e)
            print(f"⚠️ TripPlan校验失败: {error}")
            return {
                "trip_plan": None,
                "validation_error": error,
                "needs_repair": True,
            }

    def _repair_plan_node(self, state: TripGraphState) -> Dict[str, Any]:
        attempts = state.get("repair_attempts", 0) + 1
        print(f"🛠️ 节点 repair_plan: 第{attempts}次修复JSON")
        self._emit_progress(state, 92, "结果修复: 修复模型输出JSON")
        prompt = self._build_repair_prompt(state)
        response = self.llm.invoke([
            SystemMessage(content=REPAIR_SYSTEM_PROMPT),
            HumanMessage(content=prompt),
        ])
        return {
            "planner_response": str(response.content),
            "repair_attempts": attempts,
        }

    def _route_after_validation(self, state: TripGraphState) -> str:
        if state.get("needs_repair") and state.get("repair_attempts", 0) < 1:
            return "repair"
        return "end"

    def _build_planner_prompt(self, state: TripGraphState) -> str:
        request = state["request"]
        payload = {
            "request": request.model_dump(),
            "attractions": state.get("attraction_results", []),
            "weather": state.get("weather_results", []),
            "hotels": state.get("hotel_results", []),
        }
        extra = f"\n用户额外要求: {request.free_text_input}" if request.free_text_input else ""
        return f"""请根据以下结构化数据生成{request.city}{request.travel_days}天旅行计划。

输入数据:
{json.dumps(payload, ensure_ascii=False, indent=2)}
{extra}

必须返回如下结构的JSON对象:
{{
  "city": "城市名称",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {{
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "交通方式",
      "accommodation": "住宿类型",
      "hotel": {{
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {{"longitude": 116.397128, "latitude": 39.916527}},
        "price_range": "300-500元",
        "rating": "4.5",
        "distance": "距离景点2公里",
        "type": "经济型酒店",
        "estimated_cost": 400
      }},
      "attractions": [
        {{
          "name": "景点名称",
          "address": "详细地址",
          "location": {{"longitude": 116.397128, "latitude": 39.916527}},
          "visit_duration": 120,
          "description": "景点详细描述",
          "category": "景点类别",
          "ticket_price": 60
        }}
      ],
      "meals": [
        {{"type": "breakfast", "name": "早餐推荐", "description": "早餐描述", "estimated_cost": 30}},
        {{"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 50}},
        {{"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}}
      ]
    }}
  ],
  "weather_info": [],
  "overall_suggestions": "总体建议",
  "budget": {{
    "total_attractions": 0,
    "total_hotels": 0,
    "total_meals": 0,
    "total_transportation": 0,
    "total": 0
  }}
}}
"""

    def _build_repair_prompt(self, state: TripGraphState) -> str:
        request = state["request"]
        return f"""原始请求:
{json.dumps(request.model_dump(), ensure_ascii=False, indent=2)}

校验错误:
{state.get("validation_error", "")}

需要修复的模型输出:
{state.get("planner_response", "")}

请修复为合法TripPlan JSON。"""

    def _parse_response(self, response: str) -> TripPlan:
        """从LLM响应中提取JSON并校验为TripPlan。"""
        if not response:
            raise ValueError("LLM返回内容为空")

        json_text = response.strip()
        if "```json" in json_text:
            start = json_text.find("```json") + 7
            end = json_text.find("```", start)
            json_text = json_text[start:end].strip()
        elif "```" in json_text:
            start = json_text.find("```") + 3
            end = json_text.find("```", start)
            json_text = json_text[start:end].strip()
        elif "{" in json_text and "}" in json_text:
            start = json_text.find("{")
            end = json_text.rfind("}") + 1
            json_text = json_text[start:end]

        data = json.loads(json_text)
        for index, day in enumerate(data.get("days", [])):
            if isinstance(day, dict):
                day["day_index"] = index
        return TripPlan(**data)


# 全局规划系统实例
_multi_agent_planner = None


def get_trip_planner_agent() -> MultiAgentTripPlanner:
    """获取旅行规划系统实例(单例模式)。"""
    global _multi_agent_planner

    if _multi_agent_planner is None:
        _multi_agent_planner = MultiAgentTripPlanner()

    return _multi_agent_planner
