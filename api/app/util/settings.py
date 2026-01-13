import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Any

from api.app.util import logger


class Settings(BaseSettings):
    """
    Application settings.
    Most values are loaded from the env file
    """

    upload_dir: str = "storage/pdf_files"
    pdf_text_output: str = "storage/pdf_text_output"

    sql_db_path: str = "volumes/pdf_ana.db"
    vector_db_path: str = "volumes"
    vector_db_collection: str = "pdf_chunks"

    dir_list: List[str] = [upload_dir, pdf_text_output, vector_db_path]

    azure_endpoint: str
    azure_endpoint: str
    azure_deployment: str
    azure_api_version: str
    azure_api_key: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    def model_post_init(self, __context: Any) -> None:
        for dir in self.dir_list:
            if not os.path.exists(dir):
                logger.info("Dir: %s not found. Creating it.",dir)
                os.makedirs(dir)


settings = Settings()
