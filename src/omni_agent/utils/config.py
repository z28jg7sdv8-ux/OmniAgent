"""
配置管理
"""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """全局配置 — 从环境变量 / .env 文件加载"""

    # 通用
    app_env: str = Field(default="development", alias="APP_ENV")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # LLM
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(default="https://api.deepseek.com/v1", alias="DEEPSEEK_BASE_URL")
    dashscope_api_key: str = Field(default="", alias="DASHSCOPE_API_KEY")
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    # 图片
    comfyui_host: str = Field(default="", alias="COMFYUI_HOST")
    comfyui_workflow_dir: str = Field(default="", alias="COMFYUI_WORKFLOW_DIR")

    # 视频
    money_printer_url: str = Field(default="http://localhost:8501", alias="MONEY_PRINTER_URL")

    # 语音
    cosyvoice_model_dir: str = Field(default="./models/cosyvoice", alias="COSYVOICE_MODEL_DIR")
    cosyvoice_device: str = Field(default="cuda:0", alias="COSYVOICE_DEVICE")
    sovits_model_dir: str = Field(default="./models/sovits", alias="SOVITS_MODEL_DIR")
    fishspeech_api_url: str = Field(default="http://localhost:8080", alias="FISHSPEECH_API_URL")

    # 数字人
    livetalking_host: str = Field(default="", alias="LIVETALKING_HOST")
    livetalking_model_dir: str = Field(default="./models/livetalking", alias="LIVETALKING_MODEL_DIR")

    # 存储
    storage_type: str = Field(default="local", alias="STORAGE_TYPE")
    storage_path: str = Field(default="./data/output", alias="STORAGE_PATH")

    # 基础设施
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    database_url: str = Field(default="postgresql://omniagent:password@localhost:5432/omniagent", alias="DATABASE_URL")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}
