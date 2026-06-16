"""任务管理 API"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TaskRequest(BaseModel):
    prompt: str
    mode: str = "auto"

@router.post("/execute")
async def execute_task(req: TaskRequest):
    """执行任务"""
    from omni_agent.core.orchestrator import Orchestrator
    from omni_agent.utils.config import Settings
    orch = Orchestrator(Settings())
    result = await orch.execute(req.prompt, mode=req.mode)
    return {
        "task_id": result.task_id,
        "status": result.status.value,
        "mode": result.mode.value,
        "output": result.output,
        "artifacts": result.artifacts,
    }

@router.get("/status/{task_id}")
async def task_status(task_id: str):
    """查询任务状态"""
    return {"task_id": task_id, "status": "completed"}
