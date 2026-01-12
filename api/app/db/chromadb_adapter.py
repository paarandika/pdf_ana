import uuid
from typing import List, Dict
import chromadb
from chromadb.config import Settings

from api.app.db import logger
from api.app.util.settings import settings


class ChromaDBAdapter:
    def __init__(
        self,
        vector_db_path: str = settings.vector_db_path,
        collection_name: str = settings.vector_db_collection,
    ):
        self.client = chromadb.PersistentClient(
            path=vector_db_path,
            settings=Settings(
                anonymized_telemetry=False,
            ),
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def insert_pages(self, pages: List[str], filename: str) -> None:
        ids = [str(uuid.uuid4()) for _ in pages]
        print(ids)
        metadatas = [
            {"page": page["metadata"]["page"], "filename": filename} for page in pages
        ]
        docs = [page["text"] for page in pages]
        self.collection.add(
            ids=ids,
            documents=docs,
            metadatas=metadatas,
        )

    def get_pages(self, filename, query, n=2, threshold=10) -> List[Dict]:
        result = self.collection.query(
            query_texts=[query], n_results=n, where={"filename": filename}
        )
        out = []
        for i, id in enumerate(result["ids"][0]):
            if result["distances"][0][i] <= threshold:
                out.append(
                    {
                        "id": id,
                        "text": result["documents"][0][i],
                        "page": result["metadatas"][0][i]["page"],
                        "distance": result["distances"][0][i]
                    }
                )
        return out
