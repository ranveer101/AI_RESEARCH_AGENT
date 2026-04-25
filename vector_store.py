import uuid

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

_vector_db = None


def get_vector_db():
    global _vector_db
    if _vector_db is None:
        import os
        cache_dir = os.getenv("SENTENCE_TRANSFORMERS_HOME", "./models")
        embedding_model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            cache_folder=cache_dir,
        )
        _vector_db = Chroma(
            collection_name="research_db",
            embedding_function=embedding_model,
        )
    return _vector_db


def add_to_vector_db(texts: list, source: str = "unknown") -> None:
    metadatas = [
        {"source": source, "id": str(uuid.uuid4())}
        for _ in texts
    ]
    get_vector_db().add_texts(texts, metadatas=metadatas)


def search_vector_db(query: str, k: int = 3) -> list:
    query = query.lower().strip()
    results = get_vector_db().similarity_search_with_score(query, k=k)
    filtered_docs = [doc for doc, score in results if score < 1.0]

    if not filtered_docs:
        filtered_docs = [doc for doc, _ in results]

    return filtered_docs


def clear_vector_db():
    get_vector_db().delete_collection()
