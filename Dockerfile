FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[all]"

# 复制源码
COPY src/ src/
COPY workflows/ workflows/

# 创建必要目录
RUN mkdir -p /app/data/output /app/logs /app/models

EXPOSE 8000

CMD ["python", "-m", "omni_agent.main", "serve", "--host", "0.0.0.0", "--port", "8000"]