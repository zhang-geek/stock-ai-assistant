"""券商交易记录CSV导入"""

from __future__ import annotations


import pandas as pd

from stock_assistant.core.database import get_session
from stock_assistant.core.models import Trade


class TradeImporter:
    """导入券商交易记录"""

    COLUMN_MAPS = {
        "generic": {
            "symbol": "股票代码",
            "name": "股票名称",
            "direction": "买卖方向",
            "price": "成交价格",
            "quantity": "成交数量",
            "commission": "手续费",
            "trade_time": "成交时间",
        },
    }

    DIRECTION_MAP = {
        "买入": "buy",
        "卖出": "sell",
        "买": "buy",
        "卖": "sell",
    }

    def import_csv(self, file_path: str, broker: str = "generic") -> int:
        """导入CSV文件到数据库，返回导入条数"""
        col_map = self.COLUMN_MAPS.get(broker)
        if col_map is None:
            raise ValueError(f"不支持的券商格式: {broker}")

        # 自动检测编码
        df = self._read_csv(file_path)

        # 映射列名: 中文 → 英文
        reverse_map = {v: k for k, v in col_map.items()}
        df = df.rename(columns=reverse_map)

        # 标准化方向
        df["direction"] = df["direction"].map(self.DIRECTION_MAP)
        if df["direction"].isna().any():
            bad = df.loc[df["direction"].isna(), "direction"].tolist()
            raise ValueError(f"无法识别的买卖方向: {bad}")

        # 类型转换
        df["price"] = pd.to_numeric(df["price"])
        df["quantity"] = pd.to_numeric(df["quantity"]).astype(int)
        df["commission"] = pd.to_numeric(df["commission"], errors="coerce").fillna(0)
        df["trade_time"] = pd.to_datetime(df["trade_time"])
        df["symbol"] = df["symbol"].astype(str).str.zfill(6)

        # 计算成交金额
        df["amount"] = df["price"] * df["quantity"]

        # 写入数据库
        session = get_session()
        try:
            for _, row in df.iterrows():
                trade = Trade(
                    symbol=row["symbol"],
                    name=row.get("name", ""),
                    direction=row["direction"],
                    price=float(row["price"]),
                    quantity=int(row["quantity"]),
                    amount=float(row["amount"]),
                    fee=float(row["commission"]),
                    trade_time=row["trade_time"],
                    broker_source=broker,
                )
                session.add(trade)
            session.commit()
            return len(df)
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def _read_csv(file_path: str) -> pd.DataFrame:
        """自动检测编码读取CSV"""
        for encoding in ["utf-8", "gbk", "gb2312", "utf-8-sig"]:
            try:
                return pd.read_csv(file_path, encoding=encoding)
            except (UnicodeDecodeError, UnicodeError):
                continue
        raise ValueError(f"无法识别文件编码: {file_path}")
