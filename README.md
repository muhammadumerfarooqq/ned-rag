# ned-rag
**Status:** 🚧 In progress — Phase 1 complete (PDF loading + chunking)

## Pipeline
1. **Chunking** — `src/chunker.py` loads the regulations PDF and splits it into ~1000-char overlapping chunks (RecursiveCharacterTextSplitter).

**Status:** 🚧 In progress — Phase 2 complete (embeddings + vector index)

## Pipeline
1. **Chunking** — `src/chunker.py` splits the regulations PDF into ~1000-char overlapping chunks.
2. **Embedding + indexing** — `src/build_index.py` embeds chunks with all-MiniLM-L6-v2 (384-d) and stores them in a persistent ChromaDB vector index for semantic search.


**Status:** 🚧 In progress — Phase 3 complete (semantic retrieval)

## Pipeline
1. **Chunking** — `src/chunker.py` splits the regulations PDF into ~1000-char overlapping chunks.
2. **Embedding + indexing** — `src/build_index.py` embeds chunks with all-MiniLM-L6-v2 (384-d) into a persistent ChromaDB index.
3. **Retrieval** — `src/retriever.py` returns the top-k (k=3) most relevant chunks for a question via cosine similarity.

**Status:** 🚧 In progress — Phase 4 complete (grounded RAG working end-to-end)

## Pipeline
1. **Chunking** — `src/chunker.py` splits the regulations PDF into ~1000-char overlapping chunks.
2. **Embedding + indexing** — `src/build_index.py` embeds chunks with all-MiniLM-L6-v2 (384-d) into a persistent ChromaDB index.
3. **Retrieval** — `src/retriever.py` returns the top-k (k=3) most relevant chunks via cosine similarity.
4. **Grounded generation** — `src/rag.py` passes retrieved chunks to Gemini (gemini-3.1-flash-lite) with a strict grounding prompt: answers cite the source clause, and out-of-scope questions return an honest "I don't know" instead of hallucinating.