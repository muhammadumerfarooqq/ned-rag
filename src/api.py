from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import answer

# 1. Create the app
app = FastAPI(title="NED Regulations RAG API")


# 3. Define the shape of an incoming request (auto-validated).
#    A question must be a string, min length 3 -> rejects empty/garbage.
class QueryRequest(BaseModel):
    question: str


# A simple health check — proves the server is alive (you had this in face-rec)
@app.get("/health")
def health():
    return {"status": "ok"}


# 2. The main endpoint: POST /query
@app.post("/query")
def query(request: QueryRequest):
    # Input validation: reject empty/whitespace questions
    q = request.question.strip()
    if len(q) < 3:
        raise HTTPException(status_code=400, detail="Question is too short.")

    # Call the RAG brain, but never leak a raw traceback to the user
    try:
        result = answer(q)
    except Exception:
        # Clean error — no file paths, no internals exposed
        raise HTTPException(status_code=500, detail="Internal error processing the question.")

    return {"question": q, "answer": result}