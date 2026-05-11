def test_trending_endpoint(client):
    response = client.get("/api/v1/trending")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["items"][0]["hashtags"] == ["viral"]
