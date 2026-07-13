# ned-rag
**Status:** 🚧 In progress — Phase 1 complete (PDF loading + chunking)

## Pipeline
1. **Chunking** — `src/chunker.py` loads the regulations PDF and splits it into ~1000-char overlapping chunks (RecursiveCharacterTextSplitter).
