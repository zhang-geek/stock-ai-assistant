# Agency Agents 使用指南

## 📦 安装完成

Agency Agents 已成功安装到 Claude Code！

**安装位置**: `C:\Users\zhang\.claude\agents\`

---

## 🎭 可用的 AI 专家团队

### 💻 工程部门 (Engineering)

| Agent | 专长 | 使用场景 |
|-------|------|---------|
| 🎨 Frontend Developer | React/Vue/Angular, UI实现, 性能优化 | 现代Web应用, 像素级UI, Core Web Vitals优化 |
| 🏗️ Backend Architect | API设计, 数据库架构, 可扩展性 | 服务端系统, 微服务, 云基础设施 |
| 📱 Mobile App Builder | iOS/Android, React Native, Flutter | 原生和跨平台移动应用 |
| 🤖 AI Engineer | ML模型, 部署, AI集成 | 机器学习功能, 数据管道, AI应用 |
| 🚀 DevOps Automator | CI/CD, 基础设施自动化, 云运维 | 管道开发, 部署自动化, 监控 |
| ⚡ Rapid Prototyper | 快速POC开发, MVP | 快速原型, 黑客松项目, 快速迭代 |
| 💎 Senior Developer | Laravel/Livewire, 高级模式 | 复杂实现, 架构决策 |
| 🔒 Security Engineer | 威胁建模, 安全代码审查 | 应用安全, 漏洞评估, 安全CI/CD |

### 🎨 设计部门 (Design)

| Agent | 专长 | 使用场景 |
|-------|------|---------|
| 🎯 UI Designer | 视觉设计, 组件库, 设计系统 | 界面创建, 品牌一致性, 组件设计 |
| 🔍 UX Researcher | 用户测试, 行为分析, 研究 | 理解用户, 可用性测试, 设计洞察 |
| 🏛️ UX Architect | 技术架构, CSS系统, 实现 | 开发友好的基础, 实现指导 |
| 🎭 Brand Guardian | 品牌识别, 一致性, 定位 | 品牌策略, 身份开发, 指南 |
| ✨ Whimsy Injector | 个性, 愉悦, 有趣的交互 | 添加乐趣, 微交互, 彩蛋, 品牌个性 |
| 📷 Image Prompt Engineer | AI图像生成提示, 摄影 | Midjourney, DALL-E, Stable Diffusion提示 |

### 📢 营销部门 (Marketing)

| Agent | 专长 | 使用场景 |
|-------|------|---------|
| 📱 Social Media Manager | 社交媒体策略, 内容创作 | 社交媒体营销, 社区管理 |
| 📝 Content Strategist | 内容策略, SEO, 文案 | 内容营销, 博客, SEO优化 |
| 🎯 Growth Hacker | 增长策略, 数据分析 | 用户增长, A/B测试, 转化优化 |

### 📊 产品部门 (Product)

| Agent | 专长 | 使用场景 |
|-------|------|---------|
| 🎯 Product Manager | 产品策略, 路线图, 需求 | 产品规划, 功能优先级, 用户故事 |
| 📊 Data Analyst | 数据分析, 可视化, 洞察 | 数据驱动决策, 报告, 仪表板 |

### 🧪 测试部门 (Testing)

| Agent | 专长 | 使用场景 |
|-------|------|---------|
| 🧪 QA Engineer | 测试策略, 自动化测试 | 质量保证, 测试计划, 自动化 |
| 🐛 Bug Hunter | 缺陷检测, 回归测试 | Bug追踪, 测试用例, 质量控制 |

---

## 🚀 使用方法

### 方法 1：直接激活 Agent（推荐）

在 Claude Code 对话中直接说：

```
"激活 Frontend Developer 模式，帮我构建一个 React 组件"
```

或者：

```
"使用 UI Designer agent 帮我设计一个登录页面"
```

### 方法 2：使用 Agent 工具

```
/agent engineering/engineering-frontend-developer
```

### 方法 3：在项目中引用

创建 `.claude/agents.md` 文件：

```markdown
# 项目 Agents

