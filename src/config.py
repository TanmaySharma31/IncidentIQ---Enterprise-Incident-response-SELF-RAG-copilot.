from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseModel):
    # Gemini
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-3.6-flash")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
    embedding_dimension: int = int(os.getenv("EMBEDDING_DIMENSION", "768"))
    max_output_tokens: int = int(os.getenv("MAX_OUTPUT_TOKENS", "512"))
    max_document_chars: int = int(os.getenv("MAX_DOCUMENT_CHARS", "3500"))

    # Pinecone
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "incidentiq-gemini-self-rag")
    pinecone_namespace: str = os.getenv("PINECONE_NAMESPACE", "incident-runbooks")
    pinecone_cloud: str = os.getenv("PINECONE_CLOUD", "aws")
    pinecone_region: str = os.getenv("PINECONE_REGION", "us-east-1")

    # Internet search
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    # Self-RAG controls
    top_k: int = int(os.getenv("TOP_K", "3"))
    max_support_retries: int = int(os.getenv("MAX_SUPPORT_RETRIES", "1"))
    max_retrieval_rewrites: int = int(os.getenv("MAX_RETRIEVAL_REWRITES", "1"))
    max_web_rewrites: int = int(os.getenv("MAX_WEB_REWRITES", "1"))
    database_path: str = os.getenv("DATABASE_PATH", "data/audit.db")

    @property
    def database_file(self) -> Path:
        p = Path(self.database_path)
        return p if p.is_absolute() else ROOT / p



@lru_cache
def get_settings() -> Settings:
    return Settings()