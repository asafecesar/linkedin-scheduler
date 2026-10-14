import uvicorn
import os
import sys

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"\n🚀 Iniciando LinkedIn AI Scheduler em http://{host}:{port}")
    print(f"📖 Documentação Swagger em http://{host}:{port}/docs\n")
    reload_enabled = os.environ.get("RELOAD", "false").lower() in ("true", "1")
    uvicorn.run("app.main:app", host=host, port=port, reload=reload_enabled)
