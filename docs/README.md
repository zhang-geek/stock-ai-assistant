# 📚 A股AI助手 - 文档中心

> 完整的项目文档，涵盖开发、部署、使用指南等所有方面

[![GitHub](https://img.shields.io/badge/GitHub-stock--ai--assistant-blue?logo=github)](https://github.com/zhang-geek/stock-ai-assistant)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://reactjs.org/)

---

## 📖 文档导航

### 🚀 快速开始

| 文档 | 描述 | 适合人群 |
|------|------|---------|
| [快速启动指南](guides/STARTUP.md) | 5分钟快速启动项目 | 新用户 |
| [CLAUDE.md](../CLAUDE.md) | Claude Code 开发指南 | 开发者 |

### 👨‍💻 开发文档

| 文档 | 描述 | 内容 |
|------|------|------|
| [开发指南](development/DEVELOPMENT.md) | 完整的开发文档 | 架构、模块、开发规范 |
| [实现总结](development/IMPLEMENTATION_SUMMARY.md) | 已完成功能总结 | Phase 0-3 实现细节 |
| [Agency Agents 指南](guides/AGENCY_AGENTS_GUIDE.md) | AI 专家团队使用指南 | 50+ AI agents 使用方法 |

### 🚢 部署文档

| 文档 | 描述 | 方案 |
|------|------|------|
| [部署指南](deployment/DEPLOYMENT.md) | 远程访问和部署 | Cloudflare Tunnel, Docker, Vercel |
| [远程开发](deployment/REMOTE_DEV.md) | Claude 自动化开发 | GitHub Actions, Telegram Bot |

### 📋 参考文档

| 文档 | 描述 |
|------|------|
| [API 文档](reference/API.md) | FastAPI 接口文档 |
| [前端组件](reference/COMPONENTS.md) | React 组件库 |
| [数据库模型](reference/DATABASE.md) | SQLAlchemy ORM 模型 |

---

## 🗂️ 文档结构

```
docs/
├── guides/                    # 使用指南
│   ├── STARTUP.md            # 快速启动
│   └── AGENCY_AGENTS_GUIDE.md # AI Agents 使用
│
├── development/              # 开发文档
│   ├── DEVELOPMENT.md        # 开发指南
│   └── IMPLEMENTATION_SUMMARY.md # 实现总结
│
├── deployment/               # 部署文档
│   ├── DEPLOYMENT.md         # 部署指南
│   └── REMOTE_DEV.md         # 远程开发
│
└── reference/                # 参考文档
    ├── API.md                # API 参考
    ├── COMPONENTS.md         # 组件参考
    └── DATABASE.md           # 数据库参考
```

---

## 🎯 按场景查找文档

### 场景 1：我是新用户，想快速体验

1. 阅读 [快速启动指南](guides/STARTUP.md)
2. 按照步骤启动项目
3. 访问 http://localhost:5173

### 场景 2：我想参与开发

1. 阅读 [CLAUDE.md](../CLAUDE.md) 了解项目结构
2. 阅读 [开发指南](development/DEVELOPMENT.md) 了解开发规范
3. 查看 [实现总结](development/IMPLEMENTATION_SUMMARY.md) 了解已完成功能

### 场景 3：我想部署到服务器

1. 阅读 [部署指南](deployment/DEPLOYMENT.md)
2. 选择合适的部署方案
3. 按照步骤配置和部署

### 场景 4：我想远程控制 Claude 开发

1. 阅读 [远程开发](deployment/REMOTE_DEV.md)
2. 配置 GitHub Actions
3. 创建 Issue 触发自动开发

### 场景 5：我想使用 AI Agents

1. 阅读 [Agency Agents 指南](guides/AGENCY_AGENTS_GUIDE.md)
2. 激活对应的 Agent
3. 开始使用专业 AI 助手

---

## 📊 项目概览

### 技术栈

**后端：**
- Python 3.12
- FastAPI
- SQLAlchemy
- AKShare

**前端：**
- React 19
- TypeScript
- Ant Design 6
- Vite

**AI 集成：**
- DeepSeek API
- Claude API
- OpenAI API

### 核心功能

- ✅ 实时行情查询
- ✅ AI 智能问答
- ✅ 市场监控
- ✅ 舆情分析
- ✅ 交易回测
- ✅ 风格探索
- ✅ 模拟交易
- ✅ 财报分析
- ✅ 费用统计

---

## 🔗 相关链接

- **GitHub 仓库**: https://github.com/zhang-geek/stock-ai-assistant
- **问题反馈**: https://github.com/zhang-geek/stock-ai-assistant/issues
- **贡献指南**: [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 📝 文档贡献

发现文档问题或想要改进？欢迎提交 PR！

1. Fork 项目
2. 创建文档分支：`git checkout -b docs/improve-xxx`
3. 提交更改：`git commit -m "docs: 改进 XXX 文档"`
4. 推送分支：`git push origin docs/improve-xxx`
5. 创建 Pull Request

---

## 📅 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-03-11 | v1.0 | 初始文档结构，整理所有文档 |
| 2026-03-10 | v0.9 | 添加部署和远程开发文档 |
| 2026-03-09 | v0.8 | 完成 Phase 0-3 开发 |

---

## 💡 提示

- 📌 建议按照文档顺序阅读，从快速启动开始
- 🔍 使用 Ctrl+F 搜索关键词快速定位
- 📖 所有文档都支持 Markdown 格式
- 🚀 遇到问题先查看对应文档的故障排除部分

---

**祝你使用愉快！** 🎉

如有问题，欢迎在 [GitHub Issues](https://github.com/zhang-geek/stock-ai-assistant/issues) 提问。
