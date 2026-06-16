"""
OmniAgent — 全能AI智能体
集图片生成、视频创作、AI配音、数字人于一体
"""

__version__ = "0.1.0"

from omni_agent.core.orchestrator import Orchestrator
from omni_agent.core.llm_router import LLMRouter
from omni_agent.core.plugin_manager import PluginManager

__all__ = ["Orchestrator", "LLMRouter", "PluginManager"]
