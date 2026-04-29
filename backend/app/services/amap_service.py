"""高德地图REST服务封装"""

from typing import Any, Dict, List, Optional

import httpx

from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo


class AmapService:
    """高德地图服务封装类。"""

    def __init__(self):
        """初始化服务。"""
        settings = get_settings()
        if not settings.amap_api_key:
            raise ValueError("高德地图API Key未配置,请在.env文件中设置AMAP_API_KEY")

        self.api_key = settings.amap_api_key
        self.base_url = "https://restapi.amap.com"
        self.timeout = 20.0

    def _get(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """调用高德REST接口并返回JSON。"""
        request_params = {**params, "key": self.api_key}
        url = f"{self.base_url}{path}"
        response = httpx.get(url, params=request_params, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()

        if str(payload.get("status", "1")) != "1":
            info = payload.get("info") or payload.get("infocode") or "未知错误"
            raise RuntimeError(f"高德地图接口调用失败: {info}")

        return payload

    @staticmethod
    def _parse_location(value: Any) -> Optional[Location]:
        if isinstance(value, Location):
            return value
        if isinstance(value, dict):
            longitude = value.get("longitude") or value.get("lng") or value.get("lon")
            latitude = value.get("latitude") or value.get("lat")
            if longitude is not None and latitude is not None:
                try:
                    return Location(longitude=float(longitude), latitude=float(latitude))
                except (TypeError, ValueError):
                    return None
        if isinstance(value, str) and "," in value:
            lng, lat = value.split(",", 1)
            try:
                return Location(longitude=float(lng.strip()), latitude=float(lat.strip()))
            except ValueError:
                return None
        return None

    @staticmethod
    def _poi_to_model(item: Dict[str, Any]) -> Optional[POIInfo]:
        location = AmapService._parse_location(item.get("location"))
        if not location:
            return None

        address = item.get("address")
        if isinstance(address, list):
            address = " ".join(str(part) for part in address)

        return POIInfo(
            id=str(item.get("id") or ""),
            name=str(item.get("name") or ""),
            type=str(item.get("type") or item.get("typecode") or ""),
            address=str(address or item.get("pname") or item.get("cityname") or ""),
            location=location,
            tel=str(item.get("tel")) if item.get("tel") else None,
        )

    def search_poi(self, keywords: str, city: str, citylimit: bool = True) -> List[POIInfo]:
        """
        搜索POI。

        Args:
            keywords: 搜索关键词
            city: 城市
            citylimit: 是否限制在城市范围内

        Returns:
            POI信息列表
        """
        try:
            payload = self._get(
                "/v3/place/text",
                {
                    "keywords": keywords,
                    "city": city,
                    "citylimit": "true" if citylimit else "false",
                    "extensions": "all",
                    "offset": 10,
                    "page": 1,
                },
            )
            pois = []
            for item in payload.get("pois", []):
                if isinstance(item, dict):
                    poi = self._poi_to_model(item)
                    if poi:
                        pois.append(poi)
            return pois

        except Exception as e:
            print(f"❌ POI搜索失败: {str(e)}")
            return []

    def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        查询天气。

        Args:
            city: 城市名称

        Returns:
            天气信息列表
        """
        try:
            payload = self._get(
                "/v3/weather/weatherInfo",
                {
                    "city": city,
                    "extensions": "all",
                },
            )
            forecasts = payload.get("forecasts") or []
            if forecasts and isinstance(forecasts[0], dict):
                casts = forecasts[0].get("casts") or []
                return [
                    WeatherInfo(
                        date=str(cast.get("date") or ""),
                        day_weather=str(cast.get("dayweather") or ""),
                        night_weather=str(cast.get("nightweather") or ""),
                        day_temp=cast.get("daytemp") or 0,
                        night_temp=cast.get("nighttemp") or 0,
                        wind_direction=str(cast.get("daywind") or ""),
                        wind_power=str(cast.get("daypower") or ""),
                    )
                    for cast in casts
                    if isinstance(cast, dict)
                ]

            return []

        except Exception as e:
            print(f"❌ 天气查询失败: {str(e)}")
            return []

    def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """
        地理编码(地址转坐标)。

        Args:
            address: 地址
            city: 城市

        Returns:
            经纬度坐标
        """
        try:
            params: Dict[str, Any] = {"address": address}
            if city:
                params["city"] = city

            payload = self._get("/v3/geocode/geo", params)
            geocodes = payload.get("geocodes") or []
            if geocodes and isinstance(geocodes[0], dict):
                return self._parse_location(geocodes[0].get("location"))
            return None

        except Exception as e:
            print(f"❌ 地理编码失败: {str(e)}")
            return None

    def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """
        获取POI详情。

        Args:
            poi_id: POI ID

        Returns:
            POI详情信息
        """
        try:
            payload = self._get("/v3/place/detail", {"id": poi_id})
            pois = payload.get("pois") or []
            if pois and isinstance(pois[0], dict):
                return pois[0]
            return {}

        except Exception as e:
            print(f"❌ 获取POI详情失败: {str(e)}")
            return {}

    @staticmethod
    def _location_to_text(location: Optional[Location]) -> str:
        if not location:
            return ""
        return f"{location.longitude},{location.latitude}"

    @staticmethod
    def _route_description(steps: List[Dict[str, Any]]) -> str:
        instructions = []
        for step in steps:
            instruction = step.get("instruction") if isinstance(step, dict) else None
            if instruction:
                instructions.append(str(instruction))
        return "；".join(instructions[:5])

    def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking",
    ) -> Dict[str, Any]:
        """
        规划路线。

        Args:
            origin_address: 起点地址
            destination_address: 终点地址
            origin_city: 起点城市
            destination_city: 终点城市
            route_type: 路线类型 (walking/driving/transit)

        Returns:
            路线信息
        """
        try:
            origin = self.geocode(origin_address, origin_city)
            destination = self.geocode(destination_address, destination_city)
            if not origin or not destination:
                return {}

            if route_type == "driving":
                path = "/v3/direction/driving"
                params = {
                    "origin": self._location_to_text(origin),
                    "destination": self._location_to_text(destination),
                    "extensions": "base",
                }
            elif route_type == "transit":
                path = "/v3/direction/transit/integrated"
                params = {
                    "origin": self._location_to_text(origin),
                    "destination": self._location_to_text(destination),
                    "city": origin_city or destination_city or "",
                    "cityd": destination_city or origin_city or "",
                }
            else:
                path = "/v3/direction/walking"
                params = {
                    "origin": self._location_to_text(origin),
                    "destination": self._location_to_text(destination),
                }

            payload = self._get(path, params)
            route = payload.get("route") or {}

            if route_type == "transit":
                transits = route.get("transits") or []
                if not transits:
                    return {}
                first = transits[0]
                segments = first.get("segments") or []
                description_parts = []
                for segment in segments[:5]:
                    if not isinstance(segment, dict):
                        continue
                    bus = segment.get("bus") or {}
                    walking = segment.get("walking") or {}
                    if bus.get("buslines"):
                        line = bus["buslines"][0]
                        description_parts.append(str(line.get("name") or "公交"))
                    elif walking.get("steps"):
                        description_parts.append(self._route_description(walking["steps"]))

                return {
                    "distance": float(first.get("distance") or 0),
                    "duration": int(float(first.get("duration") or 0)),
                    "route_type": route_type,
                    "description": "；".join(part for part in description_parts if part)
                    or f"{origin_address} 到 {destination_address} 的公交路线",
                }

            paths = route.get("paths") or []
            if not paths:
                return {}
            first_path = paths[0]
            return {
                "distance": float(first_path.get("distance") or 0),
                "duration": int(float(first_path.get("duration") or 0)),
                "route_type": route_type,
                "description": self._route_description(first_path.get("steps") or [])
                or f"{origin_address} 到 {destination_address} 的{route_type}路线",
            }

        except Exception as e:
            print(f"❌ 路线规划失败: {str(e)}")
            return {}


# 创建全局服务实例
_amap_service = None


def get_amap_service() -> AmapService:
    """获取高德地图服务实例(单例模式)"""
    global _amap_service

    if _amap_service is None:
        _amap_service = AmapService()

    return _amap_service
