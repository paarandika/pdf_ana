from typing import List
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse

from api.app.api import logger
from api.app.util.settings import settings
from api.app.db.sqlite_adapter import SQLiteDBAdapter as sql_db_adapter
from api.app.rag.question_chain import QuestionsChain

question_router = APIRouter(prefix="/question")
question_chain = QuestionsChain()
sql_adapter = sql_db_adapter()


@question_router.post("/ask")
async def ask_question(
    uuid: str, question: str, filename: str, background_tasks: BackgroundTasks
):
    async def stream_generator():
        full_answer = ""
        async for chunk in question_chain.invoke(question, filename):
            full_answer += chunk
            yield chunk

        background_tasks.add_task(
            sql_adapter.insert_question, uuid, question, full_answer, filename
        )

    return StreamingResponse(stream_generator(), media_type="text/event-stream")
