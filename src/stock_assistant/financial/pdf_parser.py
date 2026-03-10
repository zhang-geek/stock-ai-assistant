"""财报PDF解析器"""

from __future__ import annotations

import re

import pdfplumber


class FinancialReportParser:
    """财报PDF解析器，提取文本、表格和关键财务指标"""

    def extract_text(self, pdf_path: str, max_pages: int = 30) -> str:
        """提取PDF文本内容

        Args:
            pdf_path: PDF文件路径
            max_pages: 最多提取页数，默认30页

        Returns:
            合并后的文本内容
        """
        pages_text = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= max_pages:
                    break
                text = page.extract_text()
                if text:
                    pages_text.append(text)
        return "\n\n".join(pages_text)

    def extract_tables(self, pdf_path: str, max_pages: int = 30) -> list[list]:
        """提取PDF中的表格

        Args:
            pdf_path: PDF文件路径
            max_pages: 最多提取页数

        Returns:
            表格列表，每个表格是行的列表
        """
        all_tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                if i >= max_pages:
                    break
                tables = page.extract_tables()
                if tables:
                    all_tables.extend(tables)
        return all_tables

    def extract_key_metrics(self, text: str) -> dict[str, str]:
        """从文本中提取关键财务指标

        使用正则匹配常见的财务指标数值。

        Args:
            text: PDF提取的文本内容

        Returns:
            {指标名: 数值字符串}
        """
        patterns = {
            "营业收入": r"营业收入[：:\s]*([0-9,.]+)\s*(万元|亿元|元)",
            "营业成本": r"营业成本[：:\s]*([0-9,.]+)\s*(万元|亿元|元)",
            "净利润": r"净利润[：:\s]*([0-9,.]+)\s*(万元|亿元|元)",
            "归母净利润": r"归属于母公司.*?净利润[：:\s]*([0-9,.]+)\s*(万元|亿元|元)",
            "扣非净利润": r"扣除非经常性损益.*?净利润[：:\s]*([0-9,.]+)\s*(万元|亿元|元)",
            "毛利率": r"毛利率[：:\s]*([0-9,.]+)\s*%",
            "净利率": r"净利率[：:\s]*([0-9,.]+)\s*%",
            "ROE": r"(?:加权平均)?净资产收益率[：:\s]*([0-9,.]+)\s*%",
            "资产负债率": r"资产负债率[：:\s]*([0-9,.]+)\s*%",
            "总资产": r"总资产[：:\s]*([0-9,.]+)\s*(万元|亿元|元)",
            "净资产": r"(?:归属于母公司.*?)?(?:所有者权益|净资产)[：:\s]*([0-9,.]+)\s*(万元|亿元|元)",
            "经营活动现金流": r"经营活动产生的现金流量净额[：:\s]*(-?[0-9,.]+)\s*(万元|亿元|元)",
            "每股收益": r"(?:基本)?每股收益[：:\s]*([0-9,.]+)\s*元",
            "营业收入同比": r"营业收入.*?同比.*?([0-9,.]+)\s*%",
            "净利润同比": r"净利润.*?同比.*?([0-9,.]+)\s*%",
        }

        metrics = {}
        for name, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                value = match.group(1).replace(",", "")
                # 带单位的指标把单位也拼上
                if match.lastindex and match.lastindex >= 2:
                    value = f"{value}{match.group(2)}"
                elif name in ("毛利率", "净利率", "ROE", "资产负债率", "营业收入同比", "净利润同比"):
                    value = f"{value}%"
                elif name == "每股收益":
                    value = f"{value}元"
                metrics[name] = value

        return metrics
