import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"\n🚀 Starting LinkedIn AI Scheduler on http://{settings.host}:{settings.port}")
    print(f"📖 Interactive Swagger documentation at http://{settings.host}:{settings.port}/docs\n")
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.reload)
