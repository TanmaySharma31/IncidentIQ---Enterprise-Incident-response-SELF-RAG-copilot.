# IncidentIQ Self-RAG Copilot

IncidentIQ is a cloud-operations incident response assistant built with FastAPI, LangGraph, Google Gemini, Pinecone, and Tavily. It retrieves relevant internal runbooks, evaluates whether the retrieved context supports an answer, optionally rewrites the query or searches the web, and returns an answer with source and trace information.

The application includes:

- A browser-based chat interface for incident questions.
- Self-RAG routing with retrieval, support checking, query rewriting, and optional web search.
- Pinecone-backed vector retrieval for internal runbooks and uploaded documents.
- Gemini generation and embeddings.
- Upload and ingestion support for PDF, TXT, Markdown, and DOCX files.
- SQLite audit history for chat requests and responses.
- Docker support with secrets supplied at runtime rather than copied into the image.

## Requirements

Choose one of these runtime options:

- **Conda/local:** Conda, Python 3.11 or newer, and the dependencies in `requirements.txt`.
- **Docker:** Docker Desktop or another Docker Engine installation.

The application also requires credentials for the external services used by the selected features:

- Google Gemini for chat responses and embeddings.
- Pinecone for vector storage and retrieval.
- Tavily for web search when the Self-RAG workflow decides internal context is insufficient.

## Configuration

Create a local `.env` file in the repository root. Keep this file private. It is excluded by both `.gitignore` and `.dockerignore`.

```dotenv
GEMINI_API_KEY=your-gemini-api-key
PINECONE_API_KEY=your-pinecone-api-key
TAVILY_API_KEY=your-tavily-api-key

PINECONE_INDEX_NAME=incidentiq-gemini-self-rag
PINECONE_NAMESPACE=incident-runbooks
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
```

Optional settings and their defaults:

| Variable | Default | Purpose |
| --- | --- | --- |
| `LLM_MODEL` | `gemini-3.6-flash` | Gemini model used to generate answers |
| `EMBEDDING_MODEL` | `gemini-embedding-001` | Gemini embedding model |
| `EMBEDDING_DIMENSION` | `768` | Pinecone index vector dimension |
| `MAX_OUTPUT_TOKENS` | `512` | Maximum generated response length |
| `MAX_DOCUMENT_CHARS` | `3500` | Maximum document text processed per ingestion unit |
| `TOP_K` | `3` | Number of Pinecone matches retrieved |
| `MAX_SUPPORT_RETRIES` | `1` | Support-check retries |
| `MAX_RETRIEVAL_REWRITES` | `1` | Retrieval query rewrites |
| `MAX_WEB_REWRITES` | `1` | Web-search query rewrites |
| `DATABASE_PATH` | `data/audit.db` | SQLite audit database path |

The Pinecone index is created automatically when the application first needs it. Its dimension must match `EMBEDDING_DIMENSION`; use a new index name or recreate the index if the dimension changes.

## Run With Conda

The project environment in this workspace is named `project`. Create it if necessary:

```powershell
conda create -n project python=3.12 -y
```

Install the dependencies:

```powershell
conda run -n project python -m pip install -r requirements.txt
```

Start the server:

```powershell
conda run -n project python -m uvicorn app:app --host 127.0.0.1 --port 8080
```

