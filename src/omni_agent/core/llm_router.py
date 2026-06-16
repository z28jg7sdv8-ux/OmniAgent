"""
LLM 路由器 — 多模型智能调度

根据任务类型、成本、延迟自动选择最优模型。
支持 OpenAI / Anthropic / DeepSeek / Qwen 等多家 API。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from omni_agent.utils.config import Settings
from omni_agent.utils.logger import get_logger

logger = get_logger(__name__)


class ModelProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    QWEN = "qwen"


@dataclass
class ModelConfig:
    provider: ModelProvider
    model: str
    max_tokens: int
    supports_vision: bool = False
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


# 预定义模型配置
MODEL_REGISTRY: dict[str, ModelConfig] = {
    # 快速模型 (意图分析、简单任务)
    "fast": ModelConfig(
        provider=ModelProvider.DEEPSEEK,
        model="deepseek-chat",
        max_tokens=4096,
        cost_per_1k_input=0.001,
        cost_per_1k_output=0.002,
    ),
    # 智能模型 (复杂推理、任务规划)
    "smart": ModelConfig(
        provider=ModelProvider.ANTHROPIC,
        model="claude-sonnet-4-20250514",
        max_tokens=8192,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
    # 多模态模型 (图片/视频理解)
    "vision": ModelConfig(
        provider=ModelProvider.OPENAI,
        model="gpt-4o",
        max_tokens=4096,
        supports_vision=True,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
    ),
    # 创意模型 (提示词生成、文案)
    "creative": ModelConfig(
        provider=ModelProvider.QWEN,
        model="qwen-max",
        max_tokens=8192,
        cost_per_1k_input=0.002,
        cost_per_1k_output=0.006,
    ),
}


class LLMRouter:
    """LLM 多模型路由器"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._clients: dict[ModelProvider, Any] = {}

    def _get_client(self, provider: ModelProvider):
        """获取对应 provider 的 API client"""
        if provider not in self._clients:
            from openai import AsyncOpenAI

            if provider == ModelProvider.OPENAI:
                self._clients[provider] = AsyncOpenAI(
                    api_key=self.settings.openai_api_key,
                    base_url=self.settings.openai_base_url,
                )
            elif provider == ModelProvider.DEEPSEEK:
                self._clients[provider] = AsyncOpenAI(
                    api_key=self.settings.deepseek_api_key,
                    base_url=self.settings.deepseek_base_url,
                )
            elif provider == ModelProvider.QWEN:
                self._clients[provider] = AsyncOpenAI(
                    api_key=self.settings.dashscope_api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                )
            elif provider == ModelProvider.ANTHROPIC:
                import anthropic
                self._clients[provider] = anthropic.AsyncAnthropic(
                    api_key=self.settings.anthropic_api_key,
                )

        return self._clients[provider]

    async def chat(
        self,
        messages: list[dict],
        model_preference: str = "fast",
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> str:
        """
        发送聊天请求

        Args:
            messages: OpenAI 格式消息列表
            model_preference: 模型偏好 (fast/smart/vision/creative)
            temperature: 温度参数
            max_tokens: 最大 token 数

        Returns:
            模型回复文本
        """
        config = MODEL_REGISTRY.get(model_preference, MODEL_REGISTRY["fast"])
        client = self._get_client(config.provider)

        logger.debug(f"LLM 路由: preference={model_preference}, provider={config.provider.value}, model={config.model}")

        if config.provider == ModelProvider.ANTHROPIC:
            # Anthropic SDK 格式
            system_msg = None
            chat_msgs = []
            for m in messages:
                if m["role"] == "system":
                    system_msg = m["content"]
                else:
                    chat_msgs.append(m)

            response = await client.messages.create(
                model=config.model,
                max_tokens=max_tokens or config.max_tokens,
                temperature=temperature,
                system=system_msg or "",
                messages=chat_msgs,
            )
            return response.content[0].text
        else:
            # OpenAI 兼容格式
            response = await client.chat.completions.create(
                model=config.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or config.max_tokens,
            )
            return response.choices[0].message.content

    async def chat_with_vision(
        self,
        messages: list[dict],
        images: list[str],
        model_preference: str = "vision",
    ) -> str:
        """多模态聊天 (带图片)"""
        config = MODEL_REGISTRY.get(model_preference, MODEL_REGISTRY["vision"])
        if not config.supports_vision:
            config = MODEL_REGISTRY["vision"]

        # 构建多模态消息
        content = []
        for msg in messages:
            if msg["role"] == "user":
                content.append({"type": "text", "text": msg["content"]})
                for img_url in images:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": img_url},
                    })
            else:
                content.append({"type": "text", "text": msg["content"]})

        client = self._get_client(config.provider)
        response = await client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": content}],
            max_tokens=config.max_tokens,
        )
        return response.choices[0].message.content
