"""
启动脚本
"""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
        log_level="info",
    )
