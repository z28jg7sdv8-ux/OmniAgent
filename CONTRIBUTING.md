# Contributing to OmniAgent

感谢你对 OmniAgent 的贡献兴趣！

## 如何贡献

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交修改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 开发规范

- Python 代码遵循 PEP 8 (使用 ruff 检查)
- 提交前运行测试: `pytest`
- 新功能需要添加对应测试
- API 变化需要更新文档

## 添加新模块

OmniAgent 采用模块化架构，添加新功能模块的步骤：

1. 在 `src/omni_agent/modules/` 下创建新目录
2. 实现 `Engine` 类，提供 `execute(action, params)` 接口
3. 在 `orchestrator.py` 中注册新模块
4. 添加对应 API 路由
5. 更新 `docker-compose.yml` (如需要独立服务)
6. 编写测试和文档

## 报告问题

请使用 GitHub Issues，包含：
- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息 (Python 版本, OS, GPU 等)