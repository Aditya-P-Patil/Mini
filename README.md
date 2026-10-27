# FolioAI Financial Research Assistant

FolioAI is an evidence-backed financial research workspace. The existing
FastAPI application remains the source of truth for PDF extraction, chunking,
Gemini embeddings, pgvector retrieval, RAG answers, and structured financial
analysis. A separate Next.js App Router frontend provides the research UI.

## Repository structure

```text
Mini/
├── app/                         # FastAPI backend (preserved layout)
│   ├── main.py
│   ├── models.py
│   ├── services/
│   └── financial_intelligence/
├── frontend/                    # Independently deployable Next.js app
│   ├── app/
│   ├── components/
│   └── lib/api.js
├── data/
├── sample_reports/
└── tests/
```

The backend was not moved into `backend/`: keeping its current import paths
avoids breaking the working application and test suite.

## Environment

Create a root `.env` from [.env.example](./.env.example):

```dotenv
DATABASE_URL=postgresql+psycopg://user:password@host:5432/postgres
GEMINI_API_KEY=your_gemini_api_key
FRONTEND_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Create `frontend/.env.local` from [frontend/.env.example](./frontend/.env.example):

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

Never put `DATABASE_URL` or `GEMINI_API_KEY` in the frontend environment.

### Supabase setup

This project uses Supabase as a PostgreSQL provider through `DATABASE_URL`;
it does not use the Supabase browser client or REST API. The Supabase project
URL by itself is not a database connection string and should not be placed in
`NEXT_PUBLIC_API_BASE_URL`. In the Supabase dashboard, copy the PostgreSQL
connection string from **Connect → ORMs → SQLAlchemy**, then set it as
`DATABASE_URL` in the root `.env`. Keep the password encoded if it contains
special URL characters.

No Supabase service-role key is required for the current database-only setup.

## Run locally

### Windows PowerShell — backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Windows PowerShell — frontend

```powershell
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Open `http://localhost:3000`. API documentation is available at
`http://127.0.0.1:8000/docs`.

## Data workflow

PDF upload intentionally does not claim that a document is searchable. The
frontend executes the real sequence:

1. `POST /documents/upload` extracts and stores PDF pages.
2. `POST /documents/{document_id}/chunk` creates text chunks.
3. `POST /documents/{document_id}/embed` generates Gemini embeddings and saves
   them to pgvector.
4. `POST /rag/ask` retrieves embedded chunks and generates a cited answer.

The embedding step requires `GEMINI_API_KEY`. Existing documents can be
chunked and embedded from the API documentation if they were uploaded before
this integration.

## API additions

- `POST /documents/{document_id}/embed` embeds pending chunks for one document.
- `GET /conversations` returns persisted RAG conversations.
- `POST /rag/ask` now stores the returned question and answer in the
  `conversations` table and returns `conversation_id`.

The application still uses SQLAlchemy `create_all` on startup, consistent with
the existing project. It does not drop, reset, or migrate existing tables
destructively. For production, introduce a versioned migration tool before
changing schema further.

## Verification

From the repository root:

```powershell
python -m compileall app
python -m pytest -q
```

From `frontend/`:

```powershell
npm install
npm run build
```

The live PDF/RAG flow additionally requires a reachable PostgreSQL database,
the pgvector extension, a Gemini key, and a document containing extractable
text. Deployment platforms with ephemeral disks should use durable object
storage for uploaded PDFs; this implementation currently stores extracted
content in PostgreSQL and does not claim durable original-file storage.
