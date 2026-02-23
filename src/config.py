from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    db_dir: str = "chroma_db"
    collection_name: str = "recipes"
    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"
    chunk_size: int = 700
    chunk_overlap: int = 100
    top_k_default: int = 3
    temperature_default: float = 0.2
    sqlite_db_path: str = "diet.db"


def get_settings() -> Settings:
    return Settings(
        db_dir=os.getenv("RAG_DB_DIR", "chroma_db"),
        collection_name=os.getenv("RAG_COLLECTION", "recipes"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        chat_model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
        chunk_size=int(os.getenv("RAG_CHUNK_SIZE", "700")),
        chunk_overlap=int(os.getenv("RAG_CHUNK_OVERLAP", "100")),
        top_k_default=int(os.getenv("RAG_TOP_K_DEFAULT", "3")),
        temperature_default=float(os.getenv("RAG_TEMPERATURE_DEFAULT", "0.2")),
        sqlite_db_path=os.getenv("DIET_DB_PATH", "diet.db"),
    )
