"""LangChain工具: 高德地图能力封装"""

from typing import Any, Dict, List

from langchain_core.tools import tool

from ..services.amap_service import get_amap_service


def _model_list_to_dict(items: List[Any]) -> List[Dict[str, Any]]:
    return [item.model_dump() if hasattr(item, "model_dump") else item for item in items]


@tool
def search_attractions(city: str, keywords: str) -> List[Dict[str, Any]]:
    """根据城市和偏好关键词搜索景点POI。"""
    service = get_amap_service()
    pois = service.search_poi(keywords=keywords, city=city, citylimit=True)
    return _model_list_to_dict(pois)


@tool
def search_hotels(city: str, accommodation: str) -> List[Dict[str, Any]]:
    """根据城市和住宿偏好搜索酒店POI。"""
    service = get_amap_service()
    keyword = accommodation if accommodation else "酒店"
    if "酒店" not in keyword and "宾馆" not in keyword and "民宿" not in keyword:
        keyword = f"{keyword}酒店"
    pois = service.search_poi(keywords=keyword, city=city, citylimit=True)
    return _model_list_to_dict(pois)


@tool
def query_weather(city: str) -> List[Dict[str, Any]]:
    """查询城市未来天气预报。"""
    service = get_amap_service()
    weather = service.get_weather(city)
    return _model_list_to_dict(weather)
