# Claude 远程开发自动化方案

## 方案一：GitHub Actions + Claude API

### 1. 创建 GitHub Actions 工作流

`.github/workflows/claude-dev.yml`:
```yaml
name: Claude Auto Development

on:
  issues:
    types: [opened, labeled]
  schedule:
    # 每天早上 9 点运行
    - cron: '0 1 * * *'  # UTC 时间
  workflow_dispatch:
    inputs:
      task:
        description: '开发任务描述'
        required: true

jobs:
  claude-dev:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install anthropic requests

      - name: Run Claude Development Task
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python scripts/claude_auto_dev.py

      - name: Create Pull Request
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          commit-message: 'feat: Claude auto development'
          title: 'Auto: Claude Development Task'
          body: |
            ## 自动开发任务完成

            由 Claude AI 自动完成的开发任务。

            请仔细审查代码变更。
          branch: claude-auto-dev
```

### 2. Claude 自动化开发脚本

`scripts/claude_auto_dev.py`:
```python
import os
import anthropic
from pathlib import Path

def run_claude_task(task_description: str):
    """使用 Claude API 执行开发任务"""
    client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    # 读取项目上下文
    context = read_project_context()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8000,
        messages=[
            {
                "role": "user",
                "content": f"""
你是一个专业的 Python/TypeScript 开发者。

项目上下文：
{context}

任务：{task_description}

请生成完整的代码实现，包括：
1. 需要修改的文件
2. 完整的代码内容
3. 测试用例

输出格式：
FILE: path/to/file.py
```python
# 代码内容
```
"""
            }
        ]
    )

    # 解析响应并写入文件
    parse_and_write_files(message.content)

def read_project_context():
    """读取项目关键文件作为上下文"""
    files = [
        "CLAUDE.md",
        "pyproject.toml",
        "src/stock_assistant/core/models.py"
    ]

    context = []
    for file in files:
        if Path(file).exists():
            with open(file, 'r', encoding='utf-8') as f:
                context.append(f"=== {file} ===\n{f.read()}\n")

    return "\n".join(context)

def parse_and_write_files(content):
    """解析 Claude 响应并写入文件"""
    # 实现文件解析和写入逻辑
    pass

if __name__ == "__main__":
    # 从 GitHub Issue 或环境变量读取任务
    task = os.environ.get("TASK_DESCRIPTION", "优化数据库查询性能")
    run_claude_task(task)
```

---

## 方案二：使用 Claude Code CLI + SSH

### 1. 在服务器上安装 Claude Code

```bash
# SSH 连接到服务器
ssh user@your-server.com

# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 配置 API Key
claude-code config set apiKey YOUR_API_KEY
```

### 2. 创建远程开发脚本

`scripts/remote_dev.sh`:
```bash
#!/bin/bash

# 远程执行 Claude Code 命令
ssh user@your-server.com << 'EOF'
  cd /path/to/stock_personal

  # 激活虚拟环境
  source .venv/bin/activate

  # 使用 Claude Code 执行任务
  echo "添加用户认证功能" | claude-code

  # 运行测试
  pytest tests/

  # 提交代码
  git add .
  git commit -m "feat: 添加用户认证功能"
  git push
EOF
```

---

## 方案三：定时任务 + Issue 触发

### 1. 创建 Issue 模板

`.github/ISSUE_TEMPLATE/claude-task.md`:
```markdown
---
name: Claude 开发任务
about: 触发 Claude 自动开发
title: '[CLAUDE] '
labels: claude-task
---

## 任务描述


## 优先级
- [ ] 高
- [ ] 中
- [ ] 低

## 预期完成时间


## 相关文件

```

### 2. Issue 触发脚本

`scripts/issue_trigger.py`:
```python
import os
import requests
from github import Github

def process_claude_issues():
    """处理带有 claude-task 标签的 Issue"""
    g = Github(os.environ['GITHUB_TOKEN'])
    repo = g.get_repo("zhang-geek/stock-ai-assistant")

    # 获取所有 claude-task 标签的 Issue
    issues = repo.get_issues(labels=["claude-task"], state="open")

    for issue in issues:
        print(f"处理任务: {issue.title}")

        # 调用 Claude API 执行任务
        result = run_claude_task(issue.body)

        # 创建 PR
        create_pr_from_result(repo, issue, result)

        # 关闭 Issue
        issue.create_comment("✅ 任务已完成，PR 已创建")
        issue.edit(state="closed")

if __name__ == "__main__":
    process_claude_issues()
```

---

## 方案四：使用 Cron Job（本地定时任务）

### 1. 创建定时开发脚本

`scripts/daily_dev.py`:
```python
#!/usr/bin/env python3
"""每日自动开发任务"""

import anthropic
import subprocess
from datetime import datetime

def daily_tasks():
    """定义每日任务列表"""
    return [
        "检查并修复代码中的 TODO 注释",
        "优化数据库查询性能",
        "更新依赖包到最新版本",
        "运行测试并修复失败的测试",
        "生成每日开发报告"
    ]

def execute_task(task: str):
    """执行单个任务"""
    client = anthropic.Anthropic()

    # 使用 Claude 分析和执行任务
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"任务: {task}\n\n请分析项目并提供解决方案。"
        }]
    )

    return response.content

def main():
    print(f"开始每日开发任务 - {datetime.now()}")

    for task in daily_tasks():
        print(f"\n执行任务: {task}")
        result = execute_task(task)
        print(f"完成: {result}")

    # 提交更改
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", f"chore: 每日自动优化 {datetime.now().date()}"])
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    main()
```

### 2. 使用 Claude Code 的 Cron 功能

```bash
# 在 Claude Code 中设置定时任务
/cron create "0 9 * * *" "检查并修复代码质量问题，运行测试，提交改进"
```

---

## 方案五：Webhook 触发

### 1. 创建 Webhook 服务器

`scripts/webhook_server.py`:
```python
from flask import Flask, request
import anthropic
import subprocess

app = Flask(__name__)

@app.route('/webhook/claude-dev', methods=['POST'])
def claude_dev_webhook():
    """接收 Webhook 触发开发任务"""
    data = request.json
    task = data.get('task', '')

    if not task:
        return {'error': 'No task provided'}, 400

    # 执行 Claude 开发任务
    result = run_claude_development(task)

    return {'status': 'success', 'result': result}

def run_claude_development(task: str):
    """执行开发任务"""
    # 实现开发逻辑
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 2. 使用 Telegram Bot 触发

```python
from telegram import Update
from telegram.ext import Application, CommandHandler

async def dev_command(update: Update, context):
    """处理 /dev 命令"""
    task = ' '.join(context.args)

    await update.message.reply_text(f"开始执行任务: {task}")

    # 调用 Claude API
    result = run_claude_task(task)

    await update.message.reply_text(f"任务完成: {result}")

def main():
    app = Application.builder().token("YOUR_BOT_TOKEN").build()
    app.add_handler(CommandHandler("dev", dev_command))
    app.run_polling()
```

---

## 推荐方案

**最佳实践组合：**

1. **日常开发**：GitHub Actions + Issue 触发
2. **紧急任务**：Telegram Bot 远程触发
3. **定时优化**：Cron Job 每日运行
4. **远程访问**：Cloudflare Tunnel + VPS

**安全注意事项：**
- 使用 GitHub Secrets 存储 API Key
- 限制 Webhook 访问 IP
- 代码审查所有自动生成的代码
- 设置任务执行频率限制
