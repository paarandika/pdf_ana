# PDF Ana
A simple pdf analyzer capable of analyzing contract PDF files and determine the compliance state.

### Features
* System automatically analyze the compliance status of a contract document.
* Users can ask questions based on the PDF file.
* All the PDF files are stored in a vector DB and only relevant parts are sent to LLM to reduce cost.
* All the questions and answers are saved in a SQL DB.

### Technologies Used
* LLM model: gpt-5-mini deployed via Azure Foundry
* Embedding model:  all-MiniLM-L6-v2 (ChromaDB default)
* SQL DB: SQLite is used in with an adapter configuration. Swappable for a different DB easily.
* Vector DB: ChromaDB is used in with an adapter configuration. Swappable for a different DB easily.
* PDF text extraction: PyMuPDF
* Orchestration framework: LangChain
* UI: Streamlit
* Logging: Python logger with custom config

### Modules

```
PDF_ANA/
├── api/
│   ├── app/
│   │   ├── api/
│   │   ├── db/
│   │   ├── rag/
│   │   ├── util/
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── evaluation/
│   └── test/
│   └── scripts/
├── ui/
│   ├── app.py
│   └── requirements.txt
├── .env
├── .gitignore
├── log_config.yml
└── README.md
```

* api - Contains the backend server and related code
    * app - Backend server and it's modules
        * api - FastAPI routers
        * db - DB adapters for SQLite and ChromaDB
        * rag - Langchain chains
        * util - Utility modules like settings, objects and pdf extractor
        * main.py - FastAPI server
        * scripts - Contains scripts such as db initiation
        * test - Placeholder for Python tests
        * evaluation - Placeholder for evaluation scripts
* ui - Contains the UI code

### ToDo
* Implement evaluation and tests
* Implement user-feedback method
* Improve the UI