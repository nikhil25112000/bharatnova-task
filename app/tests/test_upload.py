def test_upload_validation_rejects_invalid_extension(client):
    response = client.post(
        "/api/v1/upload/presigned-url",
        json={
            "filename": "video.avi",
            "content_type": "video/avi",
            "file_size": 1024,
        },
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["success"] is False


def test_upload_validation_accepts_mp4(client):
    response = client.post(
        "/api/v1/upload/presigned-url",
        json={
            "filename": "video.mp4",
            "content_type": "video/mp4",
            "file_size": 1024,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["expires_in"] == 300
