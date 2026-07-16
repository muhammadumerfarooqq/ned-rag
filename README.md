# NED Regulations RAG

A Retrieval-Augmented Generation (RAG) app that answers questions about NED University's
academic regulations in plain English — pulling answers **only** from the official
documents and citing the exact source clause as proof.

Built so a student can ask "What attendance do I need to sit an exam?" and get a correct,
sourced answer in seconds — instead of digging through a regulations PDF or asking seniors.

**Status:** ✅ Live at [https://ned-rag.onrender.com](https://ned-rag.onrender.com) — Phase 9 complete (deployed + measured). Note: free tier sleeps after 15 min; first request may take 50-90s to wake.

📊 **Public evaluation dashboard:** [wandb.ai/umerfarooq-ned-university-of-engineering-and-technology/ned-rag-eval](https://wandb.ai/umerfarooq-ned-university-of-engineering-and-technology/ned-rag-eval)

## Why this project is different

Most "chat with a PDF" clones never leave localhost and are never measured. This one is:

- **Live on a public URL** (Docker + Render), callable by anyone.
- **Measured, not assumed** — retrieval quality and answer faithfulness are numbers on a
  public dashboard, produced by a hand-labelled evaluation set.
- **Honest about what it doesn't know** — 5/5 out-of-scope questions correctly refused.
- **Honest about its own limitations** — see [Known limitations](#known-limitations).

## Results

Measured against a hand-labelled set of 23 in-scope + 5 out-of-scope questions. Each
in-scope question carries a verbatim "gold snippet" that locates the chunk actually
containing its answer, so labels survive re-chunking.

### Retrieval — recall@k

recall@k = the fraction of questions for which the answer-bearing chunk appears in the
top-k retrieved chunks. Measures retrieval only; makes no LLM calls.

| k | recall@k |
|---|---|
| 1 | 0.478 |
| 3 | 0.826 |
| 5 | 0.957 |
| 10 | 1.000 |

Going from k=1 to k=3 rescues 8 questions, **7 of which had the gold chunk at rank 2** —
confirming the original k=3 choice with evidence rather than intuition. recall@10 = 1.000
is a sanity check (every gold chunk is reachable, and the label set is valid), not a
shipping configuration.

### End-to-end — why k=3 was kept

| | recall@k | answer_rate | faithfulness | abstained (in-scope) |
|---|---|---|---|---|
| **k=3** | 0.826 | 0.913 (21/23) | **21/21** | 2 |
| **k=5** | **0.957** | 0.913 (21/23) | 20/21 | 2 |

**k=5 retrieves 13 points better and delivers nothing.** `answer_rate` is identical, and
faithfulness drops. The two extra chunks caused one question to start being answered and
another — whose gold chunk ranked **1st** — to stop: context dilution talking the model out
of an answer it already had.

**Decision: k=3.** Higher recall did not translate into more answered questions, and
measurably diluted generation.

### Out-of-scope handling

`refusal_rate = 5/5 = 1.000` at both k=3 and k=5. Questions with no answer in the corpus
("Who founded NED University?", "What is the weather in Karachi?") return an honest
"I don't know" rather than a guess.

### Metrics defined

- **recall@k** — was the answer-bearing chunk retrieved? (retrieval only)
- **answer_rate** — of in-scope questions, how many produced an answer rather than an abstention?
- **faithfulness** — of the answers actually attempted, how many contain only claims supported
  by the retrieved context? (generation only)
- **refusal_rate** — of out-of-scope questions, how many were correctly refused?

Separating these matters: a bad answer can come from retrieval missing the evidence *or*
from the model inventing content. One number cannot tell them apart.

## Known limitations

Stated deliberately — these are measured findings, not unknowns.

- **Small sample.** n = 23 in-scope questions. One question flipping moves faithfulness by
  ~5 points. The direction of the k=3 vs k=5 result is defensible; the third decimal place
  is not.
- **LLM-as-judge is unreliable on abstentions.** Faithfulness is scored by Gemini judging
  Gemini's output. Identical refusal text ("I don't know...") scored both YES and NO at
  temperature 0 — the rubric ("is every factual claim supported?") is ill-defined for a
  statement about the *absence* of information. Fixed by classifying abstentions before
  judging and excluding them from the faithfulness denominator; they are tracked separately
  as `abstained`.
- **Fabricated citations are the real failure mode.** The single unfaithful answer stated a
  correct fact but attached a clause number that appears in a *different* chunk — the model
  stitched two chunks together to manufacture a reference. Since "cites the exact clause" is
  this app's headline feature, citation accuracy is a sharper risk than factual accuracy.
- **Chunking cuts across section boundaries.** `RecursiveCharacterTextSplitter` counts
  characters and has no concept of clauses or sections. One chunk holds the end of section 7,
  a garbled formula, and the start of section 8 — three topics averaged into one embedding.
  It ranks 6th for a question it directly answers. This is the target of the next phase.
- **PDF formula extraction is broken.** Clause 7.11 (the GPA formula) is a visual fraction in
  the source PDF; text extraction returns it with words concatenated and out of order — a
  parsing failure upstream of both retrieval and generation.

## Pipeline

1. **Chunking** — `src/chunker.py` splits the regulations PDF into ~1000-char overlapping chunks (RecursiveCharacterTextSplitter, size 1000 / overlap 150 → 38 chunks).
2. **Embedding + indexing** — `src/build_index.py` embeds chunks with `all-MiniLM-L6-v2` (384-d) into a persistent ChromaDB vector index.
3. **Retrieval** — `src/retriever.py` returns the top-k (k=3, selected on measured evidence) most relevant chunks, with their chunk IDs.
4. **Grounded generation** — `src/rag.py` passes retrieved chunks to Gemini (`gemini-3.1-flash-lite`, temperature 0) with a strict grounding prompt: answers cite the source clause, and questions not covered by the context return an honest "I don't know".
5. **API** — `src/api.py` wraps the pipeline in a FastAPI service: `POST /query` returns a grounded answer as JSON, `GET /health` for status. Input validation via Pydantic; errors handled without leaking internals.
6. **UI** — `src/app.py` serves a themed Gradio web interface (in-process, calling the RAG pipeline directly).
7. **Evaluation** — `eval/` holds the labelled question set and the harnesses that produce the numbers above, logged to Weights & Biases.

## Tech stack

Python · sentence-transformers · ChromaDB · Google Gemini API · FastAPI · Gradio (UI) · Docker (CPU-only PyTorch, vector index baked at build time) · Render · Weights & Biases (experiment tracking)

## Corpus

- `data/regulations_4155.pdf` — Revised Regulations for B.E./B.S./B.Arch (Notification 4155, NED University). Curated to one authoritative document on purpose.

## Security

- API key stored in a git-ignored `.env`, loaded via environment variables — never committed.
- Code references the key by name (`os.getenv`), so the repository is safe to make public.
- The key is **not** baked into the Docker image — embeddings run locally at build time and
  need no key. Verified: `docker run --rm ned-rag python -c "import os; print(os.getenv('GEMINI_API_KEY'))"`
  prints `None`. The key is injected only at runtime (`--env-file` locally, dashboard
  variable on Render).

## Running locally

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python src/build_index.py    # builds the vector index (one time)
python src/app.py            # http://localhost:7860
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

## Running the evaluation

Evaluation runs offline, from a local machine — it is not part of the deployed image, so
`wandb` is deliberately kept out of `requirements.txt` (the deployed container runs in
512 MB and never uses it).

```bash
pip install -r requirements-dev.txt
wandb login

python eval/validate_questions.py   # verifies every gold snippet resolves to a chunk
python eval/run_recall.py           # recall@1/3/5/10 — no LLM calls
python eval/run_faithfulness.py     # answer_rate, faithfulness, refusal_rate — uses Gemini
```

## Project structure

```
data/regulations_4155.pdf     the corpus
src/chunker.py                load_and_chunk() -> list of text chunks
src/build_index.py            embeds chunks, builds the persistent ChromaDB collection
src/retriever.py              retrieve(question, k) -> [{id, text, distance}]
src/rag.py                    answer(question, k): retrieval + grounded generation
src/api.py                    FastAPI service (POST /query, GET /health)
src/app.py                    Gradio UI (in-process, themed)
eval/questions.json           23 in-scope + 5 out-of-scope questions with gold snippets
eval/validate_questions.py    checks every gold snippet resolves to a chunk
eval/run_recall.py            recall@k harness -> W&B
eval/run_faithfulness.py      faithfulness / answer_rate / refusal_rate harness -> W&B
Dockerfile                    CPU-only torch, index baked at build time
requirements.txt              runtime dependencies (deployed)
requirements-dev.txt          evaluation-only dependencies (not deployed)
```

## Roadmap

- **Phase 10** — fix section-boundary chunking, re-measure, report the delta.
- Query rewriting for vague and typo'd phrasings.
- Deterministic GPA calculator (pure Python arithmetic, never routed through the LLM).