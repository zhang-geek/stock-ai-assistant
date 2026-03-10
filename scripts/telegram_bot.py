#!/usr/bin/env python3
"""
Telegram Bot - 远程触发 Claude 开发
使用方法：
1. 创建 Telegram Bot (通过 @BotFather)
2. 设置环境变量 TELEGRAM_BOT_TOKEN
3. 运行此脚本
4. 发送 /dev <任务描述> 触发开发
"""

import os
import asyncio
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /start 命令"""
    await update.message.reply_text(
        "🤖 A股AI助手 - Claude 开发 Bot\n\n"
        "可用命令：\n"
        "/dev <任务> - 触发开发任务\n"
        "/status - 查看项目状态\n"
        "/deploy - 部署到服务器\n"
        "/test - 运行测试"
    )

async def dev_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理 /dev 命令 - 触发开发任务"""
    if not context.args:
        await update.message.reply_text("❌ 请提供任务描述\n\n用法: /dev 添加用户登录功能")
        return

    task = ' '.join(context.args)

    await update.message.reply_text(f"🚀 开始执行任务: {task}\n\n请稍候...")

    try:
        # 触发 GitHub Actions
        result = subprocess.run(
            [
                "gh", "workflow", "run", "claude-dev.yml",
                "-f", f"task={task}"
            ],
            capture_output=True,
            text=True,
            cwd="/path/to/stock_personal"  # 修改为你的项目路径
        )

        if result.returncode == 0:
            await update.message.reply_text(
                f"✅ 任务已提交到 GitHub Actions\n\n"
                f"任务: {task}\n\n"
                f"请在 GitHub 查看执行进度"
            )
        else:
            await update.message.reply_text(f"❌ 提交失败: {result.stderr}")

    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """查看项目状态"""
    try:
        # 获取 git 状态
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            cwd="/path/to/stock_personal"
        )

        status = result.stdout if result.stdout else "工作区干净"

        await update.message.reply_text(
            f"📊 项目状态\n\n"
            f"```\n{status}\n```",
            parse_mode="Markdown"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """运行测试"""
    await update.message.reply_text("🧪 正在运行测试...")

    try:
        result = subprocess.run(
            ["pytest", "tests/", "-v"],
            capture_output=True,
            text=True,
            cwd="/path/to/stock_personal",
            timeout=60
        )

        output = result.stdout[-1000:]  # 最后 1000 字符

        if result.returncode == 0:
            await update.message.reply_text(f"✅ 测试通过\n\n```\n{output}\n```", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ 测试失败\n\n```\n{output}\n```", parse_mode="Markdown")

    except subprocess.TimeoutExpired:
        await update.message.reply_text("⏱️ 测试超时")
    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

async def deploy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """部署到服务器"""
    await update.message.reply_text("🚀 开始部署...")

    try:
        # 推送到 GitHub
        subprocess.run(["git", "push"], cwd="/path/to/stock_personal", check=True)

        # 触发部署（根据你的部署方式调整）
        # 例如：SSH 到服务器并拉取代码
        result = subprocess.run(
            [
                "ssh", "user@your-server.com",
                "cd /path/to/stock_personal && git pull && docker-compose up -d"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            await update.message.reply_text("✅ 部署成功")
        else:
            await update.message.reply_text(f"❌ 部署失败: {result.stderr}")

    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

def main():
    """启动 Bot"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ 错误: 未设置 TELEGRAM_BOT_TOKEN")
        return

    # 创建应用
    app = Application.builder().token(token).build()

    # 添加命令处理器
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dev", dev_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("test", test_command))
    app.add_handler(CommandHandler("deploy", deploy_command))

    print("🤖 Telegram Bot 已启动")
    print("发送 /start 开始使用")

    # 启动 Bot
    app.run_polling()

if __name__ == "__main__":
    main()
