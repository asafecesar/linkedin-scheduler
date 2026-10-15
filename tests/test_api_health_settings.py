import pytest

@pytest.mark.asyncio
async def test_health_check_endpoint(async_client):
    res = await async_client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "ollama_online" in data
    assert "linkedin_configured" in data

@pytest.mark.asyncio
async def test_settings_get_and_save(async_client):
    # Save settings
    payload = {
        "user_name": "Test Engineer",
        "user_headline": "Senior Tech Lead",
        "ollama_model": "qwen2.5:14b",
        "ollama_base_url": "http://127.0.0.1:11434"
    }
    save_res = await async_client.post("/api/settings", json=payload)
    assert save_res.status_code == 200
    save_data = save_res.json()
    assert save_data["success"] is True

    # Retrieve settings
    get_res = await async_client.get("/api/settings")
    assert get_res.status_code == 200
    settings = get_res.json()
    assert settings["user_name"] == "Test Engineer"
    assert settings["user_headline"] == "Senior Tech Lead"
    assert settings["ollama_model"] == "qwen2.5:14b"
