# 📚 文档结构总览

```
A股AI助手 项目文档
│
├── 📄 README.md                          # 项目主页
├── 📄 CLAUDE.md                          # Claude Code 开发指南
│
└── 📁 docs/                              # 文档中心
    │
    ├── 📄 README.md                      # 文档导航中心 ⭐
    │
    ├── 📁 guides/                        # 📖 使用指南
    │   ├── STARTUP.md                    # 快速启动（5分钟）
    │   └── AGENCY_AGENTS_GUIDE.md        # AI Agents 使用指南
    │
    ├── 📁 development/                   # 👨‍💻 开发文档
    │   ├── DEVELOPMENT.md                # 完整开发指南
    │   └── IMPLEMENTATION_SUMMARY.md     # 实现总结（Phase 0-3）
    │
    ├── 📁 deployment/                    # 🚀 部署文档
    │   ├── DEPLOYMENT.md                 # 部署指南
    │   └── REMOTE_DEV.md                 # 远程开发自动化
    │
    └── 📁 reference/                     # 📚 参考文档
        ├── API.md                        # API 接口完整参考
        └── DATABASE.md                   # 数据库模型参考
```

---

## 🎯 快速导航

### 我想...

#### 🚀 快速开始
→ [README.md](../README.md) → [guides/STARTUP.md](guides/STARTUP.md)

#### 👨‍💻 参与开发
→ [CLAUDE.md](../CLAUDE.md) → [development/DEVELOPMENT.md](development/DEVELOPMENT.md)

#### 🚢 部署项目
→ [deployment/DEPLOYMENT.md](deployment/DEPLOYMENT.md)

#### 🤖 使用 AI Agents
→ [guides/AGENCY_AGENTS_GUIDE.md](guides/AGENCY_AGENTS_GUIDE.md)

#### 📡 查看 API
→ [reference/API.md](reference/API.md)

#### 🗄️ 了解数据库
→ [reference/DATABASE.md](reference/DATABASE.md)

---

## 📊 文档统计

| 类别 | 文档数 | 总字数 |
|------|--------|--------|
| 使用指南 | 2 | ~8,000 |
| 开发文档 | 2 | ~22,000 |
| 部署文档 | 2 | ~11,000 |
| 参考文档 | 2 | ~15,000 |
| **总计** | **8** | **~56,000** |

---

## 🔄 文档更新日志

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-03-11 | v1.0 | 完整文档结构重组，新增 API 和数据库参考 |
| 2026-03-10 | v0.9 | 添加部署和远程开发文档 |
| 2026-03-09 | v0.8 | 完成 Phase 0-3 开发文档 |

---

## 📝 文档贡献指南

### 文档命名规范

- 使用大写字母开头
- 使用下划线分隔单词
- 使用 `.md` 扩展名
- 例如：`API_REFERENCE.md`

### 文档结构规范

```markdown
# 标题

> 简短描述

---

## 章节 1

内容...

---

## 章节 2

内容...
```

### 提交文档更新

```bash
git checkout -b docs/improve-xxx
# 编辑文档
git commit -m "docs: 改进 XXX 文档"
git push origin docs/improve-xxx
# 创建 PR
```

---

## 🔍 搜索技巧

### 按关键词搜索

```bash
# 在所有文档中搜索
grep -r "关键词" docs/

# 在特定目录搜索
grep -r "API" docs/reference/
```

### 按文件类型搜索

```bash
# 查找所有 Markdown 文件
find docs/ -name "*.md"

# 查找包含特定内容的文件
find docs/ -name "*.md" -exec grep -l "FastAPI" {} \;
```

---

## 📖 推荐阅读顺序

### 新用户
1. README.md
2. guides/STARTUP.md
3. guides/AGENCY_AGENTS_GUIDE.md

### 开发者
1. CLAUDE.md
2. development/DEVELOPMENT.md
3. reference/API.md
4. reference/DATABASE.md

### 运维人员
1. deployment/DEPLOYMENT.md
2. deployment/REMOTE_DEV.md

---

## 🎨 文档图标说明

- 📄 单个文档文件
- 📁 文档目录
- 📖 使用指南
- 👨‍💻 开发文档
- 🚀 部署文档
- 📚 参考文档
- ⭐ 重要文档
- 🔥 热门文档
- 🆕 新增文档

---

**提示**: 所有文档都支持 Markdown 格式，可以在 GitHub 上直接阅读。
