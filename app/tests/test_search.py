def test_search_endpoint(client):
    response = client.get("/api/v1/search", params={"query": "viral", "limit": 10})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["data"]["items"]) == 1
    assert "viral" in payload["data"]["items"][0]["caption"].lower()
