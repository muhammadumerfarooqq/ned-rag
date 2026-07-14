import gradio as gr
from rag import answer

# The function the UI calls: question in -> grounded answer out
def ask(question):
    if not question or len(question.strip()) < 3:
        return "Please enter a real question (at least a few characters)."
    try:
        return answer(question.strip())
    except Exception:
        return "Something went wrong while processing your question. Please try again."


# Build the UI with a clean built-in theme (NOT default gray)
with gr.Blocks(theme=gr.themes.Soft(primary_hue="indigo")) as demo:
    gr.Markdown(
        """
        # 🎓 NED Regulations Assistant
        Ask about NED University's academic regulations — attendance, CGPA, probation,
        grades, withdrawal, and more. Answers come **only** from the official regulations
        and cite the exact clause. If it's not in the regulations, the assistant will say so.
        """
    )
    with gr.Row():
        question_box = gr.Textbox(
            label="Your question",
            placeholder="e.g. What attendance do I need to sit an exam?",
            lines=2,
            scale=4,
        )
    ask_button = gr.Button("Ask", variant="primary")
    answer_box = gr.Markdown(label="Answer")

    # Wire the button (and Enter key) to the function
    ask_button.click(fn=ask, inputs=question_box, outputs=answer_box)
    question_box.submit(fn=ask, inputs=question_box, outputs=answer_box)

    gr.Examples(
        examples=[
            "What attendance do I need to sit an exam?",
            "How is CGPA calculated?",
            "When am I placed on probation?",
            "Who founded NED university?",  # out-of-scope -> honest refusal demo
        ],
        inputs=question_box,
    )

if __name__ == "__main__":
    demo.launch()