"""市场监控 CLI 命令"""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from stock_assistant.market.analyzer import MarketAnalyzer

market_app = typer.Typer()
console = Console(force_terminal=True)


@market_app.command()
def morning():
    """盘前简报 - AI生成今日市场概览"""
    analyzer = MarketAnalyzer()

    async def _run():
        with console.status("正在生成盘前简报..."):
            report = await analyzer.morning_brief()
        console.print("\n[bold]盘前简报[/bold]\n")
        console.print(report)

    asyncio.run(_run())


@market_app.command()
def review():
    """盘后复盘 - AI生成今日行情总结"""
    analyzer = MarketAnalyzer()

    async def _run():
        with console.status("正在生成盘后复盘..."):
            report = await analyzer.evening_review()
        console.print("\n[bold]盘后复盘[/bold]\n")
        console.print(report)

    asyncio.run(_run())


@market_app.command()
def scan(
    threshold: float = typer.Option(5.0, "--threshold", "-t", help="涨跌幅阈值(%)"),
):
    """异动扫描 - 扫描涨跌幅超过阈值的股票"""
    analyzer = MarketAnalyzer()

    async def _run():
        with console.status(f"正在扫描异动（阈值: {threshold}%）..."):
            signals = await analyzer.scan_signals(threshold)

        if not signals:
            console.print(f"[dim]未发现涨跌幅超过 {threshold}% 的异动[/dim]")
            return

        table = Table(title=f"异动扫描（阈值: {threshold}%）")
        table.add_column("类型", style="bold")
        table.add_column("代码")
        table.add_column("名称")
        table.add_column("涨跌幅", justify="right")
        table.add_column("严重度")

        for sig in signals:
            color = "red" if sig["change_pct"] >= 0 else "green"
            severity_style = "bold red" if sig["severity"] == "high" else "yellow"
            table.add_row(
                "大涨" if sig["signal_type"] == "price_surge" else "大跌",
                sig["symbol"],
                sig["name"],
                f"[{color}]{sig['change_pct']:+.2f}%[/{color}]",
                f"[{severity_style}]{sig['severity']}[/{severity_style}]",
            )

        console.print(table)
        console.print(f"\n[dim]共发现 {len(signals)} 个异动信号，已写入数据库[/dim]")

    asyncio.run(_run())
