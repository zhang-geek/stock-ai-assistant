"""模拟交易 CLI 命令"""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from stock_assistant.paper_trading.engine import PaperTradingEngine

paper_app = typer.Typer()
console = Console(force_terminal=True)


@paper_app.command()
def portfolio():
    """查看模拟投资组合"""
    engine = PaperTradingEngine()
    data = engine.get_portfolio()

    # 账户总览
    color = "red" if data["total_pnl"] >= 0 else "green"
    console.print("\n[bold]模拟交易账户[/bold]")
    console.print(f"  初始资金: {data['capital']:>14,.2f}")
    console.print(f"  可用现金: {data['cash']:>14,.2f}")
    console.print(f"  持仓市值: {data['market_value']:>14,.2f}")
    console.print(f"  总 资 产: {data['total_value']:>14,.2f}")
    console.print(f"  总 盈 亏: [{color}]{data['total_pnl']:>+14,.2f} ({data['pnl_pct']:+.2f}%)[/{color}]")

    # 持仓明细
    positions = data["positions"]
    if not positions:
        console.print("\n[dim]暂无持仓[/dim]")
        return

    table = Table(title="\n持仓明细")
    table.add_column("代码")
    table.add_column("名称", style="bold")
    table.add_column("数量", justify="right")
    table.add_column("成本价", justify="right")
    table.add_column("现价", justify="right")
    table.add_column("市值", justify="right")
    table.add_column("盈亏", justify="right")
    table.add_column("盈亏%", justify="right")

    for p in positions:
        c = "red" if p["pnl"] >= 0 else "green"
        table.add_row(
            p["symbol"],
            p["name"],
            str(p["quantity"]),
            f"{p['entry_price']:.2f}",
            f"{p['current_price']:.2f}",
            f"{p['market_value']:,.2f}",
            f"[{c}]{p['pnl']:+,.2f}[/{c}]",
            f"[{c}]{p['pnl_pct']:+.2f}%[/{c}]",
        )

    console.print(table)


@paper_app.command()
def buy(
    symbol: str = typer.Argument(..., help="股票代码"),
    quantity: int = typer.Option(100, "-q", "--quantity", help="买入数量"),
):
    """手动模拟买入"""
    from stock_assistant.data.akshare_source import get_data_source

    ds = get_data_source()
    with console.status("获取实时价格..."):
        df = ds.get_realtime_quote([symbol])

    if df.empty:
        console.print(f"[red]未找到股票: {symbol}[/red]")
        raise typer.Exit(1)

    row = df.iloc[0]
    price = float(row["price"])
    name = row["name"]

    console.print(f"买入 {name}({symbol}) {quantity}股 @ {price:.2f}，金额: {price * quantity:,.2f}")

    engine = PaperTradingEngine()
    ok = engine.buy(symbol, price, quantity, reasoning="手动买入")
    if ok:
        console.print("[bold green]买入成功[/bold green]")
    else:
        console.print("[bold red]买入失败（资金不足或超过仓位限制）[/bold red]")


@paper_app.command()
def sell(
    symbol: str = typer.Argument(..., help="股票代码"),
    quantity: int = typer.Option(0, "-q", "--quantity", help="卖出数量，0=全部"),
):
    """手动模拟卖出"""
    from stock_assistant.data.akshare_source import get_data_source

    ds = get_data_source()
    with console.status("获取实时价格..."):
        df = ds.get_realtime_quote([symbol])

    if df.empty:
        console.print(f"[red]未找到股票: {symbol}[/red]")
        raise typer.Exit(1)

    row = df.iloc[0]
    price = float(row["price"])
    name = row["name"]
    qty_text = f"{quantity}股" if quantity > 0 else "全部"

    console.print(f"卖出 {name}({symbol}) {qty_text} @ {price:.2f}")

    engine = PaperTradingEngine()
    ok = engine.sell(symbol, price, quantity, reasoning="手动卖出")
    if ok:
        console.print("[bold green]卖出成功[/bold green]")
    else:
        console.print("[bold red]卖出失败（未找到持仓或数量不足）[/bold red]")


@paper_app.command()
def decide(symbol: str = typer.Argument(..., help="股票代码")):
    """AI多Agent协作决策"""
    from stock_assistant.paper_trading.agents import multi_agent_decision

    async def _run():
        with console.status("多Agent分析中..."):
            result = await multi_agent_decision(symbol)

        console.print(f"\n[bold]AI决策分析: {symbol}[/bold]\n")

        # 各Agent结果
        table = Table(title="Agent分析结果")
        table.add_column("Agent", style="bold")
        table.add_column("信号")
        table.add_column("置信度", justify="right")
        table.add_column("理由")

        signal_colors = {"buy": "red", "sell": "green", "hold": "yellow"}
        for a in result["agents"]:
            c = signal_colors.get(a["signal"], "white")
            table.add_row(
                a["agent"],
                f"[{c}]{a['signal']}[/{c}]",
                f"{a['confidence']:.0%}",
                a["reasoning"],
            )

        console.print(table)

        # 最终决策
        action_color = signal_colors.get(result["action"], "white")
        console.print(f"\n综合得分: {result['weighted_score']:+.2f}")
        console.print(f"最终建议: [{action_color}][bold]{result['action'].upper()}[/bold][/{action_color}]")

    asyncio.run(_run())


@paper_app.command()
def history(n: int = typer.Option(20, "-n", "--count", help="显示条数")):
    """查看交易历史"""
    engine = PaperTradingEngine()
    records = engine.get_history(n)

    if not records:
        console.print("[dim]暂无交易记录[/dim]")
        return

    table = Table(title=f"最近 {n} 条交易记录")
    table.add_column("时间")
    table.add_column("代码")
    table.add_column("操作")
    table.add_column("价格", justify="right")
    table.add_column("数量", justify="right")
    table.add_column("金额", justify="right")
    table.add_column("理由")

    for r in records:
        action_color = "red" if r["action"] == "buy" else "green"
        ts = r["timestamp"].strftime("%m-%d %H:%M") if r["timestamp"] else ""
        table.add_row(
            ts,
            r["symbol"],
            f"[{action_color}]{r['action']}[/{action_color}]",
            f"{r['price']:.2f}",
            str(r["quantity"]),
            f"{r['price'] * r['quantity']:,.2f}",
            r["reasoning"][:30] if r["reasoning"] else "",
        )

    console.print(table)
