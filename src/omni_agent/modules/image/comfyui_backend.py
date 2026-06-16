"""
ComfyUI 后端 — 通过 API 与 ComfyUI 交互

ComfyUI 是最强大的 Stable Diffusion 工作流引擎，
支持 Flux / SDXL / ControlNet / IP-Adapter 等全系列模型。
"""

from __future__ import annotations

import json
import uuid
from typing import Any

import httpx

from omni_agent.utils.config import Settings
from omni_agent.utils.logger import get_logger

logger = get_logger(__name__)


class ComfyUIBackend:
    """ComfyUI API 后端"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.comfyui_host or "http://localhost:8188"
        self.client_id = str(uuid.uuid4())

    async def _queue_prompt(self, workflow: dict) -> str:
        """提交工作流到 ComfyUI"""
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow, "client_id": self.client_id},
            )
            data = resp.json()
            return data["prompt_id"]

    async def _wait_for_result(self, prompt_id: str, timeout: int = 300) -> dict:
        """等待工作流执行完成"""
        import asyncio

        for _ in range(timeout // 2):
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/history/{prompt_id}")
                history = resp.json()
                if prompt_id in history:
                    return history[prompt_id]
            await asyncio.sleep(2)

        raise TimeoutError(f"ComfyUI 工作流超时: {prompt_id}")

    async def text2img(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        model: str = "flux",
        num_images: int = 1,
    ) -> dict[str, Any]:
        """文生图"""
        # 加载对应的工作流模板
        workflow = self._load_workflow(f"{model}_text2img")

        # 填充参数
        self._set_node_param(workflow, "KSampler", "seed", hash(prompt) % (2**32))
        self._set_node_param(workflow, "KSampler", "steps", 20)
        self._set_node_param(workflow, "CLIPTextEncode_pos", "text", prompt)
        self._set_node_param(workflow, "CLIPTextEncode_neg", "text", negative_prompt)
        self._set_node_param(workflow, "EmptyLatentImage", "width", width)
        self._set_node_param(workflow, "EmptyLatentImage", "height", height)
        self._set_node_param(workflow, "EmptyLatentImage", "batch_size", num_images)

        # 提交执行
        prompt_id = await self._queue_prompt(workflow)
        result = await self._wait_for_result(prompt_id)

        # 提取输出图片路径
        outputs = result.get("outputs", {})
        images = []
        for node_id, node_output in outputs.items():
            for img in node_output.get("images", []):
                images.append(f"{self.base_url}/view?filename={img['filename']}&subfolder={img.get('subfolder', '')}")

        return {
            "action": "text2img",
            "status": "completed",
            "images": images,
            "output_path": images[0] if images else None,
        }

    def _load_workflow(self, name: str) -> dict:
        """加载工作流模板"""
        from pathlib import Path
        workflow_dir = Path(self.settings.comfyui_workflow_dir or "./workflows/comfyui")
        workflow_file = workflow_dir / f"{name}.json"

        if workflow_file.exists():
            return json.loads(workflow_file.read_text(encoding="utf-8"))

        # 内置默认工作流
        return self._default_text2img_workflow()

    def _default_text2img_workflow(self) -> dict:
        """默认 Flux 文生图工作流"""
        return {
            "3": {"class_type": "KSampler", "inputs": {"seed": 0, "steps": 20, "cfg": 3.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["10", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
            "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
            "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["10", 1]}, "_meta": {"title": "CLIPTextEncode_pos"}},
            "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["10", 1]}, "_meta": {"title": "CLIPTextEncode_neg"}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["10", 2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "OmniAgent", "images": ["8", 0]}},
            "10": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "flux1-dev.safetensors"}},
        }

    def _set_node_param(self, workflow: dict, node_title: str, param: str, value: Any):
        """设置工作流节点参数"""
        for node_id, node in workflow.items():
            meta = node.get("_meta", {})
            class_type = node.get("class_type", "")
            if meta.get("title") == node_title or class_type == node_title:
                if param in node.get("inputs", {}):
                    node["inputs"][param] = value
                    return
