"""
任务 DAG 引擎 — 支持依赖关系的有向无环图任务编排

用于编排复杂的多步骤工作流，如:
- 先生成图片 → 再生成配音 → 最后合成视频
- 先克隆声音 → 再训练数字人 → 最后驱动渲染
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TaskNode:
    """DAG 中的任务节点"""
    task_id: str
    action: str
    params: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    priority: int = 0


class TaskDAG:
    """任务有向无环图"""

    def __init__(self):
        self._nodes: dict[str, TaskNode] = {}
        self._edges: dict[str, list[str]] = {}  # task_id -> 依赖的 task_id 列表

    def add_node(self, node: TaskNode):
        """添加任务节点"""
        self._nodes[node.task_id] = node
        self._edges[node.task_id] = node.depends_on.copy()

    def remove_node(self, task_id: str):
        """移除任务节点"""
        self._nodes.pop(task_id, None)
        self._edges.pop(task_id, None)
        # 清理其他节点对此节点的依赖
        for deps in self._edges.values():
            if task_id in deps:
                deps.remove(task_id)

    def get_node(self, task_id: str) -> TaskNode | None:
        return self._nodes.get(task_id)

    def topological_levels(self) -> list[list[TaskNode]]:
        """
        按拓扑层级返回节点，同一层级的节点可以并行执行

        Returns:
            按层级分组的节点列表，层级0为无依赖的根节点
        """
        in_degree = {tid: len(deps) for tid, deps in self._edges.items()}
        # 反向边: 被依赖关系
        reverse_edges: dict[str, list[str]] = {tid: [] for tid in self._nodes}
        for tid, deps in self._edges.items():
            for dep in deps:
                if dep in reverse_edges:
                    reverse_edges[dep].append(tid)

        levels = []
        current_level = [tid for tid, deg in in_degree.items() if deg == 0]

        while current_level:
            level_nodes = [self._nodes[tid] for tid in current_level if tid in self._nodes]
            if level_nodes:
                levels.append(level_nodes)

            next_level = []
            for tid in current_level:
                for child in reverse_edges.get(tid, []):
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        next_level.append(child)

            current_level = next_level

        return levels

    def validate(self) -> bool:
        """验证 DAG 是否合法 (无环)"""
        visited = set()
        rec_stack = set()

        def _dfs(tid):
            visited.add(tid)
            rec_stack.add(tid)
            for dep in self._edges.get(tid, []):
                if dep not in visited:
                    if not _dfs(dep):
                        return False
                elif dep in rec_stack:
                    return False
            rec_stack.remove(tid)
            return True

        for tid in self._nodes:
            if tid not in visited:
                if not _dfs(tid):
                    return False
        return True

    @property
    def node_count(self) -> int:
        return len(self._nodes)
