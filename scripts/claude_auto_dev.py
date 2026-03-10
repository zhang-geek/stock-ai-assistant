#!/usr/bin/env python3
"""
Claude 自动开发脚本
通过 GitHub Actions 触发，使用 Claude API 执行开发任务
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict
import anthropic
from github import Github

def read_project_context() -> str:
    """读取项目关键文件作为上下文"""
    context_files = [
        "CLAUDE.md",
        "pyproject.toml",
        "src/stock_assistant/core/models.py",
        "frontend/package.json"
    ]

    context = []
    for file_path in context_files:
        path = Path(file_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    context.append(f"=== {file_path} ===\n{content}\n")
            except Exception as e:
                print(f"Warning: Could not read {file_path}: {e}")

    return "\n".join(context)

def get_task_description() -> str:
    """从环境变量或 GitHub Issue 获取任务描述"""
    # 优先使用手动输入的任务
    task = os.environ.get("TASK_DESCRIPTION")
    if task:
        return task

    # 从 GitHub Issue 获取
    issue_number = os.environ.get("ISSUE_NUMBER")
    if issue_number:
        g = Github(os.environ.get("GITHUB_TOKEN"))
        repo = g.get_repo(os.environ.get("GITHUB_REPOSITORY", "zhang-geek/stock-ai-assistant"))
        issue = repo.get_issue(int(issue_number))
        return f"{issue.title}\n\n{issue.body}"

    return "优化代码质量和性能"

def parse_claude_response(content: str) -> List[Dict[str, str]]:
    """解析 Claude 响应，提取文件路径和内容"""
    files = []
    lines = content.split('\n')

    current_file = None
    current_content = []
    in_code_block = False

    for line in lines:
        # 检测文件标记
        if line.startswith('FILE:') or line.startswith('### FILE:'):
            if current_file and current_content:
                files.append({
                    'path': current_file,
                    'content': '\n'.join(current_content)
                })

            current_file = line.split(':', 1)[1].strip()
            current_content = []
            in_code_block = False

        # 检测代码块
        elif line.startswith('```'):
            in_code_block = not in_code_block
            if not in_code_block and current_content:
                # 代码块结束
                pass

        # 收集代码内容
        elif current_file and in_code_block:
            current_content.append(line)

    # 添加最后一个文件
    if current_file and current_content:
        files.append({
            'path': current_file,
            'content': '\n'.join(current_content)
        })

    return files

def write_files(files: List[Dict[str, str]]):
    """将文件写入磁盘"""
    for file_info in files:
        file_path = Path(file_info['path'])

        # 创建目录
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_info['content'])

        print(f"✅ 已写入: {file_path}")

def run_claude_task(task_description: str):
    """使用 Claude API 执行开发任务"""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ 错误: 未设置 ANTHROPIC_API_KEY")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # 读取项目上下文
    context = read_project_context()

    print(f"📋 任务: {task_description}")
    print("🤖 正在调用 Claude API...")

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8000,
            messages=[
                {
                    "role": "user",
                    "content": f"""你是一个专业的全栈开发者，正在开发 A股AI助手项目。

项目上下文：
{context}

开发任务：
{task_description}

请完成以下工作：
1. 分析任务需求
2. 设计实现方案
3. 编写完整的代码
4. 确保代码质量和最佳实践

输出格式要求：
对于每个需要创建或修改的文件，使用以下格式：

FILE: path/to/file.py
```python
# 完整的文件内容
```

FILE: path/to/another/file.tsx
```typescript
// 完整的文件内容
```

注意：
- 提供完整可运行的代码
- 遵循项目现有的代码风格
- 添加必要的注释
- 确保类型安全
"""
                }
            ]
        )

        # 提取文本内容
        response_text = ""
        for block in message.content:
            if hasattr(block, 'text'):
                response_text += block.text

        print("✅ Claude 响应已接收")
        print(f"📝 响应长度: {len(response_text)} 字符")

        # 解析并写入文件
        files = parse_claude_response(response_text)

        if not files:
            print("⚠️  警告: 未检测到文件输出")
            print("响应内容:")
            print(response_text[:500])
            return

        print(f"📁 检测到 {len(files)} 个文件")

        # 写入文件
        write_files(files)

        print("✅ 所有文件已写入完成")

    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

def main():
    print("🚀 Claude 自动开发任务启动")
    print("=" * 50)

    # 获取任务描述
    task = get_task_description()

    # 执行任务
    run_claude_task(task)

    print("=" * 50)
    print("✅ 任务执行完成")

if __name__ == "__main__":
    main()
