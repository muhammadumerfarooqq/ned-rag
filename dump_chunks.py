import sys
sys.path.insert(0, "src")
from chunker import load_and_chunk

chunks = load_and_chunk("data/regulations_4155.pdf")
with open("chunks_dump.txt", "w", encoding="utf-8") as f:
    for i, c in enumerate(chunks):
        f.write(f"\n{'='*70}\nchunk_{i}\n{'='*70}\n{c}\n")
print(f"Wrote {len(chunks)} chunks to chunks_dump.txt")