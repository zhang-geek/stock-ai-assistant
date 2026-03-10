"""交易回测 API"""

import tempfile

from fastapi import APIRouter, UploadFile

from stock_assistant.backtest.analyzer import TradeAnalyzer
from stock_assistant.backtest.importer import TradeImporter

router = APIRouter()


@router.get("/statistics")
def get_statistics():
    analyzer = TradeAnalyzer()
    stats = analyzer.get_statistics()
    return {"data": stats}


@router.get("/ai-analysis")
async def ai_analysis():
    analyzer = TradeAnalyzer()
    stats = analyzer.get_statistics()
    result = await analyzer.ai_analysis(stats)
    return {"data": result}


@router.post("/import")
async def import_csv(file: UploadFile, broker: str = "generic"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    importer = TradeImporter()
    count = importer.import_csv(tmp_path, broker=broker)
    return {"imported": count}
