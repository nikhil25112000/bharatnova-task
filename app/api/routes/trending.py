from fastapi import APIRouter, Depends, status

from app.api.deps import get_trending_service
from app.core.constants import success_response
from app.services.trending_service import TrendingService

router = APIRouter(tags=["Trending"])


@router.get("/trending", status_code=status.HTTP_200_OK)
async def get_trending_posts(
    service: TrendingService = Depends(get_trending_service),
):
    posts = await service.get_trending_posts()
    return success_response("Trending posts fetched successfully", {"items": posts})
