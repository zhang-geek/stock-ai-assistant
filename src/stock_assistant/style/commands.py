"""风格探索模块CLI命令"""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.table import Table

style_app = typer.Typer()
console = Console(force_terminal=True)


@style_app.command()
def analyze():
    """分析交易风格"""
    from stock_assistant.backtest.analyzer import TradeAnalyzer
    from stock_assistant.style.analyzer import StyleAnalyzer

    style_analyzer = StyleAnalyzer()
    style_data = style_analyzer.analyze_style()

    if not style_data:
        console.print("[yellow]暂无交易记录，请先导入[/yellow]")
        return

    # 风格特征表
    table = Table(title="交易风格分析")
    table.add_column("特征", style="bold")
    table.add_column("值", justify="right")

    table.add_row("风格标签", f"[bold cyan]{style_data['style_label']}[/bold cyan]")
    table.add_row("平均持仓天数", f"{style_data['avg_holding_days']}天")
    table.add_row("月均交易次数", f"{style_data['trading_frequency']}次")
    table.add_row("交易时间偏好", style_data["time_pattern"])
    table.add_row("交易股票数", f"{style_data['concentration']}只")

    console.print(table)

    # 偏好股票
    if style_data["position_preference"]:
        pref_table = Table(title="偏好股票 TOP 5")
        pref_table.add_column("股票", style="bold")
        for item in style_data["position_preference"]:
            pref_table.add_row(item)
        console.print(pref_table)

    # 交易统计
    trade_analyzer = TradeAnalyzer()
    stats = trade_analyzer.get_statistics()

    if stats.get("paired_count", 0) > 0:
        stats_table = Table(title="交易统计")
        stats_table.add_column("指标", style="bold")
        stats_table.add_column("值", justify="right")

        stats_table.add_row("配对交易数", str(stats["paired_count"]))
        stats_table.add_row("胜率", f"{stats['win_rate']:.1%}")
        stats_table.add_row("平均盈利率", f"{stats['avg_profit']:.2%}")
        stats_table.add_row("盈亏比", f"{stats['profit_loss_ratio']:.2f}")

        console.print(stats_table)


@style_app.command()
def coach():
    """AI交易教练 - 获取个性化改进建议"""
    from stock_assistant.backtest.analyzer import TradeAnalyzer
    from stock_assistant.style.analyzer import StyleAnalyzer

    style_analyzer = StyleAnalyzer()
    style_data = style_analyzer.analyze_style()

    if not style_data:
        console.print("[yellow]暂无交易记录，无法提供教练建议[/yellow]")
        return

    trade_analyzer = TradeAnalyzer()
    stats = trade_analyzer.get_statistics()

    async def _coach():
        with console.status("AI教练分析中..."):
            return await style_analyzer.ai_coach(style_data, stats)

    try:
        result = asyncio.run(_coach())
        console.print("\n[bold]AI交易教练建议:[/bold]")
        console.print(result)
    except Exception as e:
        console.print(f"[yellow]AI教练分析跳过: {e}[/yellow]")
