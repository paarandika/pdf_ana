from typing import Dict
from operator import itemgetter
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnableLambda,
)
from langchain_core.output_parsers import StrOutputParser

from api.app.db import logger
from api.app.util.settings import settings
from api.app.util.base_classes import ComplianceAnswer, ComplianceResponse
from api.app.db.chromadb_adapter import ChromaDBAdapter as vector_db_adapter


class QuestionsChain:

    def __init__(self):
        self.vector_adapter = vector_db_adapter()
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_endpoint,
            azure_deployment=settings.azure_deployment,
            api_version=settings.azure_api_version,
            api_key=settings.azure_api_key,
            max_completion_tokens=12000,
            # temperature=0.4,
            max_retries=1,
        )
        self.prompt = ChatPromptTemplate.from_template(
            """You are an expert compliance analyst. Given relevant pages from a contract and a question, answer the question based on the contract.
            **Strictly adhere to the provided documents**

            Question: {question}

            Contract pages: {pages}"""
        )
        pages = RunnableLambda(self._context_retriever)
        self.chain = RunnableParallel(
            {
                "pages": pages,
                "question": itemgetter("question"),
            }
        ) | self.prompt | self.llm | StrOutputParser()

    def _context_retriever(self, data: Dict) -> str:
        filename = data["filename"]
        query = data["question"]
        page_list = self.vector_adapter.get_pages(filename, query, n=5)

        logger.info("Number of pages for file %s: %d", filename, len(page_list))
        logger.debug("Chunk ids: %s", " ,".join([page["id"] for page in page_list]))
        logger.debug(
            "Chunk distances: %s", " ,".join([page["id"] for page in page_list])
        )

        out = [page["text"] for page in page_list]
        return "\n\n".join(out)

    def invoke(self, question: str, filename: str):
        return self.chain.astream({"question": question, "filename": filename})
