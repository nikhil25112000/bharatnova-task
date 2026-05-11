from pydantic import BaseModel, Field


class PresignedUrlRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content_type: str = Field(min_length=3, max_length=100)
    file_size: int = Field(gt=0, le=104857600)


class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_url: str
    expires_in: int
