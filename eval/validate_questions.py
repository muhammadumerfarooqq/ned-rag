import json, re, sys
sys.path.insert(0, "src")
from chunker import load_and_chunk

def norm(s):
    return re.sub(r"\s+", " ", s).strip().lower()

chunks = load_and_chunk("data/regulations_4155.pdf")
normed = [norm(c) for c in chunks]

with open("eval/questions.json", encoding="utf-8") as f:
    questions = json.load(f)

bad = 0
for q in questions:
    if q["type"] == "out_of_scope":
        print(f"{q['id']:5} SKIP (out of scope)")
        continue
    hits = [i for i, c in enumerate(normed) if norm(q["gold_snippet"]) in c]
    if len(hits) == 0:
        print(f"{q['id']:5} NOT FOUND -> {q['gold_snippet']!r}")
        bad += 1
    else:
        print(f"{q['id']:5} OK  chunk(s) {hits}")

print(f"\n{bad} broken snippet(s) out of {len(questions)}")