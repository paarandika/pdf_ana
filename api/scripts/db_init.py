import sqlite3
import os

DB_NAME = "volumes/pdf_ana.db"
if not os.path.exists("volumes"):
    os.makedirs("volumes")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pdf_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pdf_name TEXT NOT NULL UNIQUE
        );
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == "__main__":
    init_db()
