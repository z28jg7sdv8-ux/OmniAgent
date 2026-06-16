# 🤖 OmniAgent — 全能AI智能体

> 集图片生成、视频创作、AI配音、数字人于一体的开源AI智能体平台

## 🌟 项目愿景

OmniAgent 旨在打造一个**一站式AI内容创作智能体**，整合当前市场最顶级的开源AI项目，让用户通过自然语言即可完成从创意到成品的全部流程。

```
用户指令 → OmniAgent Orchestrator → 图片/视频/音频/数字人 多模块协作 → 成品输出
```

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    OmniAgent Gateway                     │
│              (FastAPI + WebSocket + REST)                │
├─────────────────────────────────────────────────────────┤
│                   Orchestrator Core                      │
│            (LLM Agent + Task DAG Engine)                 │
├──────────┬──────────┬──────────┬──────────┬─────────────┤
│  🎨 Image │  🎬 Video │  🔊 Voice │  🧑 Digital │  🧠 LLM   │
│  Module   │  Module   │  Module   │  Human     │  Router    │
├──────────┼──────────┼──────────┼──────────┼─────────────┤
│ ComfyUI  │ MoneyPrin │ CosyVoice │ LiveTalking│ Qwen3     │
│ Flux     │ terTurbo  │ GPT-SoVITS│ Duix-Avatar│ DeepSeek  │
│ SDXL     │ ViMax     │ FishSpeech│ HeyGen    │ GPT-4o    │
│ GPT-Img2 │ Seedance2 │ ChatTTS   │ MuseTalk  │ Claude    │
└──────────┴──────────┴──────────┴──────────┴─────────────┘
│                  Plugin & MCP Layer                      │
├─────────────────────────────────────────────────────────┤
│              Storage / Queue / Monitoring                │
└─────────────────────────────────────────────────────────┘
```

## 📦 核心模块

### 🎨 图片生成模块 (Image Module)
基于 [ComfyUI](https://github.com/comfyanonymous/ComfyUI) + 多模型后端

| 功能 | 底层项目 | 说明 |
|------|---------|------|
| 文生图 | Flux / SDXL / GPT-Image-2 | 多模型切换 |
| 图生图 | ControlNet + IP-Adapter | 风格迁移、条件控制 |
| 图片编辑 | Inpainting / Outpainting | 局部重绘、扩展 |
| 批量生成 | ComfyUI Workflow | DAG流水线编排 |

### 🎬 视频生成模块 (Video Module)
基于 [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) + [ViMax](https://github.com/HKUDS/ViMax)

| 功能 | 底层项目 | 说明 |
|------|---------|------|
| 文生视频 | Seedance 2 / Kling / Sora | AI视频生成 |
| 图生视频 | Seedance2 I2V / Runway | 图片转视频 |
| 短视频自动生产 | MoneyPrinterTurbo | 一键生成短视频 |
| 电影级编排 | ViMax | Agent式视频导演 |
| 视频剪辑 | FFmpeg + Timeline Studio | 自动剪辑合成 |

### 🔊 AI配音模块 (Voice Module)
基于 [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) + [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS)

| 功能 | 底层项目 | 说明 |
|------|---------|------|
| 文字转语音 | CosyVoice / FishSpeech | 多语言高质量TTS |
| 语音克隆 | GPT-SoVITS / OpenVoice | 1分钟数据克隆 |
| 实时语音合成 | ChatTTS | 对话式语音 |
| 语音情感控制 | CosyVoice | 情感/语速/风格调节 |

### 🧑 数字人模块 (Digital Human Module)
基于 [LiveTalking](https://github.com/lipku/LiveTalking) + [Duix-Avatar](https://github.com/duixcom/Duix-Avatar)

| 功能 | 底层项目 | 说明 |
|------|---------|------|
| 实时数字人 | LiveTalking | <1.5s延迟实时交互 |
| 数字人克隆 | Duix-Avatar | 离线视频数字人生成 |
| 语音驱动 | MuseTalk / SadTalker | 音频驱动面部动画 |
| 多形象支持 | 自定义形象 | 上传照片生成数字人 |

### 🧠 LLM Router (智能调度)
多模型路由，根据任务类型自动选择最优模型

| 用途 | 模型 | 说明 |
|------|------|------|
| 通用对话 | Qwen3 / DeepSeek | 国产大模型 |
| 复杂推理 | Claude / GPT-4o | 顶级推理能力 |
| 代码生成 | DeepSeek-Coder | 代码专精 |
| 多模态理解 | GPT-4o / Qwen-VL | 图片/视频理解 |

## 🚀 快速开始

### 环境要求
- Python 3.10+
- CUDA 12.0+ (GPU推理)
- Docker & Docker Compose
- 8GB+ VRAM (最低), 24GB+ VRAM (推荐)

### Docker 一键部署

```bash
# 克隆项目
git clone https://github.com/your-username/OmniAgent.git
cd OmniAgent

