"""回测模块CLI命令"""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.table import Table

backtest_app = typer.Typer()
console = Console(force_terminal=True)


@backtest_app.command("import")
def import_trades(
    file: str = typer.Argument(..., help="CSV文件路径"),
    broker: str = typer.Option("generic", help="券商格式"),
):
    """导入券商交易记录"""
    from stock_assistant.backtest.importer import TradeImporter

    importer = TradeImporter()
    try:
        count = importer.import_csv(file, broker=broker)
        console.print(f"[green]成功导入 {count} 条交易记录[/green]")
    except Exception as e:
        console.print(f"[red]导入失败: {e}[/red]")
        raise typer.Exit(1)


@backtest_app.command()
def analyze():
    """分析历史交易"""
    from stock_assistant.backtest.analyzer import TradeAnalyzer

    analyzer = TradeAnalyzer()
    stats = analyzer.get_statistics()

    if stats["total_trades"] == 0:
        console.print("[yellow]暂无交易记录，请先导入[/yellow]")
        return

    # 展示统计表
    table = Table(title="交易统计")
    table.add_column("指标", style="bold")
    table.add_column("值", justify="right")

    table.add_row("总交易次数", str(stats["total_trades"]))
    table.add_row("配对交易数", str(stats["paired_count"]))
    table.add_row("胜率", f"{stats['win_rate']:.1%}")
    table.add_row("平均盈利率", f"{stats['avg_profit']:.2%}")
    table.add_row("最大单笔盈利", f"{stats['max_profit']:.2%}")
    table.add_row("最大单笔亏损", f"{stats['max_loss']:.2%}")
    table.add_row("盈亏比", f"{stats['profit_loss_ratio']:.2f}")
    table.add_row("交易最多股票", stats["most_traded"])

    console.print(table)

    # 按月盈亏
    if stats.get("monthly_pnl"):
        monthly_table = Table(title="按月盈亏(元)")
        monthly_table.add_column("月份", style="bold")
        monthly_table.add_column("盈亏", justify="right")

        for month, pnl in stats["monthly_pnl"].items():
            color = "red" if pnl >= 0 else "green"
            monthly_table.add_row(month, f"[{color}]{pnl:+,.0f}[/{color}]")

        console.print(monthly_table)

    # AI分析
    async def _ai():
        with console.status("AI分析中..."):
            return await analyzer.ai_analysis(stats)

    try:
        result = asyncio.run(_ai())
        console.print("\n[bold]AI分析:[/bold]")
        console.print(result)
    except Exception as e:
        console.print(f"[yellow]AI分析跳过: {e}[/yellow]")


@backtest_app.command()
def history(n: int = typer.Option(20, "-n", help="显示条数")):
    """查看交易历史"""
    from stock_assistant.core.database import get_session
    from stock_assistant.core.models import Trade

    session = get_session()
    try:
        trades = (
            session.query(Trade)
            .order_by(Trade.trade_time.desc())
            .limit(n)
            .all()
        )

        if not trades:
            console.print("[yellow]暂无交易记录[/yellow]")
            return

        table = Table(title=f"最近 {n} 条交易记录")
        table.add_column("时间")
        table.add_column("代码")
        table.add_column("名称", style="bold")
        table.add_column("方向")
        table.add_column("价格", justify="right")
        table.add_column("数量", justify="right")
        table.add_column("金额", justify="right")
        table.add_column("手续费", justify="right")

        for t in trades:
            dir_style = "red" if t.direction == "buy" else "green"
            dir_text = "买入" if t.direction == "buy" else "卖出"
            table.add_row(
                t.trade_time.strftime("%Y-%m-%d %H:%M"),
                t.symbol,
                t.name or "",
                f"[{dir_style}]{dir_text}[/{dir_style}]",
                f"{t.price:.2f}",
                f"{t.quantity:,}",
                f"{t.amount:,.0f}",
                f"{t.fee:.2f}",
            )

        console.print(table)
    finally:
        session.close()
