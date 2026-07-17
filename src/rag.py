import os
from dotenv import load_dotenv
from google import genai
from retriever import retrieve

load_dotenv()
_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = "gemini-3.1-flash-lite"

# The grounding prompt — this is what forces honesty and kills hallucination.
_PROMPT_TEMPLATE = """You are an assistant that answers questions about NED University's academic regulations.

Answer the question using ONLY the context below. Follow these rules strictly:
- If the answer is in the context, answer in plain English and quote the exact clause number (e.g. "clause 7.5").
- If the answer involves more than one clause or condition, put each one on its own line as a markdown bullet ("- "). Never run multiple clauses together in one paragraph.
- If the answer is NOT in the context, reply exactly: "I don't know — that isn't covered in the NED regulations I have access to."
- Do NOT use any knowledge outside the context. Do NOT guess.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def answer(question: str, k: int = 5):
    """Retrieve relevant chunks, then have the LLM answer grounded ONLY in them."""
    hits = retrieve(question, k=k)
    context = "\n\n---\n\n".join(h["text"] for h in hits)
    prompt = _PROMPT_TEMPLATE.format(context=context, question=question)
    response = _client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config={"temperature": 0},
    )
    return response.text


if __name__ == "__main__":
    tests = [
        "What attendance do I need to sit an exam?",
        "how is CGPA calculated?",
        "who founded NED university?",
    ]
    for q in tests:
        print(f"\n{'='*70}\nQ: {q}\n{'='*70}")
        print(answer(q))