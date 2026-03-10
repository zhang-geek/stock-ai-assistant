"""CLI入口 - A股AI辅助炒股系统"""

from __future__ import annotations

import asyncio
import sys

import typer
from rich.console import Console
from rich.table import Table

from stock_assistant.core.database import init_db
from stock_assistant.market.commands import market_app
from stock_assistant.sentiment.commands import sentiment_app
from stock_assistant.backtest.commands import backtest_app
from stock_assistant.financial.commands import financial_app
from stock_assistant.style.commands import style_app
from stock_assistant.paper_trading.commands import paper_app

# Windows 终端默认 GBK 编码，Rich 输出 Unicode 字符会报错，强制使用 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")  # noqa: E402
    sys.stderr.reconfigure(encoding="utf-8")  # noqa: E402

app = typer.Typer(name="stock-assistant", help="A股AI辅助炒股系统")
console = Console(force_terminal=True)

# 注册子模块
app.add_typer(market_app, name="market", help="市场监控")
app.add_typer(sentiment_app, name="sentiment", help="舆情监控")
app.add_typer(backtest_app, name="backtest", help="交易回测")
app.add_typer(financial_app, name="financial", help="财报分析")
app.add_typer(style_app, name="style", help="风格探索")
app.add_typer(paper_app, name="paper", help="模拟交易")


@app.callback()
def startup():
    """初始化数据库"""
    init_db()


# ==================== 基础命令 ====================

@app.command()
def quote(symbol: str = typer.Argument(..., help="股票代码，如 000001")):
    """查询实时行情"""
    from stock_assistant.data.akshare_source import get_data_source
    ds = get_data_source()

    with console.status("获取行情数据..."):
        df = ds.get_realtime_quote([symbol])

    if df.empty:
        console.print(f"[red]未找到股票: {symbol}[/red]")
        raise typer.Exit(1)

    row = df.iloc[0]
    color = "red" if row["change_pct"] >= 0 else "green"

    table = Table(title=f"{row['name']} ({row['symbol']})")
    table.add_column("指标", style="bold")
    table.add_column("值", justify="right")

    table.add_row("最新价", f"[{color}]{row['price']:.2f}[/{color}]")
    table.add_row("涨跌幅", f"[{color}]{row['change_pct']:+.2f}%[/{color}]")
    table.add_row("今开", f"{row['open']:.2f}")
    table.add_row("最高", f"{row['high']:.2f}")
    table.add_row("最低", f"{row['low']:.2f}")
    table.add_row("昨收", f"{row['prev_close']:.2f}")
    table.add_row("成交量", f"{row['volume']:,.0f}")
    table.add_row("成交额", f"{row['amount']:,.0f}")

    console.print(table)


@app.command()
def ask(question: str = typer.Argument(..., help="你的问题")):
    """向AI提问关于市场的问题"""
    from stock_assistant.llm.router import get_router

    async def _ask():
        router = get_router()
        providers = router.get_available_providers()
        if not providers:
            console.print("[red]没有可用的LLM。请先配置API Key (.env文件)[/red]")
            raise typer.Exit(1)

        console.print(f"[dim]使用模型: {providers[0]}[/dim]")
        with console.status("AI思考中..."):
            answer = await router.ask(question)
        console.print()
        console.print(answer)

    asyncio.run(_ask())


@app.command()
def index():
    """查看主要指数行情"""
    from stock_assistant.data.akshare_source import get_data_source
    ds = get_data_source()

    with console.status("获取指数数据..."):
        df = ds.get_index_quote()

    table = Table(title="主要指数")
    table.add_column("指数", style="bold")
    table.add_column("最新价", justify="right")
    table.add_column("涨跌幅", justify="right")

    for _, row in df.iterrows():
        color = "red" if row["change_pct"] >= 0 else "green"
        table.add_row(
            row["name"],
            f"{row['price']:.2f}",
            f"[{color}]{row['change_pct']:+.2f}%[/{color}]",
        )

    console.print(table)


@app.command()
def top(
    direction: str = typer.Argument("up", help="up=涨幅榜 down=跌幅榜"),
    n: int = typer.Option(10, "--count", "-n", help="显示条数"),
):
    """查看涨跌幅排行"""
    from stock_assistant.data.akshare_source import get_data_source
    ds = get_data_source()

    with console.status("获取数据..."):
        if direction == "up":
            df = ds.get_top_gainers(n)
            title = f"涨幅榜 TOP {n}"
        else:
            df = ds.get_top_losers(n)
            title = f"跌幅榜 TOP {n}"

    table = Table(title=title)
    table.add_column("代码")
    table.add_column("名称", style="bold")
    table.add_column("价格", justify="right")
    table.add_column("涨跌幅", justify="right")
    table.add_column("成交额", justify="right")
    table.add_column("换手率", justify="right")

    for _, row in df.iterrows():
        color = "red" if row["change_pct"] >= 0 else "green"
        table.add_row(
            str(row["symbol"]),
            str(row["name"]),
            f"{row['price']:.2f}",
            f"[{color}]{row['change_pct']:+.2f}%[/{color}]",
            f"{row['amount'] / 1e8:.1f}亿",
            f"{row['turnover']:.1f}%",
        )

    console.print(table)


