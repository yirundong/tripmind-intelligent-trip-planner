"""POI 补充能力接口。

地图搜索、天气和路线统一放在 map.py；这里仅保留结果页仍在使用的图片查询。
"""

from fastapi import APIRouter, HTTPException

from ...services.unsplash_service import get_unsplash_service

router = APIRouter(prefix="/poi", tags=["POI"])


@router.get(
    "/photo",
    summary="获取景点图片",
    description="根据景点名称从 Unsplash 获取展示图片",
)
async def get_attraction_photo(name: str):
    """根据景点名称查询展示图片。"""
    try:
        unsplash_service = get_unsplash_service()
        photo_url = unsplash_service.get_photo_url(f"{name} China landmark")
        if not photo_url:
            photo_url = unsplash_service.get_photo_url(name)

        return {
            "success": True,
            "message": "获取图片成功",
            "data": {
                "name": name,
                "photo_url": photo_url,
            },
        }
    except Exception as e:
        print(f"❌ 获取景点图片失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取景点图片失败: {str(e)}",
        )
