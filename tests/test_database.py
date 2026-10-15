from app import database as db

def test_database_settings_crud():
    # Initially empty default
    assert db.get_setting("non_existent") == ""
    assert db.get_setting("non_existent", "default_val") == "default_val"

    # Save setting
    db.set_setting("test_key", "test_value")
    assert db.get_setting("test_key") == "test_value"

    # Overwrite setting
    db.set_setting("test_key", "updated_value")
    assert db.get_setting("test_key") == "updated_value"

    # Multiple settings
    db.set_setting("key2", "value2")
    all_settings = db.get_all_settings()
    assert all_settings.get("test_key") == "updated_value"
    assert all_settings.get("key2") == "value2"

def test_database_posts_crud():
    # Create post
    post = db.create_post(
        topic="Scaling Systems",
        content="Tips on scaling backend services...",
        status="draft",
        scheduled_at="2026-10-20T10:00:00",
        image_url="https://example.com/image.png"
    )
    post_id = post["id"]
    assert post_id is not None
    assert isinstance(post_id, int)
    assert post["topic"] == "Scaling Systems"
    assert post["status"] == "draft"

    # Get post by ID
    fetched = db.get_post_by_id(post_id)
    assert fetched is not None
    assert fetched["topic"] == "Scaling Systems"
    assert fetched["status"] == "draft"
    assert fetched["content"] == "Tips on scaling backend services..."

    # Update post
    updated = db.update_post(post_id, {
        "status": "scheduled",
        "content": "Updated content with more depth."
    })
    assert updated["status"] == "scheduled"
    assert updated["content"] == "Updated content with more depth."

    # List all posts
    posts = db.get_all_posts()
    assert len(posts) == 1
    assert posts[0]["id"] == post_id

    # Delete post
    db.delete_post(post_id)
    assert db.get_post_by_id(post_id) is None
    assert len(db.get_all_posts()) == 0
