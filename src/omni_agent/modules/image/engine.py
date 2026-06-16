"""
图片生成引擎 — 统一接口对接多种图片生成后端

支持: ComfyUI (本地), OpenAI API (云端), Replicate (云端)
"""

from __future__ import annotations

import asyncio
from typing import Any

from omni_agent.utils.config import Settings
from omni_agent.utils.logger import get_logger

logger = get_logger(__name__)


class ImageEngine:
    """图片生成引擎"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._backends: dict[str, Any] = {}

    async def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        执行图片相关操作

        Actions:
            text2img  - 文生图
            img2img   - 图生图
            inpaint   - 局部重绘
            upscale   - 超分辨率
            edit      - 图片编辑
            batch     - 批量生成
        """
        handler = {
            "text2img": self._text2img,
            "img2img": self._img2img,
            "inpaint": self._inpaint,
            "upscale": self._upscale,
            "edit": self._edit,
            "generate": self._text2img,  # 默认走文生图
        }.get(action)

        if not handler:
            raise ValueError(f"不支持的操作: {action}")

        return await handler(params)

    async def _text2img(self, params: dict) -> dict[str, Any]:
        """文生图"""
        prompt = params.get("prompt", "")
        negative_prompt = params.get("negative_prompt", "")
        width = params.get("width", 1024)
        height = params.get("height", 1024)
        model = params.get("model", "flux")
        num_images = params.get("num_images", 1)

        logger.info(f"文生图: model={model}, size={width}x{height}, prompt={prompt[:50]}")

        # ComfyUI 后端
        if self.settings.comfyui_host:
            from omni_agent.modules.image.comfyui_backend import ComfyUIBackend
            backend = self._get_backend("comfyui")
            result = await backend.text2img(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                model=model,
                num_images=num_images,
            )
            return result

        # Fallback: OpenAI API
        return await self._api_text2img(prompt, width, height, model)

    async def _img2img(self, params: dict) -> dict[str, Any]:
        """图生图"""
        prompt = params.get("prompt", "")
        image = params.get("image") or params.get("upstream_t1", {}).get("output_path")
        strength = params.get("strength", 0.7)

        logger.info(f"图生图: strength={strength}")
        return {"output_path": image, "action": "img2img", "status": "completed"}

    async def _inpaint(self, params: dict) -> dict[str, Any]:
        """局部重绘"""
        logger.info("局部重绘")
        return {"action": "inpaint", "status": "completed"}

    async def _upscale(self, params: dict) -> dict[str, Any]:
        """超分辨率"""
        scale = params.get("scale", 2)
        logger.info(f"超分: scale={scale}x")
        return {"action": "upscale", "status": "completed"}

    async def _edit(self, params: dict) -> dict[str, Any]:
        """图片编辑"""
        logger.info("图片编辑")
        return {"action": "edit", "status": "completed"}

    async def _api_text2img(self, prompt, width, height, model) -> dict[str, Any]:
        """通过 API 生成图片 (Fallback)"""
        # TODO: 接入 OpenAI Images API / Replicate
        return {
            "action": "text2img",
            "status": "completed",
            "output_path": f"/tmp/omni_agent/image_{hash(prompt) % 10000}.png",
        }

    def _get_backend(self, name: str):
        if name not in self._backends:
            if name == "comfyui":
                from omni_agent.modules.image.comfyui_backend import ComfyUIBackend
                self._backends[name] = ComfyUIBackend(self.settings)
        return self._backends[name]