# 复制配置文件
cp .env.example .env

# 启动所有服务
docker compose up -d
```

### 开发模式

```bash
# 安装依赖
pip install -e ".[dev]"

# 启动API服务
python -m omni_agent.main --dev

# 启动前端
cd web && npm install && npm run dev
```

## 📁 项目结构

```
OmniAgent/
├── README.md                    # 项目说明
├── docker-compose.yml           # 容器编排
├── pyproject.toml               # Python项目配置
├── .env.example                 # 环境变量模板
├── docs/                        # 文档
│   ├── architecture.md          # 架构设计
│   ├── deployment.md            # 部署指南
│   └── api-reference.md         # API文档
├── src/
│   └── omni_agent/
│       ├── __init__.py
│       ├── main.py              # 入口
│       ├── core/
│       │   ├── orchestrator.py  # 任务编排器
│       │   ├── llm_router.py    # LLM路由
│       │   ├── task_dag.py      # 任务DAG引擎
│       │   └── plugin_manager.py # 插件管理
│       ├── modules/
│       │   ├── image/           # 图片模块
│       │   │   ├── engine.py
│       │   │   ├── comfyui_backend.py
│       │   │   └── workflows/
│       │   ├── video/           # 视频模块
│       │   │   ├── engine.py
│       │   │   ├── money_printer.py
│       │   │   └── vimax_backend.py
│       │   ├── voice/           # 配音模块
│       │   │   ├── engine.py
│       │   │   ├── cosyvoice_backend.py
│       │   │   └── sovits_backend.py
│       │   └── digital_human/   # 数字人模块
│       │       ├── engine.py
│       │       ├── livetalking_backend.py
│       │       └── duix_backend.py
│       ├── api/
│       │   ├── routes/          # API路由
│       │   ├── middleware/      # 中间件
│       │   └── websocket.py    # WebSocket
│       └── utils/
│           ├── config.py
│           ├── logger.py
│           └── storage.py
├── plugins/                     # MCP插件
├── workflows/                   # 预设工作流
├── web/                         # 前端界面
│   ├── package.json
│   └── src/
├── tests/                       # 测试
└── scripts/                     # 部署脚本
```

## 🔗 整合的开源项目

| 项目 | 用途 | Stars |
|------|------|-------|
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | 图片生成工作流引擎 | 75k+ |
| [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) | AI短视频一键生成 | 88k+ |
| [CosyVoice](https://github.com/FunAudioLLM/CosyVoice) | 多语言语音生成 | 30k+ |
| [GPT-SoVITS](https://github.com/RVC-Boss/GPT-SoVITS) | 少样本语音克隆 | 45k+ |
| [FishSpeech](https://github.com/fishaudio/fish-speech) | SOTA开源TTS | 20k+ |
| [ChatTTS](https://github.com/2noise/ChatTTS) | 对话式语音合成 | 35k+ |
| [LiveTalking](https://github.com/lipku/LiveTalking) | 实时交互数字人 | 10k+ |
| [Duix-Avatar](https://github.com/duixcom/Duix-Avatar) | 数字人克隆 | 5k+ |
| [ViMax](https://github.com/HKUDS/ViMax) | Agent式视频生成 | 10k+ |
| [OpenVoice](https://github.com/myshell-ai/OpenVoice) | 即时语音克隆 | 30k+ |
| [LocalAI](https://github.com/mudler/LocalAI) | 本地AI引擎 | 30k+ |

## 📜 License

MIT License

## 🤝 参与贡献

欢迎提交 Issue 和 PR！请阅读 [贡献指南](CONTRIBUTING.md)。
