import gradio as gr
from rag import answer
from gpa import calculate_gpa


# ============================================================
#  LOGIC — unchanged. Do not edit when restyling.
# ============================================================
def ask(question):
    if not question or len(question.strip()) < 3:
        return "Please enter a real question (at least a few characters)."
    try:
        return answer(question.strip())
    except Exception:
        return "Something went wrong while processing your question. Please try again."


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
    if hasattr(table, "values"):
        rows_in = table.values.tolist()
    else:
        rows_in = list(table)

    courses = []
    for row in rows_in:
        name = str(row[0]).strip() if row[0] is not None else ""
        if not name or name.lower() == "nan":
            continue

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


# ============================================================
#  NAVIGATION
# ============================================================
def show_qa():
    return (
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(variant="primary"),
        gr.update(variant="secondary"),
    )


def show_gpa():
    return (
        gr.update(visible=False),
        gr.update(visible=True),
        gr.update(variant="secondary"),
        gr.update(variant="primary"),
    )


# ============================================================
#  STYLING
# ============================================================
MAGENTA = "#FF2E9F"
PURPLE = "#7B2FF7"

CSS = f"""
.gradio-container, body {{
    background: #000000 !important;
    color: #E8E8ED !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}}
footer {{ display: none !important; }}

#app-header {{
    text-align: center;
    padding: 28px 0 4px 0;
}}
#app-header h1 {{
    font-size: 30px;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(90deg, {MAGENTA} 0%, {PURPLE} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
#app-header p {{
    color: #6E6E78;
    font-size: 13px;
    margin: 6px 0 0 0;
    letter-spacing: 0.4px;
}}

#nav-bar {{
    justify-content: center;
    gap: 8px;
    border-bottom: 1px solid #1C1C22;
    padding-bottom: 14px;
    margin-bottom: 26px;
}}
#nav-bar button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
    max-width: 240px;
}}
#nav-bar button.secondary {{ color: #5A5A64 !important; }}
#nav-bar button.primary {{ color: {MAGENTA} !important; }}

.grad-btn {{
    background: linear-gradient(90deg, {MAGENTA} 0%, {PURPLE} 100%) !important;
    border: none !important;
    border-radius: 40px !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    padding: 14px 0 !important;
    box-shadow: 0 4px 24px rgba(255, 46, 159, 0.22) !important;
}}
.grad-btn:hover {{ filter: brightness(1.12); }}

.sleek-input textarea, .sleek-input input {{
    background: #0B0B0F !important;
    border: 1px solid #1E1E26 !important;
    border-radius: 24px !important;
    color: #E8E8ED !important;
    padding: 16px 20px !important;
    font-size: 15px !important;
}}
.sleek-input textarea:focus, .sleek-input input:focus {{
    border-color: {MAGENTA} !important;
    box-shadow: 0 0 0 3px rgba(255, 46, 159, 0.15) !important;
    outline: none !important;
}}
.sleek-input label span {{ color: #6E6E78 !important; font-size: 12px !important; }}

#answer-bubble {{
    border: 1px solid transparent !important;
    border-radius: 28px !important;
    background:
        linear-gradient(#08080C, #08080C) padding-box,
        linear-gradient(120deg, {MAGENTA}, {PURPLE}) border-box !important;
    padding: 22px 26px !important;
    min-height: 90px;
    line-height: 1.65;
}}
#answer-bubble p, #answer-bubble li {{ color: #D8D8E0 !important; }}

.gradio-container .examples button,
.gradio-container button.example {{
    background: #0B0B0F !important;
    border: 1px solid #22222B !important;
    border-radius: 40px !important;
    color: #8A8A96 !important;
    font-size: 13px !important;
    padding: 9px 18px !important;
}}
.gradio-container .examples button:hover {{
    border-color: {MAGENTA} !important;
    color: {MAGENTA} !important;
}}

.gradio-container .accordion,
.gradio-container details {{
    background: #08080C !important;
    border: 1px solid #1C1C22 !important;
    border-radius: 24px !important;
}}

.gradio-container table {{
    background: transparent !important;
    border: none !important;
    border-collapse: collapse !important;
}}
.gradio-container table thead th {{
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid #22222B !important;
    color: #5A5A64 !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    padding: 12px 14px !important;
}}
.gradio-container table tbody td {{
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid #131318 !important;
    color: #C8C8D2 !important;
    font-size: 14px !important;
    padding: 13px 14px !important;
}}
.gradio-container table tbody tr:hover td {{ background: #0A0A0E !important; }}

.wrap.svelte-1cl284s, .block {{
    background: transparent !important;
    border: none !important;
}}

#gpa-summary h2 {{
    background: linear-gradient(90deg, {MAGENTA} 0%, {PURPLE} 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 30px !important;
}}

#credit {{
    text-align: center;
    color: #3E3E48;
    font-size: 12px;
    padding: 34px 0 20px 0;
    border-top: 1px solid #131318;
    margin-top: 44px;
}}
#credit b {{ color: #6E6E78; font-weight: 600; }}
"""

