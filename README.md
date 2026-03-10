# 🎯 A股AI助手

> 基于 FastAPI + React 的智能投资分析平台，集成 LLM 路由系统（DeepSeek/Claude/OpenAI）

[![GitHub stars](https://img.shields.io/github/stars/zhang-geek/stock-ai-assistant?style=social)](https://github.com/zhang-geek/stock-ai-assistant)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-blue?logo=react)](https://reactjs.org/)

---

## ✨ 特性

- 🎨 **现代化 UI** - React 19 + TypeScript + Ant Design 6
- ⚡ **高性能后端** - FastAPI + SQLAlchemy + 三级缓存
- 🤖 **智能 AI** - LLM 路由系统，自动选择最优模型
- 📊 **实时行情** - AKShare 数据源，60秒自动刷新
- 🎭 **AI Agents** - 50+ 专业 AI 助手随时调用
- 🚀 **自动化开发** - GitHub Actions + Claude API
- 🌐 **远程访问** - Cloudflare Tunnel 支持

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/zhang-geek/stock-ai-assistant.git
cd stock-ai-assistant
```

### 2. 后端启动

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/Scripts/activate  # Windows Git Bash

# 安装依赖
pip install -e ".[dev,web]"

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 启动后端
uvicorn stock_assistant.api.main:app --reload --port 8000
```

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问应用

- **前端**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs

---

## 📚 文档

完整文档请访问 **[docs/](docs/README.md)**

### 快速导航

| 文档 | 描述 |
|------|------|
| [快速启动](docs/guides/STARTUP.md) | 5分钟快速启动指南 |
| [开发指南](docs/development/DEVELOPMENT.md) | 完整开发文档 |
| [部署指南](docs/deployment/DEPLOYMENT.md) | 远程访问和部署 |
| [API 参考](docs/reference/API.md) | FastAPI 接口文档 |
| [数据库模型](docs/reference/DATABASE.md) | SQLAlchemy ORM 模型 |
| [Agency Agents](docs/guides/AGENCY_AGENTS_GUIDE.md) | AI 专家团队使用 |
| [远程开发](docs/deployment/REMOTE_DEV.md) | Claude 自动化开发 |

---

## 🎯 核心功能

### 📈 行情查询
- 实时行情数据
- 日K线图表
- 涨跌幅排行
- 板块表现

### 💬 AI 问答
- 智能对话界面
- 流式响应
- 多模型支持
- 费用统计

### 📊 市场监控
- 异动监控
- 市场概览
- 实时更新

### 📰 舆情分析
- 新闻抓取
- 情感分析
- 热点追踪

### 📈 交易回测
- CSV 导入
- 统计分析
- 收益曲线
- 风险指标

### 🎯 风格探索
- 交易风格识别
- 个性化建议
- 策略优化

### 💼 模拟交易
- 虚拟账户
- 实时下单
- 持仓管理
- AI 决策

### 📑 财报分析
- PDF 上传
- 智能解析
- 关键指标提取

---

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **数据库**: SQLite
- **数据源**: AKShare
- **AI**: DeepSeek / Claude / OpenAI

### 前端
- **框架**: React 19
- **语言**: TypeScript
- **UI**: Ant Design 6
- **构建**: Vite
- **路由**: React Router 7

### 开发工具
- **代码检查**: Ruff
- **测试**: Pytest
- **类型检查**: MyPy
- **包管理**: pip

---

## 📊 项目结构

```
stock_personal/
├── src/stock_assistant/      # 后端源码
│   ├── api/                   # FastAPI 路由
│   ├── core/                  # 核心模块
│   ├── llm/                   # LLM 路由系统
│   ├── data/                  # 数据源
│   ├── market/                # 市场监控
│   ├── sentiment/             # 舆情分析
│   ├── backtest/              # 交易回测
│   ├── style/                 # 风格探索
│   ├── paper_trading/         # 模拟交易
│   └── financial/             # 财报分析
│
├── frontend/                  # 前端源码
│   ├── src/
│   │   ├── pages/            # 页面组件
│   │   ├── components/       # 通用组件
│   │   ├── api/              # API 客户端
│   │   ├── types/            # TypeScript 类型
│   │   └── styles/           # 样式文件
│   └── public/               # 静态资源
│
├── docs/                      # 文档
│   ├── guides/               # 使用指南
│   ├── development/          # 开发文档
│   ├── deployment/           # 部署文档
│   └── reference/            # 参考文档
│
├── tests/                     # 测试文件
├── scripts/                   # 脚本工具
├── config/                    # 配置文件
└── data/                      # 数据目录
```

---

## 🤖 AI Agents

项目集成了 50+ 专业 AI agents，涵盖：

- 💻 **工程**: Frontend Developer, Backend Architect, DevOps
- 🎨 **设计**: UI Designer, UX Researcher, Brand Guardian
- 📢 **营销**: Social Media Manager, Content Strategist
- 📊 **产品**: Product Manager, Data Analyst
- 🧪 **测试**: QA Engineer, Bug Hunter

**使用方法**:
```
"激活 Frontend Developer 模式，帮我优化 Dashboard 组件"
```

详见 [Agency Agents 指南](docs/guides/AGENCY_AGENTS_GUIDE.md)

---

## 🚀 远程访问

### Cloudflare Tunnel（推荐）

```bash
# 安装
winget install --id Cloudflare.cloudflared

# 创建隧道
cloudflared tunnel create stock-ai-assistant

# 启动
cloudflared tunnel run stock-ai-assistant
```

### GitHub Actions 自动开发

1. 创建 Issue，添加 `claude-task` 标签
2. GitHub Actions 自动触发 Claude 开发
3. 完成后自动创建 PR

详见 [远程开发指南](docs/deployment/REMOTE_DEV.md)

---

## 📈 开发进度

- ✅ Phase 0: 基础框架
- ✅ Phase 1: 环境配置
- ✅ Phase 2: 核心功能
- ✅ Phase 3: Web 前端
- ✅ UI 优化和动画系统
- ✅ 远程访问和自动化
- 🚧 Phase 4: 高级功能（进行中）

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m "feat: add amazing feature"`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 🙏 致谢

- [AKShare](https://github.com/akfamily/akshare) - A股数据源
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Web 框架
- [Ant Design](https://ant.design/) - 企业级 UI 组件库
- [Agency Agents](https://github.com/msitarzewski/agency-agents) - AI 专家团队
- [Claude](https://www.anthropic.com/) - AI 助手

---

## 📞 联系方式

- **GitHub**: [@zhang-geek](https://github.com/zhang-geek)
- **Issues**: [提交问题](https://github.com/zhang-geek/stock-ai-assistant/issues)
- **Email**: [联系我们](mailto:your-email@example.com)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**

[![Star History Chart](https://api.star-history.com/svg?repos=zhang-geek/stock-ai-assistant&type=Date)](https://star-history.com/#zhang-geek/stock-ai-assistant&Date)
