# NED Regulations RAG

A Retrieval-Augmented Generation (RAG) app that answers questions about NED University's
academic regulations in plain English — pulling answers **only** from the official
documents and citing the exact source clause as proof.

Built so a student can ask "What attendance do I need to sit an exam?" and get a correct,
sourced answer in seconds — instead of digging through a regulations PDF or asking seniors.

**Status:** ✅ Live at [https://ned-rag.onrender.com](https://ned-rag.onrender.com) — Phase 8 complete (deployed). Note: free tier sleeps after 15 min; first request may take 50-90s to wake.

## Why this project is different
Most "chat with a PDF" clones never leave localhost and are never measured. This one is
built to:
- Run live on a public URL (Docker + Render), callable by anyone.
- **Measure** retrieval quality (recall@k) and answer faithfulness — logged, not assumed.
- Handle out-of-scope questions honestly: it answers "I don't know" instead of hallucinating.
- Stay robust across differently-phrased questions (terse, typo'd, vague).

## Pipeline
1. **Chunking** — `src/chunker.py` splits the regulations PDF into ~1000-char overlapping chunks (RecursiveCharacterTextSplitter).
2. **Embedding + indexing** — `src/build_index.py` embeds chunks with `all-MiniLM-L6-v2` (384-d) into a persistent ChromaDB vector index.
3. **Retrieval** — `src/retriever.py` returns the top-k (k=3) most relevant chunks for a question via cosine similarity.
4. **Grounded generation** — `src/rag.py` passes retrieved chunks to Gemini (`gemini-3.1-flash-lite`) with a strict grounding prompt: answers cite the source clause, and out-of-scope questions return an honest "I don't know" instead of hallucinating.
5. **API** — `src/api.py` wraps the pipeline in a FastAPI service: `POST /query` returns a grounded answer as JSON, `GET /health` for status. Input validation via Pydantic; errors handled without leaking internals.
6. **UI** — `src/app.py` serves a themed Gradio web interface (in-process, calling the RAG pipeline directly) so users can ask questions in plain English and see cited answers.

## Tech stack
Python · sentence-transformers · ChromaDB · Google Gemini API · FastAPI · Gradio (UI) · Docker · Render · Weights & Biases (evaluation)

## Corpus
- `data/regulations_4155.pdf` — Revised Regulations for B.E./B.S./B.Arch (Notification 4155, NED University)

## Security
- API key stored in a git-ignored `.env`, loaded via environment variables — never committed.
- Code references the key by name (`os.getenv`), so the repository is safe to make public.
- The key is **not** baked into the Docker image — embeddings run locally at build time and need no key. Verified: `docker run --rm ned-rag python -c "import os; print(os.getenv('GEMINI_API_KEY'))"` prints `None`. The key is injected only at runtime.

## Running locally
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python src/build_index.py    # builds the vector index (one time)
uvicorn api:app --app-dir src
# open http://127.0.0.1:8000/docs
```

## Running with Docker
The image bundles the code and the pre-built vector index (baked in at build time, so the
container starts ready — no re-embedding on startup). The Gemini key is passed in at runtime
and is never stored in the image.
```bash
docker build -t ned-rag .
docker run -p 7860:7860 --env-file .env ned-rag
# open http://localhost:7860
```