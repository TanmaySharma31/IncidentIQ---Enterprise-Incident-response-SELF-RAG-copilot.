# IncidentIQ Self-RAG Copilot

## Docker

Build the image from the repository root:

```powershell
docker build -t incidentiq .
```

Run it with the local environment file supplied at runtime:

```powershell
docker run --rm -p 8080:8080 --env-file .env `
	-v "${PWD}\data:/app/data" `
	-v "${PWD}\uploads:/app/uploads" `
	incidentiq
```

Open `http://localhost:8080` after the container starts. The image does not copy `.env` or API keys; provide secrets through `--env-file` or your deployment platform's secret store.