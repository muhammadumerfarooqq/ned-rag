import gradio as gr
from rag import answer
from gpa import calculate_gpa


# ---------- Tab 1: Q&A ----------
def ask(question):
    if not question or len(question.strip()) < 3:
        return "Please enter a real question (at least a few characters)."
    try:
        return answer(question.strip())
    except Exception:
        return "Something went wrong while processing your question. Please try again."


# ---------- Tab 2: GPA calculator ----------
EXAMPLE_ROWS = [
    ["Computer Communication Network", 150, 113, 4],
    ["Design of AR and VR Apps", 150, 145, 3],
    ["Game Design and Development", 150, 120, 4],
    ["Video Games and Creative Writing", 100, 85, 3],
    ["Operating Systems", 150, 130, 4],
]


def load_example():
    return EXAMPLE_ROWS


def compute_gpa(table):
    """table: Gradio Dataframe → pandas DataFrame (or list of lists)."""
    if hasattr(table, "values"):
        rows_in = table.values.tolist()
    else:
        rows_in = list(table)

    courses = []
    for row in rows_in:
        name = str(row[0]).strip() if row[0] is not None else ""
        if not name or name.lower() == "nan":
            continue  # skip blank rows

        try:
            total = float(row[1])
            obtained = float(row[2])
            credits = float(row[3])
        except (TypeError, ValueError):
            return [], f"**{name}**: marks and credit hours must be numbers."

        if total <= 0:
            return [], f"**{name}**: total marks must be greater than 0."
        if obtained < 0:
            return [], f"**{name}**: obtained marks cannot be negative."
        if obtained > total:
            return [], f"**{name}**: obtained marks ({obtained:g}) exceed total marks ({total:g})."
        if credits <= 0:
            return [], f"**{name}**: credit hours must be greater than 0."

        courses.append({"name": name, "total": total, "obtained": obtained, "credits": credits})

    if not courses:
        return [], "Add at least one course to calculate your GPA."

    rows, gpa, total_credits, total_points = calculate_gpa(courses)
    summary = (
        f"## Your GPA: **{gpa}**\n\n"
        f"Total credit hours: **{total_credits:g}**  ·  "
        f"Total grade points: **{total_points}**\n\n"
        f"GPA = {total_points} ÷ {total_credits:g} = **{gpa}** *(clause 7.11)*"
    )
    return rows, summary


# ---------- UI ----------
with gr.Blocks(theme=gr.themes.Soft(primary_hue="indigo")) as demo:
    gr.Markdown("# 🎓 NED Regulations Assistant")

    with gr.Tabs():
        # ===== TAB 1 =====
        with gr.Tab("Ask the regulations"):
            gr.Markdown(
                """
                Ask about NED University's academic regulations — attendance, CGPA, probation,
                grades, withdrawal, and more. Answers come **only** from the official regulations
                and cite the exact clause. If it's not in the regulations, the assistant will say so.
                """
            )
            question_box = gr.Textbox(
                label="Your question",
                placeholder="e.g. What attendance do I need to sit an exam?",
                lines=2,
            )
            ask_button = gr.Button("Ask", variant="primary")
            answer_box = gr.Markdown(label="Answer")

            ask_button.click(fn=ask, inputs=question_box, outputs=answer_box)
            question_box.submit(fn=ask, inputs=question_box, outputs=answer_box)

            gr.Examples(
                examples=[
                    "What attendance do I need to sit an exam?",
                    "How is CGPA calculated?",
                    "When am I placed on probation?",
                    "Who founded NED university?",
                ],
                inputs=question_box,
            )

        # ===== TAB 2 =====
        with gr.Tab("GPA calculator"):
            gr.Markdown(
                """
                ### Welcome, engineer — let me calculate your GPA.

                Enter your courses below: name, what the course is **out of** (100, 150, etc.),
                the marks you **obtained**, and its **credit hours**. Click **+** under the table
                to add a row per course.

                Grades follow **clause 7.10** and the GPA formula follows **clause 7.11**.
                Pure arithmetic — no AI involved, so the number is exact.
                """
            )

            with gr.Accordion("📋 See a worked example — a full semester", open=False):
                gr.Markdown(
                    """
                    | Course | Out of | Obtained | % | Grade | Point | Cr | Points |
                    |---|---|---|---|---|---|---|---|
                    | Computer Communication Network | 150 | 113 | 75.33 | **B+** | 3.4 | 4 | 13.6 |
                    | Design of AR and VR Apps | 150 | 145 | 96.67 | **A+** | 4.0 | 3 | 12.0 |
                    | Game Design and Development | 150 | 120 | 80.00 | **A-** | 3.7 | 4 | 14.8 |
                    | Video Games and Creative Writing | 100 | 85 | 85.00 | **A** | 4.0 | 3 | 12.0 |
                    | Operating Systems | 150 | 130 | 86.67 | **A** | 4.0 | 4 | 16.0 |

                    **Total points = 68.4  ·  Total credit hours = 18**

                    ### GPA = 68.4 ÷ 18 = **3.8**

                    Marks are converted to a percentage first, then to a grade using clause 7.10 —
                    so a course out of 150 and a course out of 100 are handled identically.
                    """
                )
                example_button = gr.Button("Load this example into the table", size="sm")

            course_table = gr.Dataframe(
                headers=["Course name", "Total marks", "Obtained marks", "Credit hours"],
                datatype=["str", "number", "number", "number"],
                row_count=(1, "dynamic"),
                column_count=(4, "fixed"),
                value=[["", None, None, None]],
                label="Your courses — click + below the table to add more rows",
            )

            gpa_button = gr.Button("Calculate my GPA", variant="primary")
            gpa_summary = gr.Markdown()
            result_table = gr.Dataframe(
                headers=[
                    "Course", "Total", "Obtained", "%",
                    "Grade", "Grade point", "Credit hrs", "Points earned",
                ],
                label="Breakdown",
                interactive=False,
            )

            example_button.click(fn=load_example, outputs=course_table)
            gpa_button.click(
                fn=compute_gpa,
                inputs=course_table,
                outputs=[result_table, gpa_summary],
            )

            gr.Markdown(
                """
                ---
                **Notes, honestly stated:**
                - A failing grade (**F**, below 50%) counts as **0.0** and *is* included in your GPA —
                  clause 7.10, note (iv). Calculators that drop failed courses inflate your GPA.
                - Grades **W, WU, I, IP, X, P** carry no grade points and are excluded entirely
                  (notes ii–iii). Don't enter them.
                - This computes **GPA** for one semester. **CGPA** spans multiple semesters (clause 7.11).
                - The regulations specify **absolute** grading. If your department curves, your actual
                  grade may differ — this implements the regulation, not departmental practice.
                - Boundaries use `>=`: 93.5% → A, 94% → A+.
                """
            )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)