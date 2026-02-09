"""
发票合并系统 - FastAPI 主应用
MVT架构: Model-View-Template(Schema)
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.views import api_router

# 创建应用
app = FastAPI(
    title="发票合并系统 API",
    description="发票上传、识别、合并服务 - MVT架构",
    version="1.0.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件目录
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app.mount("/api/v1/files", StaticFiles(directory=str(UPLOAD_DIR)), name="files")

# 注册路由
app.include_router(api_router)


@app.on_event("startup")
async def startup():
    """应用启动时初始化数据库和OCR服务"""
    print("🚀 系统启动中...")

    # 初始化数据库
    init_db()
    print("✅ 数据库初始化完成")

    # 预加载OCR服务（后台挂载，加快后续识别速度）
    try:
        from app.services.ocr_service import OCRService
        print("⏳ 正在初始化 RapidOCR 服务...")
        OCRService.get_ocr()
        print("✅ RapidOCR 服务已预加载，识别速度已优化")
    except Exception as e:
        print(f"⚠️ OCR服务初始化失败: {e}")
        print("   系统将继续运行，OCR将在首次使用时初始化")

    print("🎉 系统启动完成！")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
