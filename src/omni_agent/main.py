"""
OmniAgent 主入口
"""

import asyncio
import click
from omni_agent.api.app import create_app
from omni_agent.utils.config import Settings
from omni_agent.utils.logger import setup_logger


@click.group()
@click.option("--env", default="development", help="运行环境")
@click.pass_context
def cli(ctx, env):
    """OmniAgent — 全能AI智能体"""
    ctx.ensure_object(dict)
    ctx.obj["env"] = env
    settings = Settings(env=env)
    ctx.obj["settings"] = settings
    setup_logger(settings.log_level)


@cli.command()
@click.option("--host", default="0.0.0.0", help="监听地址")
@click.option("--port", default=8000, type=int, help="监听端口")
@click.option("--reload", is_flag=True, help="开发模式热重载")
@click.pass_context
def serve(ctx, host, port, reload):
    """启动 API 服务"""
    settings = ctx.obj["settings"]
    app = create_app(settings)

    import uvicorn

    uvicorn.run(
        "omni_agent.api.app:create_app",
        host=host,
        port=port,
        reload=reload,
        factory=True,
    )


@cli.command()
@click.argument("prompt")
@click.option("--mode", default="auto", help="执行模式: auto|image|video|voice|digital_human")
@click.pass_context
def run(ctx, prompt, mode):
    """执行单次任务"""
    from omni_agent.core.orchestrator import Orchestrator

    settings = ctx.obj["settings"]
    orchestrator = Orchestrator(settings)

    result = asyncio.run(orchestrator.execute(prompt, mode=mode))
    click.echo(f"✅ 任务完成: {result}")


@cli.command()
@click.pass_context
def status(ctx):
    """查看系统状态"""
    click.echo("🤖 OmniAgent Status")
    click.echo(f"  Version: 0.1.0")
    click.echo(f"  Environment: {ctx.obj['env']}")


if __name__ == "__main__":
    cli()
