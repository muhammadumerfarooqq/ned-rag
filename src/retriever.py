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


def retrieve(question: str, k: int = 5):
    """Return the top-k most relevant chunks for a question.

    Returns a list of dicts: [{"id": ..., "text": ..., "distance": ...}, ...]

    k=5 selected in Phase 10 by measurement, not intuition. With clause-aware
    chunking (47 chunks), recall@5 = 1.000 — every gold chunk is retrieved for
    every question in the eval set. k=3 gives recall@3 = 0.826 and starves the
    model of context (answer_rate 0.826 vs 0.913 at k=5).

    See eval/ and the W&B dashboard for the full ablation.
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
    print(f"Retrieved {len(hits)} chunks. Closest: {hits[0]['id']} @ {hits[0]['distance']:.3f}")
    print(f"Preview: {hits[0]['text'][:120]}...")