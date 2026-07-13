import chromadb
from chromadb.utils import embedding_functions
from chunker import load_and_chunk

# 1. Get the chunks from Phase 1's module (reuse, don't rewrite)
chunks = load_and_chunk("data/regulations_4155.pdf")
print(f"Loaded {len(chunks)} chunks.")

# 2. Tell Chroma to embed using the SAME model we tested (all-MiniLM)
embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# 3. Open a persistent DB in ./chroma_db (created on disk, survives restarts)
client = chromadb.PersistentClient(path="chroma_db")

# 4. Reset the collection so re-running doesn't create duplicates (idempotent)
client.delete_collection("ned_regulations") if any(
    c.name == "ned_regulations" for c in client.list_collections()
) else None
collection = client.create_collection(
    name="ned_regulations",
    embedding_function=embed_fn,
)

# 5. Add all chunks — Chroma embeds each one and stores vector + text + id
collection.add(
    documents=chunks,
    ids=[f"chunk_{i}" for i in range(len(chunks))],
)
print(f"Indexed {collection.count()} chunks into Chroma.")

# 6. Prove search works: ask a question, get the nearest chunks back
results = collection.query(
    query_texts=["What attendance do I need to sit an exam?"],
    n_results=2,
)
print("\nTop match for 'attendance to sit an exam':\n")
print(results["documents"][0][0][:400])