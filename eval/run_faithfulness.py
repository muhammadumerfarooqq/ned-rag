import wandb
import json, sys, time
sys.path.insert(0, "src")
from retriever import retrieve
from rag import answer, _client, _MODEL


def with_retry(fn, *args, **kwargs):
    for attempt in range(4):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            if "503" in str(e) or "429" in str(e):
                wait = 10 * (attempt + 1)
                print(f"  ...{type(e).__name__}, retrying in {wait}s")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("failed after 4 retries")


with open("eval/questions.json", encoding="utf-8") as f:
    questions = json.load(f)

in_scope = [q for q in questions if q["type"] == "in_scope"]
out_scope = [q for q in questions if q["type"] == "out_of_scope"]

K = 5

REFUSAL = "i don't know"


def is_refusal(text):
    return REFUSAL in text.lower()


JUDGE_PROMPT = """You are checking whether an ANSWER stays faithful to its SOURCE.

SOURCE:
{context}

ANSWER:
{answer}

Is every factual claim in the ANSWER supported by the SOURCE?
Ignore wording differences - only check the facts.
Reply with exactly one word: YES or NO."""


def judge(context, ans):
    resp = _client.models.generate_content(
        model=_MODEL,
        contents=JUDGE_PROMPT.format(context=context, answer=ans),
        config={"temperature": 0},
    )
    return resp.text.strip().upper().startswith("YES")


rows = []

# ---- IN-SCOPE: classify refusals BEFORE judging ----
faithful = 0
attempted = 0
abstained = 0
print("=== IN-SCOPE ===")
for q in in_scope:
    hits = retrieve(q["question"], k=K)
    context = "\n\n---\n\n".join(h["text"] for h in hits)
    ans = with_retry(answer, q["question"], k=K)
    time.sleep(4)

    if is_refusal(ans):
        abstained += 1
        verdict = "ABSTAINED"
        flag = "N/A"
    else:
        attempted += 1
        ok = with_retry(judge, context, ans)
        time.sleep(4)
        faithful += ok
        verdict = "FAITHFUL" if ok else "UNFAITHFUL"
        flag = "YES" if ok else "NO"

    print(f"{q['id']:5} {verdict:11} {q['question']}")
    rows.append([q["id"], q["question"], "in_scope", ans[:300], flag, ""])

answer_rate = attempted / len(in_scope)
faithfulness = faithful / attempted if attempted else 0.0
print(f"\nanswer_rate  = {attempted}/{len(in_scope)} = {answer_rate:.3f}")
print(f"faithfulness = {faithful}/{attempted} = {faithfulness:.3f}  (of attempted answers only)")
print(f"abstained    = {abstained}  (in-scope questions it refused)")

# ---- OUT-OF-SCOPE: refusal is the correct behaviour ----
refused = 0
print("\n=== OUT-OF-SCOPE REFUSAL ===")
for q in out_scope:
    ans = with_retry(answer, q["question"], k=K)
    time.sleep(4)
    ok = is_refusal(ans)
    refused += ok
    print(f"{q['id']:5} {'REFUSED' if ok else 'ANSWERED (BAD)':14} {q['question']}")
    rows.append([q["id"], q["question"], "out_of_scope", ans[:300], "", "YES" if ok else "NO"])

refusal_rate = refused / len(out_scope)
print(f"\nrefusal_rate = {refused}/{len(out_scope)} = {refusal_rate:.3f}")

run = wandb.init(
    project="ned-rag-eval",
    config={"k": K, "judge_model": _MODEL, "eval_type": "faithfulness"},
)
wandb.log({
    "faithfulness": faithfulness,
    "answer_rate": answer_rate,
    "abstained": abstained,
    "out_of_scope_refusal_rate": refusal_rate,
})
table = wandb.Table(
    columns=["id", "question", "type", "answer", "faithful", "refused"], data=rows
)
wandb.log({"eval_details": table})
run.finish()