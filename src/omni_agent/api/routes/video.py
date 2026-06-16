"""视频生成 API"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/text2video")
async def text2video(prompt: str, duration: int = 5, model: str = "seedance2"):
    """文生视频"""
    return {"status": "ok", "action": "text2video"}

@router.post("/auto-short")
async def auto_short(topic: str, voice_name: str = "default"):
    """自动生成短视频"""
    return {"status": "ok", "action": "auto_short"}
