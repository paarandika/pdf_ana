import os
import pymupdf4llm
from typing import List, Union

from api.app.util import logger
from api.app.util.settings import settings


class PDFExtractor:
    def __init__(self, margin: List[float] = [0, 0]) -> None:
        self.ouput_folder = settings.pdf_text_output
        self.margin = margin

    def extract_pages(
        self,
        document_path: str,
    ) -> Union[List, str] | None:
        text_dir = self._create_doc_env(document_path)
        if not text_dir:
            return None
        try:
            md_text = pymupdf4llm.to_markdown(
                document_path,
                page_chunks="text",
                ignore_images=True,
            )
        except Exception as e:
            logger.error("Exception while extracting: %s", document_path)
            return [], text_dir

        for i, page in enumerate(md_text):
            with open(os.path.join(text_dir, f"{i}.txt"), "w") as f:
                f.write(page["text"])
        return md_text, text_dir

    def _create_doc_env(self, document: str) -> str:
        _, file_name = os.path.split(document)
        doc_output = os.path.join(self.ouput_folder, file_name)
        if os.path.exists(doc_output):
            logger.info("Document folder %s exists", doc_output)
            return None
        os.mkdir(doc_output)
        return doc_output
