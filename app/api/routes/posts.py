from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_post_service
from app.core.config import get_settings
from app.core.constants import success_response
from app.schemas.post_schema import PostCreate, PostListResponse, PostRead
from app.services.post_service import PostService

router = APIRouter(prefix="/posts", tags=["Posts"])
settings = get_settings()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    service: PostService = Depends(get_post_service),
):
    post = await service.create_post(payload)
    return success_response("Post created successfully", PostRead.model_validate(post).model_dump(mode="json"))


@router.get("", status_code=status.HTTP_200_OK)
async def list_posts(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=settings.default_page_limit, ge=1, le=settings.max_page_limit),
    service: PostService = Depends(get_post_service),
):
    payload = await service.list_posts(cursor=cursor, limit=limit)
    response = PostListResponse(
        items=[PostRead.model_validate(post) for post in payload["items"]],
        next_cursor=payload["next_cursor"],
    )
    return success_response("Posts fetched successfully", response.model_dump(mode="json"))


@router.get("/{post_id}", status_code=status.HTTP_200_OK)
async def get_post(
    post_id: UUID,
    service: PostService = Depends(get_post_service),
):
    post = await service.get_post(post_id)
    return success_response("Post fetched successfully", PostRead.model_validate(post).model_dump(mode="json"))


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
    post_id: UUID,
    service: PostService = Depends(get_post_service),
):
    await service.delete_post(post_id)
    return success_response("Post deleted successfully", {})
