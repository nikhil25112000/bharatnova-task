from uuid import uuid4


def test_create_post(client):
    response = client.post(
        "/api/v1/posts",
        json={
            "user_id": str(uuid4()),
            "caption": "Hello #viral #fyp",
            "media_url": "https://cdn.example.com/video.mp4",
            "bitrate_status": "ready",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["hashtags"] == ["viral", "fyp"]


def test_delete_post(client):
    response = client.delete(f"/api/v1/posts/{uuid4()}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["message"] == "Post deleted successfully"
