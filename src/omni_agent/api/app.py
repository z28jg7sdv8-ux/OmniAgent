"""
OmniAgent FastAPI 应用
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from omni_agent.utils.config import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    """创建 FastAPI 应用"""
    if settings is None:
        settings = Settings()

    app = FastAPI(
        title="OmniAgent",
        description="全能AI智能体 — 集图片、视频、配音、数字人于一体",
        version="0.1.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    from omni_agent.api.routes import image, video, voice, digital_human, task

    app.include_router(image.router, prefix="/api/v1/image", tags=["🎨 图片生成"])
    app.include_router(video.router, prefix="/api/v1/video", tags=["🎬 视频生成"])
    app.include_router(voice.router, prefix="/api/v1/voice", tags=["🔊 AI配音"])
    app.include_router(digital_human.router, prefix="/api/v1/digital-human", tags=["🧑 数字人"])
    app.include_router(task.router, prefix="/api/v1/task", tags=["📋 任务管理"])

    @app.get("/")
    async def root():
        return {
            "name": "OmniAgent",
            "version": "0.1.0",
            "description": "全能AI智能体",
            "docs": "/docs",
        }

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
