"""图片生成 API"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/text2img")
async def text2img(prompt: str, model: str = "flux", width: int = 1024, height: int = 1024):
    """文生图"""
    from omni_agent.core.orchestrator import Orchestrator, TaskMode
    from omni_agent.utils.config import Settings
    orch = Orchestrator(Settings())
    result = await orch.execute(f"生成图片: {prompt}", mode="image")
    return result.output

@router.post("/img2img")
async def img2img(prompt: str, image_url: str, strength: float = 0.7):
    """图生图"""
    return {"status": "ok", "action": "img2img"}

@router.post("/upscale")
async def upscale(image_url: str, scale: int = 2):
    """超分辨率"""
    return {"status": "ok", "action": "upscale"}
