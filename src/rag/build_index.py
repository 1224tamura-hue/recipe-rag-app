import logging
import os
from typing import List

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from src.config import Settings
from src.utils.text import split_documents


def get_embeddings(settings: Settings) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=settings.embedding_model)


def load_or_build_vectorstore(docs: List[Document], settings: Settings) -> Chroma:
    """
    - chroma_db/ が存在すればロード
    - なければ作成して永続化
    """
    os.makedirs(settings.db_dir, exist_ok=True)

    embeddings = get_embeddings(settings)

    # まずロードを試す（失敗したら作る）
    try:
        vs = Chroma(
            collection_name=settings.collection_name,
            persist_directory=settings.db_dir,
            embedding_function=embeddings,
        )
        # 何か入っているか軽くチェック（空なら作り直す）
        try:
            existing = vs._collection.count()  # type: ignore[attr-defined]
            if existing > 0:
                return vs
        except Exception as exc:
            logging.warning("Chroma count failed; rebuilding: %s", exc)
    except Exception as exc:
        logging.warning("Chroma load failed; rebuilding: %s", exc)

    # ビルド（分割→追加→永続化）
    split_docs = split_documents(docs, settings)
    vs = Chroma(
        collection_name=settings.collection_name,
        persist_directory=settings.db_dir,
        embedding_function=embeddings,
    )
    vs.add_documents(split_docs)
    return vs


def rebuild_vectorstore(docs: List[Document], settings: Settings) -> Chroma:
    """
    DBを作り直したい時用（将来UIボタンで使用）
    """
    embeddings = get_embeddings(settings)
    # Chromaは同名collectionが残ることがあるので別名運用もあり。
    # MVPはシンプルに同名で再作成を試みる。
    vs = Chroma(
        collection_name=settings.collection_name,
        persist_directory=settings.db_dir,
        embedding_function=embeddings,
    )
    # 既存を消して入れ直し（失敗しても継続）
    try:
        vs._collection.delete(where={})  # type: ignore[attr-defined]
    except Exception as exc:
        logging.warning("Chroma delete failed; continuing: %s", exc)

    split_docs = split_documents(docs, settings)
    vs.add_documents(split_docs)
    return vs
