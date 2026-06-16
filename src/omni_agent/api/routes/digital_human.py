"""数字人 API"""
from fastapi import APIRouter

router = APIRouter()

@router.post("/create")
async def create_avatar(image_url: str, name: str = "default"):
    """创建数字人"""
    return {"status": "ok", "action": "create"}

@router.post("/animate")
async def animate(avatar_id: str, audio_url: str):
    """音频驱动动画"""
    return {"status": "ok", "action": "animate"}

@router.websocket("/ws/interact/{avatar_id}")
async def interact_ws(websocket, avatar_id: str):
    """实时交互 WebSocket"""
    await websocket.accept()
    await websocket.send_json({"status": "connected", "avatar_id": avatar_id})
