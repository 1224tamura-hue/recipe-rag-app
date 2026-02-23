from langchain_community.vectorstores import Chroma


def build_retriever(vectorstore: Chroma, top_k: int):
    return vectorstore.as_retriever(search_kwargs={"k": top_k})
