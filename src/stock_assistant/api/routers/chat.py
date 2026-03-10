"""AI问答 API"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from stock_assistant.api.deps import get_llm
from stock_assistant.llm.base import Message, TaskType

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    system: str = "你是一个专业的A股投资助手。"


@router.post("/ask")
async def ask(req: AskRequest):
    llm = get_llm()
    result = await llm.ask(req.question, system=req.system, task_type=TaskType.GENERAL)
    return {"data": result}


@router.post("/stream")
async def stream_chat(req: AskRequest):
    llm = get_llm()
    messages = [
        Message(role="system", content=req.system),
        Message(role="user", content=req.question),
    ]

    async def event_generator():
        async for chunk in llm.stream(messages, task_type=TaskType.GENERAL):
            yield f"data: {chunk}\n\n"
        done_marker = "[DONE]"
        yield f"data: {done_marker}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
