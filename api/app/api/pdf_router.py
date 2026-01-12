import shutil
import os
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from api.app.api import logger
from api.app.util.settings import settings
from api.app.db.db_adapter import SQLiteDBAdapter as sql_db_adapter
from api.app.util.pdf_extractor import PDFExtractor

pdf_router = APIRouter(prefix="/pdf")
sql_adapter = sql_db_adapter()
pdf_extractor = PDFExtractor()


@pdf_router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    logger.debug("PDF upload")
    if file.content_type != "application/pdf":
        logger.error("Non-pdf file recieved: %s" % file.filename)
        return JSONResponse(
            status_code=400, content={"message": "Only PDF files are allowed."}
        )

    file_location = os.path.join(settings.upload_dir, file.filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.debug("PDF upload successful")

    pages, path = pdf_extractor.extract_pages(os.path.join(file_location))
    if pages is None:
        logger.error("PDF: %s already exists" % file.filename)
        return JSONResponse(status_code=400, content={"message": "PDF already exists"})
    if len(pages) == 0:
        logger.error("PDF: %s is mpty or invalid" % file.filename)
        return JSONResponse(
            status_code=400, content={"message": "Empty or invalid PDF"}
        )
    sql_adapter.insert_pdf(file.filename)
    return {"filename": file.filename}
