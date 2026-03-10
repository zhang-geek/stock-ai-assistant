"""财报分析 CLI 子命令"""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

financial_app = typer.Typer(help="财报分析")
console = Console(force_terminal=True)


@financial_app.command()
def analyze(
    pdf: str = typer.Argument(..., help="财报PDF文件路径"),
    symbol: str = typer.Option("", "--symbol", "-s", help="股票代码，用于保存指标"),
    report_date: str = typer.Option("", "--date", "-d", help="报告期，如 2024-12-31"),
):
    """分析财报PDF"""
    pdf_path = Path(pdf)
    if not pdf_path.exists():
        console.print(f"[red]文件不存在: {pdf}[/red]")
        raise typer.Exit(1)
    if not pdf_path.suffix.lower() == ".pdf":
        console.print("[red]请提供PDF文件[/red]")
        raise typer.Exit(1)

    from stock_assistant.financial.analyzer import FinancialAnalyzer

    analyzer = FinancialAnalyzer()

    async def _run():
        return await analyzer.analyze_report(
            str(pdf_path), symbol=symbol, report_date=report_date
        )

    with console.status("正在解析财报并分析..."):
        result = asyncio.run(_run())

    console.print()
    console.print(result)


@financial_app.command()
def compare(
    symbols: str = typer.Argument(..., help="股票代码，逗号分隔，如 000001,000002"),
):
    """同行业股票对比"""
    symbol_list = [s.strip() for s in symbols.split(",") if s.strip()]
    if len(symbol_list) < 2:
        console.print("[red]请提供至少两个股票代码进行对比[/red]")
        raise typer.Exit(1)

    from stock_assistant.financial.analyzer import FinancialAnalyzer

    analyzer = FinancialAnalyzer()

    async def _run():
        return await analyzer.compare_stocks(symbol_list)

    with console.status("正在获取数据并生成对比分析..."):
        result = asyncio.run(_run())

    console.print()
    console.print(result)


@financial_app.command()
def metrics(
    symbol: str = typer.Argument(..., help="股票代码"),
    limit: int = typer.Option(50, "--limit", "-n", help="最多显示条数"),
):
    """查看已保存的财务指标"""
    from stock_assistant.core.database import get_session
    from stock_assistant.core.models import FinancialMetric

    session = get_session()
    try:
        rows = (
            session.query(FinancialMetric)
            .filter(FinancialMetric.symbol == symbol)
            .order_by(FinancialMetric.report_date.desc())
            .limit(limit)
            .all()
        )
    finally:
        session.close()

    if not rows:
        console.print(f"[dim]暂无 {symbol} 的财务指标数据[/dim]")
        console.print("[dim]提示: 使用 financial analyze <pdf> --symbol {symbol} 解析财报后自动保存[/dim]")
        return

    table = Table(title=f"{symbol} 财务指标")
    table.add_column("报告期", style="bold")
    table.add_column("指标名称")
    table.add_column("数值", justify="right")
    table.add_column("单位")

    for row in rows:
        table.add_row(
            row.report_date or "-",
            row.metric_name,
            f"{row.value:,.2f}" if row.value is not None else "-",
            row.unit or "-",
        )

    console.print(table)
