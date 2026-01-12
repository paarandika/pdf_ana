import sqlite3
from typing import List

from api.app.db import logger
from api.app.util.settings import settings

class SQLiteDBAdapter:
    def __init__(self, db_path: str = settings.db_path):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def insert_pdf(self, pdf_name: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO pdf_files (pdf_name) VALUES (?);",
            (pdf_name,)
        )

        conn.commit()
        conn.close()

    def get_all_pdf_names(self) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT pdf_name FROM pdf_files;")
        rows = cursor.fetchall()

        conn.close()
        return [row[0] for row in rows]