Open [http://localhost:8080](http://localhost:8080). The health endpoint is available at [http://localhost:8080/api/health](http://localhost:8080/api/health).

For an activated environment, the equivalent commands are:

```powershell
conda activate project
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8080
```

## Run With Docker

Build the image from the repository root:

```powershell
docker build -t incidentiq:first-version .
```

Run the container with secrets injected at runtime:

```powershell
docker run -d --name incidentiq -p 8080:8080 `
	--env-file .env `
	-v "${PWD}\data:/app/data" `
	-v "${PWD}\uploads:/app/uploads" `
	incidentiq:first-version
```

The image does not copy `.env`, API keys, the local SQLite database, or uploaded files. The `data` and `uploads` mounts preserve those runtime files on the host.

Useful container commands:

```powershell
docker logs -f incidentiq
docker ps --filter "name=incidentiq"
docker stop incidentiq
docker rm incidentiq
```

Verify the deployment:

```powershell
Invoke-RestMethod http://localhost:8080/api/health
```

Expected response:

```json
{"status":"ok","service":"cloudops-sentinel-self-rag"}
```

## Using the Application

1. Start the local server or Docker container.
2. Open the web interface at `http://localhost:8080`.
3. Ask an incident or cloud-operations question.
4. Review the answer, route, sources, support status, and trace returned by the Self-RAG workflow.
5. Upload a runbook or other supported document when additional internal knowledge is needed.

Uploaded documents are written to `uploads/`, split into chunks, embedded with Gemini, and indexed in the configured Pinecone namespace.

Supported upload extensions:

- `.pdf`
- `.txt`
- `.md`
- `.docx`

## API Reference

### Health check

```http
GET /api/health
```

### Chat

```http
POST /api/chat
Content-Type: application/json
```

Request:

```json
{
	"question": "What is the rollback procedure for a failed deployment?",
	"thread_id": "demo-thread-001"
}
```

The response includes `answer`, `route`, `used_web_search`, `support_status`, `usefulness`, `sources`, `trace`, `thread_id`, and `memory_turns`.

PowerShell example:

```powershell
Invoke-RestMethod `
	-Uri http://localhost:8080/api/chat `
	-Method Post `
	-ContentType "application/json" `
	-Body '{"question":"What is the rollback procedure for a failed deployment?","thread_id":"demo-thread-001"}'
```

### Upload a document

```http
POST /api/upload
Content-Type: multipart/form-data
```

PowerShell example:

```powershell
curl.exe -X POST http://localhost:8080/api/upload -F "file=@documents/deployment-rollback-sop.md"
```

The response reports the filename, number of indexed chunks, and Pinecone namespace.

### Audit history

```http
GET /api/audits?limit=20
```

The limit is constrained by the application to between 1 and 100 entries.

## Architecture

```text
Browser
	|
	v
FastAPI (app.py)
	|-- /api/chat ------> LangGraph Self-RAG workflow
	|                       |-- Gemini generation
	|                       |-- Pinecone retrieval
	|                       |-- Tavily web search when needed
	|                       `-- SQLite-backed conversation/audit state
	|
	|-- /api/upload ----> document parsing and chunk ingestion -> Pinecone
	|-- /api/audits ----> SQLite audit records
	`-- /api/health
```

Important directories:

| Path | Purpose |
| --- | --- |
| `app.py` | FastAPI application and HTTP endpoints |
| `src/config.py` | Environment-backed application settings |
| `src/self_rag.py` | Self-RAG workflow and response generation |
| `src/ingestion.py` | Document parsing, chunking, and indexing |
| `src/vectorstore.py` | Gemini embeddings and Pinecone access |
| `src/db.py` | SQLite initialization and audit persistence |
| `src/models.py` | Pydantic API request and response models |
| `documents/` | Included internal runbooks |
| `uploads/` | Runtime-uploaded documents |
| `data/` | Runtime SQLite and LangGraph data |
| `static/` | Browser JavaScript and CSS |
| `templates/` | Jinja HTML templates |

## Troubleshooting

### Missing API key

Errors mentioning `GEMINI_API_KEY` or `PINECONE_API_KEY` mean the process did not receive the required environment variable. For Docker, confirm `--env-file .env` is present. For Conda, confirm the `.env` file is in the repository root or export the variables before starting the server.

### Pinecone dimension mismatch

The configured `EMBEDDING_DIMENSION` must match the existing Pinecone index. Set `PINECONE_INDEX_NAME` to a new index or recreate the old index with the configured dimension.

### Port 8080 is already in use

Use another host port while keeping the application port unchanged:

```powershell
docker run -d --name incidentiq -p 8081:8080 --env-file .env incidentiq:first-version
```

Then open `http://localhost:8081`.

### Inspect logs

For Docker:

```powershell
docker logs -f incidentiq
```

For Conda, the Uvicorn process writes startup and request errors directly to the terminal where it was started.

## Security Notes

- Never commit `.env` or place API keys in the Dockerfile.
- Pass secrets to Docker with `--env-file` or your deployment platform's secret manager.
- Do not publish the development server directly to the public internet without authentication, TLS, rate limiting, and appropriate network controls.
- Uploaded documents may contain operationally sensitive information. Restrict access to the application and protect the `uploads/` and `data/` directories.

## License

See [LICENSE](LICENSE) for the project's license.