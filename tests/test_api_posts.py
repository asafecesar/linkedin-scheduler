import pytest

@pytest.mark.asyncio
async def test_create_and_get_post(async_client):
    payload = {
        "topic": "Clean Code Principles",
        "content": "Keep functions small and focused on a single responsibility.",
        "status": "draft"
    }
    res = await async_client.post("/api/posts", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["topic"] == payload["topic"]
    assert created["content"] == payload["content"]
    assert created["status"] == "draft"
    post_id = created["id"]

    # Get by ID
    get_res = await async_client.get(f"/api/posts/{post_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == post_id

    # List posts
    list_res = await async_client.get("/api/posts")
    assert list_res.status_code == 200
    posts = list_res.json()
    assert len(posts) == 1
    assert posts[0]["id"] == post_id

@pytest.mark.asyncio
async def test_update_and_delete_post(async_client):
    # Create
    create_res = await async_client.post("/api/posts", json={
        "topic": "DevOps Practices",
        "content": "Automate CI/CD pipelines.",
        "status": "draft"
    })
    post_id = create_res.json()["id"]

    # Update
    update_res = await async_client.put(f"/api/posts/{post_id}", json={
        "content": "Updated: Automate CI/CD pipelines and deployment checks.",
        "status": "scheduled",
        "scheduled_at": "2026-11-01T14:00:00"
    })
    assert update_res.status_code == 200
    updated = update_res.json()
    assert updated["content"] == "Updated: Automate CI/CD pipelines and deployment checks."
    assert updated["status"] == "scheduled"

    # Delete
    del_res = await async_client.delete(f"/api/posts/{post_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # Verify 404 after deletion
    get_after = await async_client.get(f"/api/posts/{post_id}")
    assert get_after.status_code == 404

@pytest.mark.asyncio
async def test_publish_now_without_credentials_fails_gracefully(async_client):
    create_res = await async_client.post("/api/posts", json={
        "topic": "Test Post",
        "content": "Content to publish.",
        "status": "draft"
    })
    post_id = create_res.json()["id"]

    # Try publish without LinkedIn configured -> expect failure status code and error message
    pub_res = await async_client.post(f"/api/posts/{post_id}/publish-now")
    assert pub_res.status_code == 500
    assert "detail" in pub_res.json()

    # Verify post marked as failed in database
    get_res = await async_client.get(f"/api/posts/{post_id}")
    assert get_res.json()["status"] == "failed"
    assert get_res.json()["error_message"] is not None