## 前端开发
使用 Frontend Developer agent 进行所有前端开发工作。

## UI设计
使用 UI Designer agent 进行界面设计。
```

---

## 💡 实际使用示例

### 示例 1：构建 React 组件

```
我：激活 Frontend Developer 模式，帮我创建一个带动画的卡片组件

Claude (Frontend Developer 模式):
我会为你创建一个现代化的 React 卡片组件，包含：
- 悬停动画效果
- 响应式设计
- TypeScript 类型定义
- 可访问性支持

[生成完整的组件代码]
```

### 示例 2：优化性能

```
我：使用 Frontend Developer agent 分析并优化我的应用性能

Claude:
我会进行全面的性能审计：
1. Core Web Vitals 分析
2. Bundle 大小优化
3. 代码分割建议
4. 懒加载实现
5. 缓存策略

[提供详细的优化方案]
```

### 示例 3：设计系统

```
我：激活 UI Designer 模式，帮我创建一个设计系统

Claude (UI Designer 模式):
我会创建一个完整的设计系统，包括：
- 颜色系统
- 排版规范
- 组件库
- 间距系统
- 图标集

[生成设计系统文档和代码]
```

---

## 🎯 针对 A股AI助手项目的推荐 Agents

### 当前项目适用的 Agents：

1. **Frontend Developer** - 优化 React 前端
   ```
   "使用 Frontend Developer agent 优化我们的 Dashboard 组件性能"
   ```

2. **UI Designer** - 改进界面设计
   ```
   "激活 UI Designer 模式，重新设计我们的行情查询页面"
   ```

3. **Backend Architect** - 优化 FastAPI 后端
   ```
   "使用 Backend Architect agent 审查我们的 API 架构"
   ```

4. **DevOps Automator** - 部署自动化
   ```
   "激活 DevOps Automator 模式，帮我设置 CI/CD 管道"
   ```

5. **Security Engineer** - 安全审计
   ```
   "使用 Security Engineer agent 审查我们的应用安全性"
   ```

---

## 📝 创建自定义 Agent

你也可以创建自己的 Agent：

```markdown
---
name: Stock Market Analyst
description: 专业的A股市场分析师
color: green
---

# Stock Market Analyst Agent

你是一个专业的A股市场分析师...

## 核心任务
- 分析市场趋势
- 提供投资建议
- 风险评估

## 工作流程
1. 收集市场数据
2. 技术分析
3. 基本面分析
4. 生成报告
```

保存到：`~/.claude/agents/custom/stock-analyst.md`

---

## 🔧 高级配置

### 组合多个 Agents

```
"使用 Frontend Developer 和 UI Designer agents 一起重新设计我们的首页"
```

### Agent 切换

```
"切换到 Backend Architect 模式"
"现在使用 DevOps Automator 模式"
```

### 项目级 Agent 配置

在项目根目录创建 `.claude/project-agents.md`：

```markdown
# A股AI助手 - 项目 Agents

## 默认 Agents
- Frontend: engineering/engineering-frontend-developer
- Backend: engineering/engineering-backend-architect
- Design: design/design-ui-designer

## 特殊任务
- 性能优化: engineering/engineering-rapid-prototyper
- 安全审计: engineering/engineering-security-engineer
```

---

## 📚 更多资源

- **完整文档**: `~/.claude/agents/README.md`
- **示例**: `~/.claude/agents/examples/`
- **贡献指南**: `~/.claude/agents/CONTRIBUTING.md`

---

## 🎉 开始使用

现在你可以在任何 Claude Code 对话中激活这些专业 AI agents！

**试试这个：**
```
"激活 Frontend Developer 模式，帮我优化 A股AI助手的前端性能"
```

祝你使用愉快！🚀
