"""
任务编排器 — OmniAgent 的核心大脑

接收用户自然语言指令，解析任务意图，调度各模块协同完成。
支持 DAG 依赖编排，实现复杂多步骤工作流。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from omni_agent.core.llm_router import LLMRouter
from omni_agent.core.task_dag import TaskDAG, TaskNode
from omni_agent.utils.config import Settings
from omni_agent.utils.logger import get_logger

logger = get_logger(__name__)


class TaskMode(str, Enum):
    AUTO = "auto"
    IMAGE = "image"
    VIDEO = "video"
    VOICE = "voice"
    DIGITAL_HUMAN = "digital_human"


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskResult:
    """任务执行结果"""
    task_id: str
    status: TaskStatus
    mode: TaskMode
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    artifacts: list[str] = field(default_factory=list)


class Orchestrator:
    """
    OmniAgent 任务编排器

    工作流程:
    1. 接收用户自然语言指令
    2. LLM 分析意图，拆解为子任务 DAG
    3. 按 DAG 拓扑序执行子任务
    4. 各模块并行/串行协作
    5. 汇总结果返回
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_router = LLMRouter(settings)
        self._modules: dict[TaskMode, Any] = {}
        self._init_modules()

    def _init_modules(self):
        """延迟加载各功能模块"""
        # 模块将在实际需要时初始化，避免启动时加载所有 GPU 模型
        self._module_classes = {
            TaskMode.IMAGE: "omni_agent.modules.image.engine.ImageEngine",
            TaskMode.VIDEO: "omni_agent.modules.video.engine.VideoEngine",
            TaskMode.VOICE: "omni_agent.modules.voice.engine.VoiceEngine",
            TaskMode.DIGITAL_HUMAN: "omni_agent.modules.digital_human.engine.DigitalHumanEngine",
        }

    async def _get_module(self, mode: TaskMode) -> Any:
        """按需加载模块"""
        if mode not in self._modules:
            class_path = self._module_classes.get(mode)
            if not class_path:
                raise ValueError(f"未知的任务模式: {mode}")

            module_path, class_name = class_path.rsplit(".", 1)
            import importlib
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            self._modules[mode] = cls(self.settings)
            logger.info(f"模块已加载: {mode.value}")

        return self._modules[mode]

    async def execute(self, prompt: str, mode: str = "auto") -> TaskResult:
        """
        执行用户任务

        Args:
            prompt: 用户自然语言指令
            mode: 执行模式，auto 为自动识别

        Returns:
            TaskResult: 任务执行结果
        """
        task_mode = TaskMode(mode)

        # 自动模式: LLM 分析意图
        if task_mode == TaskMode.AUTO:
            task_mode = await self._analyze_intent(prompt)
            logger.info(f"意图识别结果: {task_mode.value}")

        logger.info(f"开始执行任务: mode={task_mode.value}, prompt={prompt[:100]}")

        try:
            # 1. LLM 规划子任务
            sub_tasks = await self._plan_tasks(prompt, task_mode)

            # 2. 构建 DAG
            dag = self._build_dag(sub_tasks)

            # 3. 执行 DAG
            result = await self._execute_dag(dag, task_mode)

            return TaskResult(
                task_id=f"task_{id(dag)}",
                status=TaskStatus.COMPLETED,
                mode=task_mode,
                output=result,
                artifacts=[v.get("output_path") for v in result.values() if v.get("output_path")],
            )
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            return TaskResult(
                task_id="error",
                status=TaskStatus.FAILED,
                mode=task_mode,
                error=str(e),
            )

    async def _analyze_intent(self, prompt: str) -> TaskMode:
        """使用 LLM 分析用户意图"""
        system_prompt = """你是一个任务意图分析器。根据用户的输入，判断应该使用哪个模块处理:

- image: 图片生成/编辑/处理相关
- video: 视频生成/剪辑/合成相关
- voice: 语音合成/配音/克隆相关
- digital_human: 数字人/虚拟人/虚拟主播相关

只返回模块名称，不要其他内容。如果涉及多个模块，用逗号分隔。"""

        response = await self.llm_router.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            model_preference="fast",
        )

        primary = response.strip().split(",")[0].strip()
        try:
            return TaskMode(primary)
        except ValueError:
            return TaskMode.IMAGE  # 默认图片模式

    async def _plan_tasks(self, prompt: str, mode: TaskMode) -> list[dict]:
        """使用 LLM 规划子任务"""
        system_prompt = f"""你是一个任务规划器。将用户指令拆解为可执行的子任务列表。

当前模式: {mode.value}
可用操作:"""

        operations = {
            TaskMode.IMAGE: "text2img(文生图), img2img(图生图), inpaint(局部重绘), upscale(超分), edit(编辑)",
            TaskMode.VIDEO: "text2video(文生视频), img2video(图生视频), concat(拼接), subtitle(字幕), bgm(配乐)",
            TaskMode.VOICE: "tts(文字转语音), clone(语音克隆), mix(混音), adjust(参数调整)",
            TaskMode.DIGITAL_HUMAN: "create(创建数字人), animate(驱动动画), interact(实时交互), render(渲染输出)",
        }

        system_prompt += f"\n{operations.get(mode, '')}"
        system_prompt += "\n\n返回 JSON 数组，每个元素包含: id, action, params, depends_on(依赖的task id列表)"

        response = await self.llm_router.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            model_preference="smart",
        )

        import json
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            # 简单回退: 单一任务
            return [{"id": "t1", "action": "generate", "params": {"prompt": prompt}, "depends_on": []}]

    def _build_dag(self, sub_tasks: list[dict]) -> TaskDAG:
        """构建任务 DAG"""
        dag = TaskDAG()
        for task in sub_tasks:
            node = TaskNode(
                task_id=task["id"],
                action=task["action"],
                params=task.get("params", {}),
                depends_on=task.get("depends_on", []),
            )
            dag.add_node(node)
        return dag

    async def _execute_dag(self, dag: TaskDAG, mode: TaskMode) -> dict:
        """按 DAG 拓扑序执行任务"""
        module = await self._get_module(mode)
        results = {}

        for level in dag.topological_levels():
            # 同一层级的任务可以并行执行
            tasks = []
            for node in level:
                # 注入上游结果作为参数
                enriched_params = {**node.params}
                for dep_id in node.depends_on:
                    if dep_id in results:
                        enriched_params[f"upstream_{dep_id}"] = results[dep_id]

                tasks.append(module.execute(node.action, enriched_params))

            level_results = await asyncio.gather(*tasks, return_exceptions=True)
            for node, result in zip(level, level_results):
                if isinstance(result, Exception):
                    logger.error(f"子任务 {node.task_id} 失败: {result}")
                    results[node.task_id] = {"error": str(result)}
                else:
                    results[node.task_id] = result

        return results
