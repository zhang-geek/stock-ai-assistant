"""多Agent协作决策"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from stock_assistant.data.akshare_source import get_data_source
from stock_assistant.llm.base import TaskType
from stock_assistant.llm.router import get_router


@dataclass
class AgentSignal:
    """Agent分析结果"""
    agent_name: str
    signal: str          # buy / sell / hold
    confidence: float    # 0-1
    reasoning: str


class TradingAgent:
    """单个交易Agent基类"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def analyze(self, symbol: str, context: dict) -> AgentSignal:
        """分析并给出交易建议，子类实现"""
        raise NotImplementedError


def _parse_llm_response(agent_name: str, answer: str) -> AgentSignal:
    """解析LLM返回的JSON"""
    import json
    try:
        start = answer.index("{")
        end = answer.rindex("}") + 1
        data = json.loads(answer[start:end])
        signal = data.get("signal", "hold")
        if signal not in ("buy", "sell", "hold"):
            signal = "hold"
        confidence = max(0.0, min(1.0, float(data.get("confidence", 0.5))))
        reasoning = data.get("reasoning", "")
    except (ValueError, json.JSONDecodeError):
        signal, confidence, reasoning = "hold", 0.5, answer[:100]

    return AgentSignal(
        agent_name=agent_name,
        signal=signal,
        confidence=confidence,
        reasoning=reasoning,
    )


class TechnicalAgent(TradingAgent):
    """技术面Agent - 分析价格走势和技术指标"""

    def __init__(self):
        super().__init__("technical", "技术面分析")

    async def analyze(self, symbol: str, context: dict) -> AgentSignal:
        router = get_router()
        quote_info = context.get("quote", "暂无行情数据")

        prompt = (
            f"你是一位A股技术分析专家。请分析股票 {symbol} 的技术面。\n"
            f"当前行情: {quote_info}\n\n"
            "请给出:\n"
            "1. signal: buy / sell / hold (只选一个)\n"
            "2. confidence: 0到1的置信度\n"
            "3. reasoning: 简要分析理由（50字以内）\n\n"
            '严格按JSON格式回复: {"signal": "...", "confidence": 0.x, "reasoning": "..."}'
        )
        answer = await router.ask(prompt, task_type=TaskType.AGENT_REASONING)
        return _parse_llm_response(self.name, answer)


class FundamentalAgent(TradingAgent):
    """基本面Agent - 分析公司基本面"""

    def __init__(self):
        super().__init__("fundamental", "基本面分析")

    async def analyze(self, symbol: str, context: dict) -> AgentSignal:
        router = get_router()
        quote_info = context.get("quote", "暂无行情数据")

        prompt = (
            f"你是一位A股基本面分析专家。请分析股票 {symbol} 的基本面情况。\n"
            f"当前行情: {quote_info}\n\n"
            "请给出:\n"
            "1. signal: buy / sell / hold (只选一个)\n"
            "2. confidence: 0到1的置信度\n"
            "3. reasoning: 简要分析理由（50字以内）\n\n"
            '严格按JSON格式回复: {"signal": "...", "confidence": 0.x, "reasoning": "..."}'
        )
        answer = await router.ask(prompt, task_type=TaskType.AGENT_REASONING)
        return _parse_llm_response(self.name, answer)


class SentimentAgent(TradingAgent):
    """情绪面Agent - 分析市场情绪"""

    def __init__(self):
        super().__init__("sentiment", "情绪面分析")

    async def analyze(self, symbol: str, context: dict) -> AgentSignal:
        router = get_router()
        quote_info = context.get("quote", "暂无行情数据")

        prompt = (
            f"你是一位A股市场情绪分析专家。请分析股票 {symbol} 的市场情绪。\n"
            f"当前行情: {quote_info}\n\n"
            "请给出:\n"
            "1. signal: buy / sell / hold (只选一个)\n"
            "2. confidence: 0到1的置信度\n"
            "3. reasoning: 简要分析理由（50字以内）\n\n"
            '严格按JSON格式回复: {"signal": "...", "confidence": 0.x, "reasoning": "..."}'
        )
        answer = await router.ask(prompt, task_type=TaskType.AGENT_REASONING)
        return _parse_llm_response(self.name, answer)


