import sqlite3
import json
from typing import List

from api.app.db import logger
from api.app.util.settings import settings
from api.app.util.base_classes import ComplianceResponse


class SQLiteDBAdapter:
    def __init__(self, db_path: str = settings.sql_db_path):
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def insert_pdf(self, pdf_name: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO pdf_files (pdf_name) VALUES (?);", (pdf_name,))

        conn.commit()
        conn.close()

    def get_all_pdf_names(self) -> List[str]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT pdf_name FROM pdf_files;")
        rows = cursor.fetchall()

        conn.close()
        return [row[0] for row in rows]

    def insert_compliance_responses(
        self, compliance_responses: ComplianceResponse
    ) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            pdf_name = compliance_responses[0].pdf_name
            cursor.execute(
                "SELECT id FROM pdf_files WHERE pdf_name = ?;",
                (pdf_name,),
            )
            row = cursor.fetchone()
            if row is None:
                logger.error("PDF not found: %s", pdf_name)
                return
            pdf_id = row[0]

            values = [
                (
                    pdf_id,
                    response.compliance_requirement,
                    response.compliance_state,
                    response.confidence,
                    json.dumps(response.relevant_quotes),
                    response.rationale,
                )
                for response in compliance_responses
            ]
            cursor.executemany(
                """
                INSERT INTO compliance_results (
                    pdf_id,
                    compliance_requirement,
                    compliance_state,
                    confidence,
                    relevant_quotes,
                    rationale
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                values,
            )
            conn.commit()
        finally:
            conn.close()
