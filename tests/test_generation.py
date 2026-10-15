import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_generation_batch_endpoint(async_client):
    mock_posts = [
        {
            "hook": "Modular architecture is a superpower in 2026:",
            "content": "Draft post about modular architecture #SoftwareEngineering #Architecture",
            "angle": "Practical Insight",
            "hashtags": ["#SoftwareEngineering", "#Architecture"],
            "estimated_read_time": "1 min"
        }
    ]

    with patch("app.routers.generation.ai_manager.generate_batch", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = {
            "posts": mock_posts,
            "is_mock": False,
            "provider": "ollama"
        }

        res = await async_client.post("/api/generate/batch", json={
            "topic": "Modular Architecture in 2026",
            "count": 1,
            "angle": "Practical Insight"
        })

        assert res.status_code == 200
        data = res.json()
        assert len(data["posts"]) == 1
        assert data["posts"][0]["content"] == mock_posts[0]["content"]

@pytest.mark.asyncio
async def test_generation_refine_endpoint(async_client):
    mock_refined = "Punchier version: Ship early and iterate with continuous feedback."

    with patch("app.routers.generation.ai_manager.refine_post", new_callable=AsyncMock) as mock_refine:
        mock_refine.return_value = {
            "refined": mock_refined,
            "provider": "ollama"
        }

        res = await async_client.post("/api/generate/refine", json={
            "content": "Original long-winded text that should be shortened.",
            "instruction": "Make it punchier"
        })

        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["refined"] == mock_refined
