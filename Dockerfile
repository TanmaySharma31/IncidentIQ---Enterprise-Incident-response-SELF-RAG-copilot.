FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py data_ingestion.py ./
COPY src ./src
COPY static ./static
COPY templates ./templates
COPY documents ./documents

RUN mkdir -p /app/data /app/uploads \
	&& useradd --create-home --shell /usr/sbin/nologin appuser \
	&& chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
