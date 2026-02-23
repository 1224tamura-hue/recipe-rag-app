import re

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import Settings


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def recipes_to_documents(recipes: list[dict]) -> list[Document]:
    docs: list[Document] = []
    for r in recipes:
        content = normalize_text(r["text"])
        docs.append(
            Document(
                page_content=content,
                metadata={
                    "id": r["id"],
                    "title": r["title"],
                    "meal_type": r.get("meal_type", ""),
                    "tags": ",".join(r.get("tags", [])),
                    "calories_kcal": r.get("calories_kcal", 0),
                    "protein_g": r.get("protein_g", 0),
                    "fat_g": r.get("fat_g", 0),
                    "carbs_g": r.get("carbs_g", 0),
                },
            )
        )
    return docs


def split_documents(docs: list[Document], settings: Settings) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    return splitter.split_documents(docs)
