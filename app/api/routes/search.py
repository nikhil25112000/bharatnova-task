from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_search_service
from app.core.config import get_settings
from app.core.constants import success_response
from app.schemas.post_schema import PostRead
from app.services.search_service import SearchService

router = APIRouter(tags=["Search"])
settings = get_settings()


@router.get("/search", status_code=status.HTTP_200_OK)
async def search_posts(
    query: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=settings.default_page_limit, ge=1, le=settings.max_page_limit),
    service: SearchService = Depends(get_search_service),
):
    posts = await service.search_posts(query, limit)
    data = {"items": [PostRead.model_validate(post).model_dump(mode="json") for post in posts]}
    return success_response("Search results fetched successfully", data)
