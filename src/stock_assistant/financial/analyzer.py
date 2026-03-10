"""财报分析器 - 结合PDF解析和LLM进行深度分析"""

from __future__ import annotations

import re

from stock_assistant.core.database import get_session
from stock_assistant.core.models import FinancialMetric
from stock_assistant.financial.pdf_parser import FinancialReportParser
from stock_assistant.llm.base import TaskType
from stock_assistant.llm.router import get_router


# LLM 输入文本最大字符数（避免超出上下文窗口）
_MAX_TEXT_LEN = 60_000


class FinancialAnalyzer:
    """财报分析器"""

    def __init__(self):
        self._parser = FinancialReportParser()

    # ------------------------------------------------------------------
    # 财报PDF分析
    # ------------------------------------------------------------------

    async def analyze_report(
        self,
        pdf_path: str,
        symbol: str = "",
        report_date: str = "",
    ) -> str:
        """分析财报PDF

        Args:
            pdf_path: PDF文件路径
            symbol: 股票代码（可选，用于保存指标）
            report_date: 报告期（如 2024-12-31），可选

        Returns:
            LLM生成的分析文本
        """
        # 1. 提取文本
        text = self._parser.extract_text(pdf_path, max_pages=30)
        if not text.strip():
            return "无法从PDF中提取到有效文本，请确认文件是否为可解析的财报PDF。"

        # 2. 提取关键指标
        metrics = self._parser.extract_key_metrics(text)

        # 3. 保存到数据库
        if symbol:
            self._save_metrics(symbol, report_date or "unknown", metrics)

        # 4. 截断文本防止超长
        truncated = text[:_MAX_TEXT_LEN]
        if len(text) > _MAX_TEXT_LEN:
            truncated += "\n\n...（文本已截断）"

        # 5. 构建 prompt 发给 LLM
        metrics_text = "\n".join(f"- {k}: {v}" for k, v in metrics.items())
        prompt = (
            "请分析以下上市公司财报，从以下维度给出专业分析：\n"
            "1. 经营状况总结\n"
            "2. 盈利能力分析\n"
            "3. 成长性评估\n"
            "4. 财务健康度（资产负债、现金流等）\n"
            "5. 主要风险点\n"
            "6. 投资建议（仅供参考）\n\n"
        )
        if metrics_text:
            prompt += f"已提取的关键指标：\n{metrics_text}\n\n"
        prompt += f"财报原文（节选）：\n{truncated}"

        router = get_router()
        result = await router.ask(
            prompt,
            system="你是一名资深A股财务分析师，擅长解读上市公司财报。请用中文回答。",
            task_type=TaskType.FINANCIAL_ANALYSIS,
        )
        return result

    # ------------------------------------------------------------------
    # 同行业股票对比
    # ------------------------------------------------------------------

    async def compare_stocks(self, symbols: list[str]) -> str:
        """同行业股票对比分析

        Args:
            symbols: 股票代码列表

        Returns:
            LLM生成的对比分析文本
        """
        # 1. 从数据库读取已有指标
        session = get_session()
        try:
            all_data: dict[str, list[FinancialMetric]] = {}
            for sym in symbols:
                rows = (
                    session.query(FinancialMetric)
                    .filter(FinancialMetric.symbol == sym)
                    .order_by(FinancialMetric.report_date.desc())
                    .all()
                )
                if rows:
                    all_data[sym] = rows
        finally:
            session.close()

        # 2. 数据库没有数据时，尝试从 AKShare 获取基本面
        missing = [s for s in symbols if s not in all_data]
        akshare_info: dict[str, dict] = {}
        if missing:
            try:
                from stock_assistant.data.akshare_source import get_data_source
                ds = get_data_source()
                for sym in missing:
                    try:
                        info = ds.get_stock_info(sym)
                        akshare_info[sym] = info
                    except Exception:
                        pass
            except Exception:
                pass

        # 3. 组装对比文本
        sections = []
        for sym in symbols:
            lines = [f"## {sym}"]
            if sym in all_data:
                # 取最新报告期的数据
                latest_date = all_data[sym][0].report_date
                for m in all_data[sym]:
                    if m.report_date == latest_date:
                        unit_str = f" ({m.unit})" if m.unit else ""
                        lines.append(f"- {m.metric_name}: {m.value}{unit_str}  [报告期: {m.report_date}]")
            if sym in akshare_info:
                for k, v in akshare_info[sym].items():
                    lines.append(f"- {k}: {v}")
            if len(lines) == 1:
                lines.append("- 暂无数据")
            sections.append("\n".join(lines))

        compare_text = "\n\n".join(sections)

        prompt = (
            "请对以下A股股票进行同行业对比分析：\n\n"
            f"{compare_text}\n\n"
            "请从以下维度对比：\n"
            "1. 盈利能力\n"
            "2. 成长性\n"
            "3. 估值水平\n"
            "4. 财务健康度\n"
            "5. 综合评价与排名建议（仅供参考）"
        )

        router = get_router()
        result = await router.ask(
            prompt,
            system="你是一名资深A股财务分析师，擅长行业对比研究。请用中文回答。",
            task_type=TaskType.FINANCIAL_ANALYSIS,
        )
        return result

    # ------------------------------------------------------------------
    # 内部方法
    # ------------------------------------------------------------------

    def _save_metrics(
        self, symbol: str, report_date: str, metrics: dict[str, str]
    ) -> None:
        """将提取的指标保存到 FinancialMetric 表"""
        session = get_session()
        try:
            for name, raw_value in metrics.items():
                # 尝试解析纯数字部分
                num_match = re.search(r"(-?[0-9.]+)", raw_value)
                value = float(num_match.group(1)) if num_match else None

                # 提取单位
                unit = raw_value
                if num_match:
                    unit = raw_value[num_match.end():].strip() or None
                else:
                    unit = None

                metric = FinancialMetric(
                    symbol=symbol,
                    report_date=report_date,
                    metric_name=name,
                    value=value,
                    unit=unit,
                )
                session.add(metric)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
