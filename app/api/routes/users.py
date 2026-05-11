from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.deps import get_user_service
from app.core.constants import success_response
from app.schemas.user_schema import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
):
    user = await service.create_user(payload)
    return success_response("User created successfully", UserRead.model_validate(user).model_dump(mode="json"))


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    user_id: UUID,
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user(user_id)
    return success_response("User fetched successfully", UserRead.model_validate(user).model_dump(mode="json"))
