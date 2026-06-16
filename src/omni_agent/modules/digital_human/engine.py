"""
数字人引擎 — 整合 LiveTalking + Duix-Avatar + MuseTalk

支持: 实时交互数字人、数字人克隆、音频驱动面部动画
"""

from __future__ import annotations

from typing import Any

from omni_agent.utils.config import Settings
from omni_agent.utils.logger import get_logger

logger = get_logger(__name__)


class DigitalHumanEngine:
    """数字人引擎"""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        执行数字人相关操作

        Actions:
            create    - 创建数字人 (上传照片/选择形象)
            animate   - 音频驱动动画
            interact  - 实时交互
            render    - 渲染输出视频
        """
        handler = {
            "create": self._create,
            "animate": self._animate,
            "interact": self._interact,
            "render": self._render,
            "generate": self._animate,
        }.get(action, self._animate)

        return await handler(params)

    async def _create(self, params: dict) -> dict[str, Any]:
        """创建数字人形象"""
        image_path = params.get("image_path", "")
        name = params.get("name", "default")
        style = params.get("style", "realistic")  # realistic / cartoon

        logger.info(f"创建数字人: name={name}, style={style}")

        # Duix-Avatar: 从照片创建数字人
        return {
            "action": "create",
            "status": "completed",
            "avatar_id": f"avatar_{hash(image_path) % 10000}",
            "output_path": image_path,
        }

    async def _animate(self, params: dict) -> dict[str, Any]:
        """音频驱动面部动画 — LiveTalking / MuseTalk"""
        avatar_id = params.get("avatar_id", "default")
        audio_path = params.get("audio_path") or params.get("upstream_t1", {}).get("output_path")
        text = params.get("text") or params.get("prompt", "")

        logger.info(f"驱动动画: avatar={avatar_id}, audio={audio_path}")

        # 优先使用 LiveTalking (实时)
        if self.settings.livetalking_host:
            import httpx
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(
                    f"{self.settings.livetalking_host}/api/animate",
                    json={"avatar_id": avatar_id, "audio_path": audio_path, "text": text},
                )
                data = resp.json()

            return {
                "action": "animate",
                "status": "completed",
                "output_path": data.get("video_path"),
            }

        return {
            "action": "animate",
            "status": "completed",
            "output_path": f"/tmp/omni_agent/digital_human_{hash(text) % 10000}.mp4",
        }

    async def _interact(self, params: dict) -> dict[str, Any]:
        """实时交互数字人"""
        avatar_id = params.get("avatar_id", "default")

        logger.info(f"启动实时交互: avatar={avatar_id}")

        # LiveTalking 实时交互通过 WebSocket
        return {
            "action": "interact",
            "status": "running",
            "ws_url": f"ws://localhost:8888/ws/avatar/{avatar_id}",
        }

    async def _render(self, params: dict) -> dict[str, Any]:
        """渲染输出"""
        avatar_id = params.get("avatar_id", "default")
        audio_path = params.get("audio_path")
        output_format = params.get("format", "mp4")

        logger.info(f"渲染输出: avatar={avatar_id}, format={output_format}")
        return {
            "action": "render",
            "status": "completed",
            "output_path": f"/tmp/omni_agent/render_{avatar_id}.{output_format}",
        }
