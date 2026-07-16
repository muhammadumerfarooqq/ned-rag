import wandb
import json, re, sys
sys.path.insert(0, "src")
from chunker import load_and_chunk, CHUNK_SIZE, CHUNK_OVERLAP, SEPARATORS
from retriever import retrieve


def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()


chunks = load_and_chunk("data/regulations_4155.pdf")
normed = [norm(c) for c in chunks]

with open("eval/questions.json", encoding="utf-8") as f:
    questions = json.load(f)

in_scope = [q for q in questions if q["type"] == "in_scope"]

# Resolve each question's gold chunk id(s) from its snippet
for q in in_scope:
    q["gold_ids"] = [
        f"chunk_{i}" for i, c in enumerate(normed) if norm(q["gold_snippet"]) in c
    ]

results = {}
for k in [1, 3, 5, 10]:
    score = 0
    print(f"\n=== k={k} ===")
    for q in in_scope:
        retrieved = [h["id"] for h in retrieve(q["question"], k=k)]
        hit = any(g in retrieved for g in q["gold_ids"])
        score += hit
        print(f"{q['id']:5} {'PASS' if hit else 'FAIL'}  gold={q['gold_ids']}  got={retrieved}")
    results[k] = score / len(in_scope)
    print(f"recall@{k} = {score}/{len(in_scope)} = {results[k]:.3f}")

print("\n=== SUMMARY ===")
print(f"chunks: {len(chunks)}  size={CHUNK_SIZE}  overlap={CHUNK_OVERLAP}")
for k, r in results.items():
    print(f"recall@{k} = {r:.3f}")

run = wandb.init(
    project="ned-rag-eval",
    config={
        "chunk_size": CHUNK_SIZE,
        "chunk_overlap": CHUNK_OVERLAP,
        "separators": str(SEPARATORS),
        "n_chunks": len(chunks),
        "embed_model": "all-MiniLM-L6-v2",
        "k_values": [1, 3, 5, 10],
    },
)
wandb.log({f"recall@{k}": r for k, r in results.items()})
run.finish()