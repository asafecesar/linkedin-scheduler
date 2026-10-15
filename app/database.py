import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any

from app.config import settings

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS voice_samples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS voice_profile (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            bio TEXT DEFAULT '',
            tone_summary TEXT DEFAULT '',
            formality_level TEXT DEFAULT 'authentic',
            emoji_style TEXT DEFAULT 'minimal',
            paragraph_style TEXT DEFAULT 'punchy-breaks',
            custom_rules TEXT DEFAULT '',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            scheduled_at TIMESTAMP NULL,
            published_at TIMESTAMP NULL,
            linkedin_post_urn TEXT NULL,
            error_message TEXT NULL,
            image_url TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Safe migration for image_url column
    try:
        cursor.execute("ALTER TABLE posts ADD COLUMN image_url TEXT NULL")
    except Exception:
        pass

    # Seed initial voice profile if missing
    cursor.execute("SELECT id FROM voice_profile WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO voice_profile (id, bio, tone_summary, formality_level, emoji_style, paragraph_style, custom_rules)
            VALUES (
                1,
                'Software Engineer & Builder in Ottawa, ON | Cloud Architecture, AI Systems & Canadian Tech Ecosystem',
                'Direct, authentic, pragmatic, and high-signal. Speaks engineer-to-engineer about real-world software architecture trade-offs, developer productivity, and tech leadership in the Ottawa & Canadian IT market.',
                'authentic',
                'minimal',
                'punchy-breaks',
                '1. Always write strictly in natural North American English.\n2. Never use corporate cliches like "In today''s fast-paced world" or "I am thrilled to announce".\n3. Hook the reader in lines 1-2 with a bold contrast or hard-earned technical lesson before the fold.\n4. Keep paragraphs short (1-2 sentences) with clean spacing for mobile readability.\n5. Focus on real engineering trade-offs, developer leverage, and Canadian tech ecosystem realities.\n6. Close with an authentic, open-ended question that sparks thoughtful peer discussion.'
            )
        """)

    # Seed initial voice sample if table is empty
    cursor.execute("SELECT COUNT(*) as count FROM voice_samples")
    row = cursor.fetchone()
    if row and row["count"] == 0:
        cursor.execute("""
            INSERT INTO voice_samples (title, content, tags)
            VALUES (?, ?, ?)
        """, (
            'Example: Engineering Leverage & Automation',
            """Most engineers spend 40+ hours a week working hard, but zero hours thinking about leverage.

A few years ago, our engineering team was doing everything manually:
- Answering the exact same architecture questions in Slack
- Rebuilding recurring deployment scripts from scratch
- Constantly firefighting production alerts

Then we established one simple rule:
"If you do a manual task three times, document it or automate it."

The result?
We reclaimed 10+ engineering hours every single week.

Automation isn't about replacing engineers.
It's about removing cognitive friction so your team can focus on the systems that actually move the business forward.

What is one manual engineering workflow you automated this year that gave you the biggest return?""",
            'Engineering, Ottawa Tech, Productivity'
        ))

    conn.commit()
    conn.close()

# Settings helpers
def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cur.fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO settings (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
    """, (key, value))
    conn.commit()
    conn.close()

def get_all_settings() -> Dict[str, str]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT key, value FROM settings")
    rows = cur.fetchall()
    conn.close()
    return {r["key"]: r["value"] for r in rows}

# Voice Profile helpers
def get_voice_profile() -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM voice_profile WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {}

def update_voice_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    custom_rules = data.get("custom_rules", "")
    if isinstance(custom_rules, list):
        custom_rules = "\n".join([str(item) for item in custom_rules])

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE voice_profile
        SET bio = ?, tone_summary = ?, formality_level = ?, emoji_style = ?, paragraph_style = ?, custom_rules = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    """, (
        str(data.get("bio", "") or ""),
        str(data.get("tone_summary", "") or ""),
        str(data.get("formality_level", "authentic") or "authentic"),
        str(data.get("emoji_style", "minimal") or "minimal"),
        str(data.get("paragraph_style", "punchy-breaks") or "punchy-breaks"),
        str(custom_rules or "")
    ))
    conn.commit()
    conn.close()
    return get_voice_profile()

# Voice Samples helpers
def get_voice_samples() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM voice_samples ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_voice_sample(title: str, content: str, tags: str = "") -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO voice_samples (title, content, tags) VALUES (?, ?, ?)", (title, content, tags))
    conn.commit()
    sample_id = cur.lastrowid
    conn.close()
    return {"id": sample_id, "title": title, "content": content, "tags": tags}

def delete_voice_sample(sample_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM voice_samples WHERE id = ?", (sample_id,))
    conn.commit()
    conn.close()

# Posts helpers
def get_all_posts() -> List[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM posts 
        ORDER BY 
            CASE WHEN scheduled_at IS NOT NULL THEN scheduled_at ELSE created_at END DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_post_by_id(post_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def create_post(topic: str, content: str, status: str = "draft", scheduled_at: Optional[str] = None, image_url: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO posts (topic, content, status, scheduled_at, image_url, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (topic, content, status, scheduled_at, image_url))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return get_post_by_id(new_id)

def update_post(post_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    post = get_post_by_id(post_id)
    if not post:
        return None

    new_topic = updates.get("topic", post["topic"])
    new_content = updates.get("content", post["content"])
    new_status = updates.get("status", post["status"])
    new_scheduled_at = updates.get("scheduled_at", post["scheduled_at"])
    new_published_at = updates.get("published_at", post["published_at"])
    new_urn = updates.get("linkedin_post_urn", post["linkedin_post_urn"])
    new_error = updates.get("error_message", post["error_message"])
    new_image_url = updates.get("image_url", post.get("image_url"))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE posts
        SET topic = ?, content = ?, status = ?, scheduled_at = ?, published_at = ?, linkedin_post_urn = ?, error_message = ?, image_url = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (new_topic, new_content, new_status, new_scheduled_at, new_published_at, new_urn, new_error, new_image_url, post_id))
    conn.commit()
    conn.close()
    return get_post_by_id(post_id)

def delete_post(post_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()

def get_due_scheduled_posts() -> List[Dict[str, Any]]:
    now_iso = datetime.utcnow().isoformat() + "Z"
    now_local = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM posts
        WHERE status = 'scheduled' AND scheduled_at IS NOT NULL AND (scheduled_at <= ? OR scheduled_at <= ?)
        ORDER BY scheduled_at ASC
    """, (now_iso, now_local))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Auto-initialize database schema on module load
init_db()
