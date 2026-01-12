import logging
from fastapi import FastAPI

from api.app.util.settings import settings
from api.app.api.pdf_router import pdf_router

logger = logging.getLogger("api." + __name__)

app = FastAPI(title="PDF Ana")
app.include_router(pdf_router, prefix="/api")