theme = gr.themes.Base(
    primary_hue=gr.themes.colors.pink,
    secondary_hue=gr.themes.colors.purple,
    neutral_hue=gr.themes.colors.gray,
    radius_size=gr.themes.sizes.radius_lg,
)


# ============================================================
#  UI
# ============================================================
with gr.Blocks(theme=theme, css=CSS, title="NED Regulations Assistant") as demo:

    gr.HTML(
        """
        <div id="app-header">
            <h1>NED Regulations Assistant</h1>
            <p>Grounded answers from the official regulations · Exact clause citations</p>
        </div>
        """
    )

    with gr.Row(elem_id="nav-bar"):
        nav_qa = gr.Button("Ask the regulations", variant="primary")
        nav_gpa = gr.Button("GPA calculator", variant="secondary")

    # ---------- PANEL 1 ----------
    with gr.Column(visible=True) as panel_qa:
        gr.Markdown(
            "<span style='color:#6E6E78;font-size:13px'>Attendance, CGPA, probation, "
            "grades, withdrawal and more. Answers come <b>only</b> from the official "
            "regulations. If it isn't in there, the assistant says so.</span>"
        )
        question_box = gr.Textbox(
            label="Your question",
            placeholder="What attendance do I need to sit an exam?",
            lines=2,
            elem_classes="sleek-input",
        )
        ask_button = gr.Button("Ask", elem_classes="grad-btn")
        answer_box = gr.Markdown(elem_id="answer-bubble")

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

    # ---------- PANEL 2 ----------
    with gr.Column(visible=False) as panel_gpa:
        gr.Markdown(
            "### Welcome, engineer — let me calculate your GPA.\n"
            "<span style='color:#6E6E78;font-size:13px'>Enter each course: name, what it's "
            "<b>out of</b>, marks <b>obtained</b>, and <b>credit hours</b>. Grades follow "
            "<b>clause 7.10</b>, the formula follows <b>clause 7.11</b>. Pure arithmetic — "
            "no AI involved, so the number is exact.</span>"
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

                **Total points = 68.4 · Total credit hours = 18**

                ### GPA = 68.4 ÷ 18 = **3.8**
                """
            )
            example_button = gr.Button("Load this example into the table", size="sm")

        course_table = gr.Dataframe(
            headers=["Course name", "Total marks", "Obtained marks", "Credit hours"],
            datatype=["str", "number", "number", "number"],
            row_count=(1, "dynamic"),
            column_count=(4, "fixed"),
            value=[["", None, None, None]],
            label="Your courses — click + below the table to add rows",
        )

        gpa_button = gr.Button("Calculate my GPA", elem_classes="grad-btn")
        gpa_summary = gr.Markdown(elem_id="gpa-summary")
        result_table = gr.Dataframe(
            headers=["Course", "Total", "Obtained", "%", "Grade", "Grade point", "Credit hrs", "Points earned"],
            label="Breakdown",
            interactive=False,
        )

        example_button.click(fn=load_example, outputs=course_table)
        gpa_button.click(fn=compute_gpa, inputs=course_table, outputs=[result_table, gpa_summary])

        gr.Markdown(
            "<span style='color:#5A5A64;font-size:12px'>"
            "<b>Notes:</b> A failing grade (<b>F</b>, below 50%) counts as <b>0.0</b> and "
            "<i>is</i> included — clause 7.10 note (iv). Grades W, WU, I, IP, X, P carry no "
            "grade points; don't enter them. This is <b>GPA</b> for one semester; CGPA spans "
            "several. The regulations specify <b>absolute</b> grading — if your department "
            "curves, your actual grade may differ. Boundaries use <code>&gt;=</code>: "
            "93.5% → A, 94% → A+.</span>"
        )

    nav_qa.click(fn=show_qa, outputs=[panel_qa, panel_gpa, nav_qa, nav_gpa])
    nav_gpa.click(fn=show_gpa, outputs=[panel_qa, panel_gpa, nav_qa, nav_gpa])

    gr.HTML(
        """
        <div id="credit">
            Developed by <b>Muhammad Umer Farooq</b> · Batch 2023<br>
            Computer Science &amp; Information Technology, NED University
        </div>
        """
    )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)