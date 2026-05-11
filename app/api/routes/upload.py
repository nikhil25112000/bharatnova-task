from fastapi import APIRouter, Depends, status

from app.api.deps import get_upload_service
from app.core.constants import success_response
from app.middleware.file_validator import validate_upload_payload
from app.schemas.upload_schema import PresignedUrlRequest
from app.services.upload_service import UploadService

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/presigned-url", status_code=status.HTTP_200_OK)
async def create_presigned_url(
    payload: PresignedUrlRequest,
    service: UploadService = Depends(get_upload_service),
):
    validate_upload_payload(payload)
    response = await service.generate_presigned_url(payload)
    return success_response("Presigned URL generated successfully", response.model_dump(mode="json"))
