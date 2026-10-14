import asyncio
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app import database as db
from app import linkedin_service

scheduler: Optional[AsyncIOScheduler] = None
is_processing = False

async def process_due_posts():
    global is_processing
    if is_processing:
        return
    is_processing = True

    try:
        due_posts = db.get_due_scheduled_posts()
        if not due_posts:
            return

        print(f"[Scheduler] {len(due_posts)} post(s) ready for publication.")

        for post in due_posts:
            post_id = post["id"]
            topic = post.get("topic") or "Untitled Post"
            print(f"[Scheduler] Processing post #{post_id}: '{topic}'...")

            token, _ = linkedin_service.get_credentials()
            if not token:
                print(f"[Scheduler] Post #{post_id} failed: LinkedIn token not configured.")
                db.update_post(post_id, {
                    "status": "failed",
                    "error_message": "LinkedIn access token is not configured in Settings."
                })
                continue

            try:
                result = await linkedin_service.publish_to_linkedin(
                    content=post["content"],
                    image_url=post.get("image_url")
                )
                print(f"[Scheduler] Post #{post_id} published successfully! URN: {result.get('post_urn')}")
                db.update_post(post_id, {
                    "status": "published",
                    "published_at": datetime.utcnow().isoformat() + "Z",
                    "linkedin_post_urn": result.get("post_urn"),
                    "error_message": None
                })
            except Exception as e:
                print(f"[Scheduler] Error publishing post #{post_id}: {e}")
                db.update_post(post_id, {
                    "status": "failed",
                    "error_message": str(e)
                })
    except Exception as e:
        print(f"[Scheduler] Unexpected error during scheduling cycle: {e}")
    finally:
        is_processing = False

def start_scheduler(interval_seconds: int = 30):
    global scheduler
    if scheduler and scheduler.running:
        return
    scheduler = AsyncIOScheduler()
    scheduler.add_job(process_due_posts, 'interval', seconds=interval_seconds, id="linkedin_post_checker", replace_existing=True)
    scheduler.start()
    print(f"[Scheduler] APScheduler started (checking every {interval_seconds}s).")

def stop_scheduler():
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        print("[Scheduler] APScheduler stopped.")
