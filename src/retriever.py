import chromadb
from chromadb.utils import embedding_functions

# Load once at module level so importing files reuse the same connection
_embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)
_client = chromadb.PersistentClient(path="chroma_db")
_collection = _client.get_collection(
    name="ned_regulations", embedding_function=_embed_fn
)


def retrieve(question: str, k: int = 3):
    """Return the top-k most relevant chunks for a question.

    Returns a list of dicts: [{"text": ..., "distance": ...}, ...]
    k=3 chosen because retrieval tests showed the answer-bearing chunk
    frequently ranks 2nd, not 1st.
    """
    results = _collection.query(query_texts=[question], n_results=k)
    ids = results["ids"][0]
    docs = results["documents"][0]
    dists = results["distances"][0]
    return [
        {"id": i, "text": d, "distance": dist}
        for i, d, dist in zip(ids, docs, dists)
    ]

if __name__ == "__main__":
    # Self-test when run directly
    hits = retrieve("What attendance do I need to sit an exam?")
    print(f"Retrieved {len(hits)} chunks. Closest distance: {hits[0]['distance']:.3f}")
    print(f"Preview: {hits[0]['text'][:120]}...")