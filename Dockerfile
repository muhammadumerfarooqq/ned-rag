# Phase 7 — NED Regulations RAG
FROM python:3.11-slim

# WORKDIR = the container's "project root". All relative paths resolve from here.
WORKDIR /app

# Install deps FIRST so this slow layer caches across code-only rebuilds.
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.13.0 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt
# Copy ONLY what the app needs. Note: no venv, no .env, no local chroma_db.
COPY data/ ./data/
COPY src/ ./src/

# BAKE THE INDEX at build time (your locked design decision).
# Uses local sentence-transformers only — needs NO Gemini key.
RUN python src/build_index.py

EXPOSE 7860

# On start: launch the Gradio UI (imports answer() in-process).
CMD ["python", "src/app.py"]