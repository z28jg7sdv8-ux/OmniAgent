"""
插件管理器 — MCP (Model Context Protocol) 插件系统

支持动态加载/卸载功能插件，扩展 OmniAgent 能力。
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any, Callable

from omni_agent.utils.config import Settings
from omni_agent.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Plugin:
    """插件描述"""
    name: str
    version: str
    description: str
    module_path: str
    enabled: bool = True
    capabilities: list[str] = field(default_factory=list)
    _instance: Any = None


class PluginManager:
    """插件管理器"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._plugins: dict[str, Plugin] = {}
        self._hooks: dict[str, list[Callable]] = {}

    def register(self, plugin: Plugin):
        """注册插件"""
        self._plugins[plugin.name] = plugin
        logger.info(f"插件注册: {plugin.name} v{plugin.version} ({plugin.description})")

    def unregister(self, name: str):
        """注销插件"""
        if name in self._plugins:
            del self._plugins[name]
            logger.info(f"插件注销: {name}")

    async def load(self, name: str) -> Any:
        """加载并初始化插件"""
        plugin = self._plugins.get(name)
        if not plugin:
            raise ValueError(f"插件未注册: {name}")

        if plugin._instance:
            return plugin._instance

        module = importlib.import_module(plugin.module_path)
        plugin._instance = module.Plugin(self.settings)
        await plugin._instance.on_load()

        logger.info(f"插件已加载: {name}")
        return plugin._instance

    async def unload(self, name: str):
        """卸载插件"""
        plugin = self._plugins.get(name)
        if plugin and plugin._instance:
            await plugin._instance.on_unload()
            plugin._instance = None
            logger.info(f"插件已卸载: {name}")

    def add_hook(self, event: str, callback: Callable):
        """注册钩子"""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    async def emit(self, event: str, **kwargs):
        """触发钩子"""
        for callback in self._hooks.get(event, []):
            try:
                result = callback(**kwargs)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"钩子执行失败: event={event}, error={e}")

    @property
    def list_plugins(self) -> list[Plugin]:
        return list(self._plugins.values())

    def get_by_capability(self, capability: str) -> list[Plugin]:
        """按能力查找插件"""
        return [p for p in self._plugins.values() if capability in p.capabilities and p.enabled]


# 导入 asyncio (add_hook/emit 中使用)
import asyncio
