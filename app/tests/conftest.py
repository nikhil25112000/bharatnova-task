import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

os.environ["APP_ENV"] = "test"

from app.api.deps import (  # noqa: E402
    get_post_service,
    get_search_service,
    get_trending_service,
    get_upload_service,
)
from app.main import app  # noqa: E402


class MockPostService:
    async def create_post(self, payload):
        return {
            "id": uuid4(),
            "user_id": payload.user_id,
            "caption": payload.caption,
            "media_url": str(payload.media_url),
            "bitrate_status": payload.bitrate_status.value,
            "hashtags": ["viral", "fyp"],
            "created_at": datetime.now(timezone.utc),
        }

    async def delete_post(self, _post_id):
        return None

    async def get_post(self, _post_id):
        raise NotImplementedError

    async def list_posts(self, *, cursor, limit):
        return {"items": [], "next_cursor": None}


class MockSearchService:
    async def search_posts(self, query, limit):
        return [
            {
                "id": uuid4(),
                "user_id": uuid4(),
                "caption": f"Search result for {query}",
                "media_url": "https://cdn.example.com/video.mp4",
                "bitrate_status": "ready",
                "hashtags": ["viral"],
                "created_at": datetime.now(timezone.utc),
            }
        ][:limit]


class MockTrendingService:
    async def get_trending_posts(self):
        return [
            {
                "id": str(uuid4()),
                "user_id": str(uuid4()),
                "caption": "Trending post #viral",
                "media_url": "https://cdn.example.com/trending.mp4",
                "bitrate_status": "ready",
                "hashtags": ["viral"],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]


class MockUploadService:
    async def generate_presigned_url(self, _payload):
        return type(
            "UploadResponse",
            (),
            {
                "model_dump": lambda self, mode="json": {
                    "upload_url": "https://s3.example.com/upload",
                    "file_url": "https://cdn.example.com/file.mp4",
                    "expires_in": 300,
                }
            },
        )()


@pytest.fixture
def client():
    app.dependency_overrides[get_post_service] = lambda: MockPostService()
    app.dependency_overrides[get_search_service] = lambda: MockSearchService()
    app.dependency_overrides[get_trending_service] = lambda: MockTrendingService()
    app.dependency_overrides[get_upload_service] = lambda: MockUploadService()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
