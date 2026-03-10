"""舆情监控 CLI 命令"""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.table import Table

sentiment_app = typer.Typer(help="舆情监控")
console = Console(force_terminal=True)


@sentiment_app.command()
def scan(
    symbol: str = typer.Argument(..., help="股票代码，如 000001"),
    limit: int = typer.Option(20, "--limit", "-n", help="抓取条数"),
):
    """扫描个股舆情"""
    from stock_assistant.sentiment.scraper import fetch_posts
    from stock_assistant.sentiment.analyzer import SentimentAnalyzer

    async def _run():
        with console.status(f"正在抓取 {symbol} 的舆情数据..."):
            posts = await fetch_posts(symbol, limit)

        if not posts:
            console.print(f"[yellow]未抓取到 {symbol} 的舆情数据[/yellow]")
            raise typer.Exit(1)

        console.print(f"[dim]抓取到 {len(posts)} 条帖子，正在分析情感...[/dim]")

        analyzer = SentimentAnalyzer()
        with console.status("LLM 情感分析中..."):
            results = await analyzer.analyze_posts(posts, symbol)

        # 保存到数据库
        saved = analyzer.save_to_db(results, symbol)
        console.print(f"[dim]已保存 {saved} 条记录到数据库[/dim]\n")

        # 展示结果
        _display_results(results, symbol)

    asyncio.run(_run())


@sentiment_app.command()
def daily(
    symbol: str = typer.Option(None, "--symbol", "-s", help="指定股票代码，不指定则汇总全部"),
):
    """每日舆情汇总"""
    from stock_assistant.sentiment.analyzer import SentimentAnalyzer

    async def _run():
        analyzer = SentimentAnalyzer()
        with console.status("生成舆情简报..."):
            summary = await analyzer.daily_summary(symbol)

        title = f"{symbol} 每日舆情简报" if symbol else "每日舆情简报"
        console.print(f"\n[bold]{title}[/bold]\n")
        console.print(summary)

    asyncio.run(_run())


@sentiment_app.command()
def kol():
    """查看已追踪的KOL观点"""
    from stock_assistant.core.database import get_session
    from stock_assistant.core.models import KOLOpinion

    session = get_session()
    try:
        opinions = (
            session.query(KOLOpinion)
            .order_by(KOLOpinion.created_at.desc())
            .limit(20)
            .all()
        )
    finally:
        session.close()

    if not opinions:
        console.print("[dim]暂无KOL观点记录[/dim]")
        return

    table = Table(title="KOL观点追踪")
    table.add_column("大V", style="bold")
    table.add_column("平台")
    table.add_column("股票")
    table.add_column("信号", justify="center")
    table.add_column("置信度", justify="right")
    table.add_column("观点")

    for op in opinions:
        signal_color = {
            "bullish": "red",
            "bearish": "green",
            "neutral": "dim",
        }.get(op.signal or "", "dim")

        signal_text = {
            "bullish": "看多",
            "bearish": "看空",
            "neutral": "中性",
        }.get(op.signal or "", op.signal or "")

        confidence = f"{op.confidence:.0%}" if op.confidence else "-"
        opinion_text = (op.opinion[:40] + "...") if len(op.opinion) > 40 else op.opinion

        table.add_row(
            op.kol_name,
            op.platform,
            op.symbol or "-",
            f"[{signal_color}]{signal_text}[/{signal_color}]",
            confidence,
            opinion_text,
        )

    console.print(table)


def _display_results(results: list[dict], symbol: str) -> None:
    """用 Rich Table 展示舆情分析结果"""
    table = Table(title=f"{symbol} 舆情分析")
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("标题", max_width=50)
    table.add_column("作者", style="dim", width=10)
    table.add_column("情感", justify="center", width=6)
    table.add_column("分数", justify="right", width=6)

    for i, post in enumerate(results, 1):
        label = post.get("sentiment_label", "中性")
        score = post.get("sentiment_score", 0.0)

        if label == "利好":
            label_styled = "[red]利好[/red]"
        elif label == "利空":
            label_styled = "[green]利空[/green]"
        else:
            label_styled = "[dim]中性[/dim]"

        score_color = "red" if score > 0 else ("green" if score < 0 else "dim")
        title = post["title"]
        if len(title) > 48:
            title = title[:48] + "..."

        table.add_row(
            str(i),
            title,
            post.get("author", "")[:10],
            label_styled,
            f"[{score_color}]{score:+.1f}[/{score_color}]",
        )

    console.print(table)

    # 汇总统计
    total = len(results)
    positive = sum(1 for r in results if r.get("sentiment_label") == "利好")
    negative = sum(1 for r in results if r.get("sentiment_label") == "利空")
    neutral = total - positive - negative
    avg_score = sum(r.get("sentiment_score", 0) for r in results) / total if total else 0

    console.print(
        f"\n[bold]汇总:[/bold] 共 {total} 条 | "
        f"[red]利好 {positive}[/red] | "
        f"[green]利空 {negative}[/green] | "
        f"[dim]中性 {neutral}[/dim] | "
        f"平均分: {avg_score:+.2f}"
    )
