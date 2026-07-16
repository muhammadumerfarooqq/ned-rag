# NED Regulations RAG

A Retrieval-Augmented Generation (RAG) app that answers questions about NED University's
academic regulations in plain English — pulling answers **only** from the official
documents and citing the exact source clause as proof.

Built so a student can ask "What attendance do I need to sit an exam?" and get a correct,
sourced answer in seconds — instead of digging through a regulations PDF or asking seniors.

**Status:** ✅ Live at [https://ned-rag.onrender.com](https://ned-rag.onrender.com) — Phase 10 complete (deployed, measured, tuned by ablation). Note: free tier sleeps after 15 min; first request may take 50-90s to wake.

📊 **Public evaluation dashboard:** [wandb.ai/umerfarooq-ned-university-of-engineering-and-technology/ned-rag-eval](https://wandb.ai/umerfarooq-ned-university-of-engineering-and-technology/ned-rag-eval)

## Why this project is different

Most "chat with a PDF" clones never leave localhost and are never measured. This one is:

- **Live on a public URL** (Docker + Render), callable by anyone.
- **Measured, not assumed** — retrieval quality and answer faithfulness are numbers on a
  public dashboard, produced by a hand-labelled evaluation set.
- **Tuned by ablation, not intuition** — chunking strategy and `k` were both selected by
  running controlled experiments and reading the numbers, including the experiments that failed.
- **Honest about what it doesn't know** — 5/5 out-of-scope questions correctly refused.
- **Honest about its own limitations** — see [Known limitations](#known-limitations).

## Results

Measured against a hand-labelled set of 23 in-scope + 5 out-of-scope questions. Each
in-scope question carries a verbatim "gold snippet" that locates the chunk actually
containing its answer — so labels survive re-chunking, which is what made the ablation below
possible without relabelling.

### Metrics defined

- **recall@k** — was the answer-bearing chunk retrieved? (retrieval only; makes no LLM calls)
- **answer_rate** — of in-scope questions, how many produced an answer rather than an abstention?
- **faithfulness** — of the answers actually attempted, how many contain only claims supported
  by the retrieved context? (generation only)
- **refusal_rate** — of out-of-scope questions, how many were correctly refused?

Separating these matters: a bad answer can come from retrieval missing the evidence *or* from
the model inventing content *or* from the model refusing evidence it has. One number cannot
tell them apart.

### Chunking ablation

**Hypothesis:** the character-based splitter cuts across section boundaries. One chunk held
the tail of section 7, a garbled formula, and the start of section 8 — three topics averaged
into a single embedding. It ranked 6th for a question it directly answered.

Three configurations, same evaluation set:

| | chunks | recall@1 | recall@3 | recall@5 | recall@10 |
|---|---|---|---|---|---|
| Character split, size 1000 (baseline) | 38 | 0.478 | 0.826 | 0.957 | 1.000 |
| Character split, size 500 | 93 | 0.522 | 0.739 | 0.913 | 0.957 |
| **Clause-aware, size 1000 (shipped)** | **47** | **0.652** | 0.826 | **1.000** | 1.000 |

**Smaller chunks failed — and the failure was informative.** Halving `chunk_size` fixed the
target chunk: both questions that depended on it jumped to rank 1. But recall@3 *dropped* to
0.739 and recall@10 fell below 1.000. Every new failure was an off-by-one neighbour (gold
chunk 54 → retrieved 53; gold 38 → retrieved 37, 40, 41). At 500 characters, adjacent chunks
became too similar to distinguish and crowded the gold chunk out of the top-3. The blunt fix
traded topic-bleed *within* chunks for topic-bleed *across* chunks — the same disease in the
opposite direction.

**Clause-aware splitting worked.** Using `["\n\s*\d+\.\d+", "\n\n", "\n", " ", ""]` as
separators (regex enabled) forces breaks at clause numbers — 7.5, 8.1, 12.1 — before falling
back to paragraphs and lines. Chunks stayed distinct (47, not 93) while topics stopped
bleeding across sections: **recall@1 improved 36% relative (0.478 → 0.652) and recall@5
reached 1.000.** recall@3 was unchanged — the gains sit at k=1 and k=5, not at the middle.

### Selecting k — the end-to-end grid

recall alone does not decide anything. Every configuration was also measured end to end:

| chunking | k | recall@k | answer_rate | faithfulness | refusal_rate |
|---|---|---|---|---|---|
| Character, 38 | 3 | 0.826 | 0.913 (21/23) | 21/21 | 5/5 |
| Character, 38 | 5 | 0.957 | 0.913 (21/23) | 20/21 | 5/5 |
| Clause-aware, 47 | 3 | 0.826 | 0.826 (19/23) | 19/19 | 5/5 |
| **Clause-aware, 47** | **5** | **1.000** | **0.913 (21/23)** | **21/21** | **5/5** |

**Shipped: clause-aware chunking, k=5.**

Two failure modes showed up in this grid, and they are opposites:

- **Dilution** (character chunks, k=5): two extra chunks talked the model out of an answer
  whose gold chunk ranked *first*. Faithfulness dropped to 20/21.
- **Starvation** (clause-aware, k=3): clause-aware chunks end where the clause ends, so they
  average ~19% shorter. At k=3 the model receives materially less context and abstains more —
  answer_rate falls to 0.826.

Clause-aware at k=5 avoids both: perfect retrieval, and enough context to use it.

**Honest framing: end-to-end this ties the original baseline rather than beating it**
(21/23 answered, 21/21 faithful, 5/5 refused — identical). It ships because **recall@5 = 1.000
removes retrieval as a constraint.** Under the baseline, four questions could never be answered
at k=3 no matter how the prompt was tuned — the evidence never arrived. Now every gold chunk
is retrieved for every question, so the remaining ceiling is the prompt, which is addressable.
Cost: ~35% more context per query (5 chunks of ~808 chars vs 3 of ~1000). Slower and more
tokens, but modest.

### The real bottleneck is the prompt, not retrieval

Across every configuration tested, recall moved 0.826 → 0.957 → 1.000 while `answer_rate`
stayed pinned at 0.913. Perfect retrieval did not move the end-to-end number at all.

Both remaining abstentions had their gold chunk retrieved — q13 at rank 1, q16 at rank 5 —
and the model refused anyway. The grounding prompt is tuned hard toward honesty (a perfect
5/5 on out-of-scope refusal), and the cost of that conservatism is now measurable: roughly
**2 in 23 in-scope questions are refused despite the evidence being present**. That is the
next thing worth fixing, and it is a generation problem, not a retrieval one.

## Known limitations

Stated deliberately — these are measured findings, not unknowns.

- **Small sample.** n = 23 in-scope questions. One question flipping moves faithfulness by
  ~5 points. Directions in the ablation above are defensible; third decimal places are not.
- **LLM-as-judge is unreliable on abstentions.** Faithfulness is scored by Gemini judging
  Gemini's output. Identical refusal text ("I don't know...") scored both YES and NO at
  temperature 0 — the rubric ("is every factual claim supported?") is ill-defined for a
  statement about the *absence* of information. Fixed by classifying abstentions before
  judging and excluding them from the faithfulness denominator; they are tracked separately
  as `abstained`. Judging Gemini with Gemini also carries self-preference bias, which this
  fix does not address.
- **Fabricated citations are the sharpest risk.** During the ablation, one answer stated a
  correct fact but attached a clause number that appears in a *different* chunk — the model
  stitched two chunks together to manufacture a reference. It does not appear in the shipped
  configuration's eval run (faithfulness 21/21), but n is small and "cites the exact clause"
  is this app's headline feature, so citation accuracy matters more here than factual accuracy.
- **Over-conservative refusal.** ~2 in 23 in-scope questions are refused with the answer
  present in the retrieved context. This is the direct cost of a strict grounding prompt.
- **PDF formula extraction is degraded.** Clause 7.11 (the GPA formula) is a visual fraction
  in the source PDF; text extraction returns it concatenated and out of order. The model
  recovers the meaning correctly in practice, but the underlying text is damaged and any
  answer depending on it rests on that recovery.
- **Single corpus.** One document, curated deliberately. Nothing here has been tested at
  scale, across multiple documents, or under concurrent load.

## Pipeline

1. **Chunking** — `src/chunker.py` splits the regulations PDF with `RecursiveCharacterTextSplitter`
   using clause-number separators (regex `\n\s*\d+\.\d+`) before paragraph and line fallbacks;
   size 1000 / overlap 150 → 47 chunks. Strategy selected by ablation (see Results).
2. **Embedding + indexing** — `src/build_index.py` embeds chunks with `all-MiniLM-L6-v2`
   (384-d, CPU) into a persistent ChromaDB collection.
3. **Retrieval** — `src/retriever.py` returns the top-k (k=5, selected by measurement) most
   relevant chunks with their IDs.
4. **Grounded generation** — `src/rag.py` passes retrieved chunks to Gemini
   (`gemini-3.1-flash-lite`, temperature 0) with a strict grounding prompt: answers cite the
   source clause, and questions not covered by the context return an honest "I don't know".
5. **API** — `src/api.py` wraps the pipeline in a FastAPI service: `POST /query` returns a
   grounded answer as JSON, `GET /health` for status. Pydantic validation; errors handled
   without leaking internals.
6. **UI** — `src/app.py` serves a themed Gradio interface, in-process (calls `answer()`
   directly rather than over HTTP, so one 512 MB instance runs one process).
7. **Evaluation** — `eval/` holds the labelled question set and the harnesses that produce
   every number above, logged to Weights & Biases.

## Tech stack

Python · sentence-transformers · ChromaDB · Google Gemini API · FastAPI · Gradio (UI) · Docker (CPU-only PyTorch, vector index baked at build time) · Render · Weights & Biases (experiment tracking)

## Corpus

- `data/regulations_4155.pdf` — Revised Regulations for B.E./B.S./B.Arch (Notification 4155,
  NED University). Curated to one authoritative document on purpose.

## Security

- API key stored in a git-ignored `.env`, loaded via environment variables — never committed.
- Code references the key by name (`os.getenv`), so the repository is safe to make public.
- The key is **not** baked into the Docker image — embeddings run locally at build time and
  need no key. Verified: `docker run --rm ned-rag python -c "import os; print(os.getenv('GEMINI_API_KEY'))"`
  prints `None`. The key is injected only at runtime (`--env-file` locally, dashboard variable
  on Render).

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
`wandb` is deliberately kept out of `requirements.txt` (the deployed container runs in 512 MB
and never uses it).

```bash
pip install -r requirements-dev.txt
wandb login

python eval/validate_questions.py   # verifies every gold snippet resolves to a chunk
python eval/run_recall.py           # recall@1/3/5/10 — no LLM calls
python eval/run_faithfulness.py     # answer_rate, faithfulness, refusal_rate — uses Gemini
```

Chunking config lives in `src/chunker.py` as module constants and is read directly by the
eval harness into the W&B run config — so a logged run cannot be mislabelled with settings
it did not use.

## Project structure

```
data/regulations_4155.pdf     the corpus
src/chunker.py                clause-aware splitter + chunking config constants
src/build_index.py            embeds chunks, builds the persistent ChromaDB collection
src/retriever.py              retrieve(question, k=5) -> [{id, text, distance}]
src/rag.py                    answer(question, k=5): retrieval + grounded generation
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

- **Loosen the grounding prompt** and re-measure. Retrieval is now perfect at k=5; the
  remaining ~2/23 abstentions are the prompt refusing evidence it already has. Target:
  raise answer_rate without losing the 5/5 refusal rate.
- **Citation verification** — check that every clause number in an answer actually appears in
  the retrieved context, rather than trusting the model not to stitch one together.
- **Query rewriting** for vague and typo'd phrasings.
- **Deterministic GPA calculator** — pure Python arithmetic from the clause 7.10 grade table,
  never routed through the LLM (a wrong CGPA is worse than no feature).