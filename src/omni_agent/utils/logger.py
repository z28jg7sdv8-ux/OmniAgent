"""
日志配置
"""

from loguru import logger
import sys


def setup_logger(level: str = "INFO"):
    """配置 loguru 日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.add(
        "logs/omni_agent_{time:YYYY-MM-DD}.log",
        rotation="1 day",
        retention="30 days",
        level="DEBUG",
    )


def get_logger(name: str = __name__):
    return logger.bind(name=name)
