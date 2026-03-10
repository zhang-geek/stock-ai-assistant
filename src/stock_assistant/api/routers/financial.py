"""财报分析 API"""

import tempfile

from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from stock_assistant.financial.analyzer import FinancialAnalyzer

router = APIRouter()


@router.post("/analyze")
async def analyze_report(
    file: UploadFile,
    symbol: str = "",
    report_date: str = "",
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    analyzer = FinancialAnalyzer()
    result = await analyzer.analyze_report(tmp_path, symbol=symbol, report_date=report_date)
    return {"data": result}


class CompareRequest(BaseModel):
    symbols: list[str]


@router.post("/compare")
async def compare_stocks(req: CompareRequest):
    analyzer = FinancialAnalyzer()
    result = await analyzer.compare_stocks(req.symbols)
    return {"data": result}