@app.command()
def sectors(n: int = typer.Option(20, "--count", "-n", help="显示条数")):
    """查看板块涨跌排行"""
    from stock_assistant.data.akshare_source import get_data_source
    ds = get_data_source()

    with console.status("获取板块数据..."):
        df = ds.get_sector_performance()

    df = df.sort_values("change_pct", ascending=False).head(n)

    table = Table(title=f"板块涨跌幅 TOP {n}")
    table.add_column("板块", style="bold")
    table.add_column("涨跌幅", justify="right")
    table.add_column("上涨", justify="right", style="red")
    table.add_column("下跌", justify="right", style="green")

    for _, row in df.iterrows():
        color = "red" if row["change_pct"] >= 0 else "green"
        table.add_row(
            str(row["sector"]),
            f"[{color}]{row['change_pct']:+.2f}%[/{color}]",
            str(int(row["up_count"])),
            str(int(row["down_count"])),
        )

    console.print(table)


# ==================== 费用管理 ====================

@app.command()
def cost(days: int = typer.Option(30, "--days", "-d", help="统计天数")):
    """查看LLM API费用汇总"""
    from stock_assistant.llm.cost_tracker import get_cost_summary

    summary = get_cost_summary(days)

    if summary["total_calls"] == 0:
        console.print("[dim]暂无API调用记录[/dim]")
        return

    table = Table(title=f"API费用汇总（近{days}天）")
    table.add_column("Provider", style="bold")
    table.add_column("调用次数", justify="right")
    table.add_column("费用(USD)", justify="right")

    for provider, data in summary["by_provider"].items():
        table.add_row(provider, str(data["calls"]), f"${data['cost']:.4f}")

    table.add_section()
    table.add_row(
        "[bold]合计[/bold]",
        str(summary["total_calls"]),
        f"[bold]${summary['total_cost_usd']:.4f}[/bold]",
    )

    console.print(table)


# ==================== 配置引导 ====================

@app.command()
def setup():
    """首次配置引导"""
    from stock_assistant.core.config import PROJECT_ROOT

    env_file = PROJECT_ROOT / ".env"

    console.print("[bold]A股AI助手 - 首次配置[/bold]\n")

    if env_file.exists():
        overwrite = typer.confirm(".env 文件已存在，是否覆盖？", default=False)
        if not overwrite:
            console.print("[dim]跳过配置[/dim]")
            return

    lines = []

    console.print("请输入API Key（可跳过，后续在.env中手动填写）\n")

    deepseek_key = typer.prompt("DeepSeek API Key（推荐，便宜好用）", default="", show_default=False)
    lines.append(f"DEEPSEEK_API_KEY={deepseek_key}")

    claude_key = typer.prompt("Anthropic API Key（可选）", default="", show_default=False)
    lines.append(f"ANTHROPIC_API_KEY={claude_key}")

    openai_key = typer.prompt("OpenAI API Key（可选）", default="", show_default=False)
    lines.append(f"OPENAI_API_KEY={openai_key}")

    lines.append("TUSHARE_TOKEN=")
    lines.append("XUEQIU_COOKIE=")

    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"\n[green]配置已保存到 {env_file}[/green]")

    # 初始化数据库
    init_db()
    console.print("[green]数据库已初始化[/green]")

    # 测试LLM连接
    if deepseek_key or claude_key or openai_key:
        console.print("\n[dim]测试LLM连接...[/dim]")
        # 重载配置
        import stock_assistant.core.config as cfg
        cfg._settings = None

        import stock_assistant.llm.router as router_mod
        router_mod._router = None

        from stock_assistant.llm.router import get_router
        router = get_router()
        providers = router.get_available_providers()
        if providers:
            console.print(f"[green]可用LLM: {', '.join(providers)}[/green]")
        else:
            console.print("[yellow]未检测到可用LLM，请检查API Key[/yellow]")
    else:
        console.print("[yellow]未配置任何API Key，LLM功能暂不可用[/yellow]")

    console.print("\n[bold green]配置完成！[/bold green]")
    console.print("试试以下命令：")
    console.print("  stock-assistant quote 000001    # 查看平安银行行情")
    console.print("  stock-assistant index           # 查看主要指数")
    console.print("  stock-assistant ask '分析一下今天的市场'  # AI问答")


def main():
    app()


if __name__ == "__main__":
    main()
