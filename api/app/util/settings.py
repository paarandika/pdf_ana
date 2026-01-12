import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from api.app.util import logger


class Settings(BaseSettings):
    """
    Application settings.
    Most values are loaded from the env file
    """
    log_level: str
    openai_api: str

    upload_dir: str = "storage/pdf_files"
    if not os.path.exists(upload_dir):
        logger.info("Upload dir %s not fount. Creating one." % upload_dir)
        os.makedirs(upload_dir)
    
    pdf_text_output: str = "storage/pdf_text_output"
    if not os.path.exists(pdf_text_output):
        logger.info("PDF text output dir %s not fount. Creating one." % pdf_text_output)
        os.makedirs(pdf_text_output)

    sql_db_path: str = "volumes/pdf_ana.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()