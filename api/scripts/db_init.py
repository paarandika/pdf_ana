import sqlite3
import os

DB_NAME = "volumes/pdf_ana.db"
if not os.path.exists("volumes"):
    os.makedirs("volumes")


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pdf_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pdf_name TEXT NOT NULL UNIQUE
        );
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS compliance_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pdf_id INTEGER NOT NULL,
            compliance_requirement TEXT NOT NULL,
            compliance_state TEXT NOT NULL,
            confidence INTEGER NOT NULL CHECK (confidence >= 0 AND confidence <= 100),
            relevant_quotes TEXT,
            rationale TEXT NOT NULL,
            FOREIGN KEY (pdf_id)
                REFERENCES pdf_files (id)
                ON DELETE CASCADE
        );
    """
    )

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT NOT NULL UNIQUE,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            pdf_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pdf_id)
                REFERENCES pdf_files (id)
                ON DELETE CASCADE
        );
    """
    )

    conn.commit()
    conn.close()
    print("Database initialized successfully.")


if __name__ == "__main__":
    init_db()