class RiskAgent(TradingAgent):
    """风控Agent - 评估风险"""

    def __init__(self):
        super().__init__("risk", "风险评估")

    async def analyze(self, symbol: str, context: dict) -> AgentSignal:
        router = get_router()
        quote_info = context.get("quote", "暂无行情数据")
        portfolio_info = context.get("portfolio", "暂无持仓数据")

        prompt = (
            f"你是一位A股风控专家。请评估买入股票 {symbol} 的风险。\n"
            f"当前行情: {quote_info}\n"
            f"当前持仓: {portfolio_info}\n\n"
            "请从仓位集中度、追高风险、市场整体风险等维度评估。\n"
            "请给出:\n"
            "1. signal: buy / sell / hold (只选一个)\n"
            "2. confidence: 0到1的置信度\n"
            "3. reasoning: 简要分析理由（50字以内）\n\n"
            '严格按JSON格式回复: {"signal": "...", "confidence": 0.x, "reasoning": "..."}'
        )
        answer = await router.ask(prompt, task_type=TaskType.AGENT_REASONING)
        return _parse_llm_response(self.name, answer)


# Agent权重
AGENT_WEIGHTS = {
    "technical": 0.30,
    "fundamental": 0.30,
    "sentiment": 0.20,
    "risk": 0.20,
}


async def multi_agent_decision(symbol: str) -> dict:
    """多Agent协作决策

    1. 获取行情数据作为共享上下文
    2. 并发调用所有 Agent 的 analyze()
    3. 加权投票生成最终决策
    """
    # 1. 准备共享上下文
    ds = get_data_source()
    df = ds.get_realtime_quote([symbol])
    quote_info = ""
    if not df.empty:
        row = df.iloc[0]
        quote_info = (
            f"名称: {row['name']}, 价格: {row['price']}, "
            f"涨跌幅: {row['change_pct']:.2f}%"
        )

    # 持仓信息
    from stock_assistant.paper_trading.engine import PaperTradingEngine
    engine = PaperTradingEngine()
    portfolio = engine.get_portfolio()
    portfolio_info = (
        f"总资产: {portfolio['total_value']:.0f}, "
        f"可用现金: {portfolio['cash']:.0f}, "
        f"持仓数: {len(portfolio['positions'])}"
    )

    context = {"quote": quote_info, "portfolio": portfolio_info}

    # 2. 并发调用所有 Agent
    agents: list[TradingAgent] = [
        TechnicalAgent(),
        FundamentalAgent(),
        SentimentAgent(),
        RiskAgent(),
    ]
    signals: list[AgentSignal] = await asyncio.gather(
        *(agent.analyze(symbol, context) for agent in agents)
    )

    # 3. 加权投票
    score_map = {"buy": 1.0, "hold": 0.0, "sell": -1.0}
    weighted_score = 0.0
    total_weight = 0.0

    agent_results = []
    for sig in signals:
        weight = AGENT_WEIGHTS.get(sig.agent_name, 0.25)
        weighted_score += score_map.get(sig.signal, 0) * sig.confidence * weight
        total_weight += weight
        agent_results.append({
            "agent": sig.agent_name,
            "signal": sig.signal,
            "confidence": sig.confidence,
            "reasoning": sig.reasoning,
        })

    # 归一化
    if total_weight > 0:
        weighted_score /= total_weight

    # 确定最终动作
    if weighted_score > 0.2:
        action = "buy"
    elif weighted_score < -0.2:
        action = "sell"
    else:
        action = "hold"

    # 汇总摘要
    summary_parts = [f"{r['agent']}: {r['signal']}({r['confidence']:.0%})" for r in agent_results]
    summary = f"综合得分: {weighted_score:.2f}, 建议: {action} | " + ", ".join(summary_parts)

    return {
        "symbol": symbol,
        "action": action,
        "weighted_score": weighted_score,
        "agents": agent_results,
        "summary": summary,
    }
