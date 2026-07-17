import gradio as gr
from rag import answer
from gpa import calculate_gpa


# ============================================================
#  LOGIC
# ============================================================
EMPTY_ANSWER = "*Ask a question to receive a cited regulation…*"


def ask(question):
    if not question or len(question.strip()) < 3:
        return "Please enter a real question (at least a few characters)."
    try:
        return answer(question.strip())
    except Exception:
        return "Something went wrong while processing your question. Please try again."


def thinking():
    return "<div class='dots'><span></span><span></span><span></span></div>"


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


def show_qa():
    return (gr.update(visible=True), gr.update(visible=False),
            gr.update(variant="primary"), gr.update(variant="secondary"))


def show_gpa():
    return (gr.update(visible=False), gr.update(visible=True),
            gr.update(variant="secondary"), gr.update(variant="primary"))


# ============================================================
#  STYLING
# ============================================================
MAGENTA = "#FF2E9F"
PURPLE = "#7B2FF7"

CSS = f"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {{
    font-family: 'Inter', system-ui, 'Segoe UI Emoji', 'Apple Color Emoji',
                 'Noto Color Emoji', sans-serif !important;
}}
html, body, gradio-app, #root, .app, .main, .contain {{ background: #000000 !important; }}

.gradio-container {{
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 0 40px !important;
    background: #000000 !important;
    color: #E0E0E0 !important;
}}
footer {{ display: none !important; }}
h1, h2, h3, h4 {{ text-transform: none !important; }}

/* ---------- HEADER ---------- */
#app-header {{ text-align: center; padding: 40px 0 8px 0; }}
#app-header h1 {{
    font-size: 30px; font-weight: 800; letter-spacing: 3px;
    text-transform: uppercase !important; margin: 0;
    background: linear-gradient(90deg, {MAGENTA} 0%, {PURPLE} 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}}
#app-header p {{ color: #5A5A64; font-size: 13px; margin: 12px 0 0 0; }}

/* ---------- NAV ---------- */
#nav-bar {{
    justify-content: center; gap: 14px;
    border-bottom: 1px solid #1C1C22;
    padding-bottom: 18px; margin-bottom: 36px;
}}
#nav-bar button {{
    background: transparent !important; border: none !important; box-shadow: none !important;
    font-size: 14px !important; font-weight: 700 !important;
    letter-spacing: 1.4px !important; text-transform: uppercase !important;
    padding: 10px 22px !important; max-width: 240px; transition: color 0.15s ease;
}}
#nav-bar button.secondary {{ color: #4A4A54 !important; }}
#nav-bar button.secondary:hover {{ color: #8A8A96 !important; }}
#nav-bar button.primary {{
    color: {MAGENTA} !important;
    text-shadow: 0 0 18px rgba(255, 46, 159, 0.45);
    border-bottom: 2px solid {MAGENTA} !important; border-radius: 0 !important;
}}

/* ---------- TEXT ---------- */
#qa-subtitle b, #qa-subtitle strong,
#gpa-subtitle b, #gpa-subtitle strong,
#gpa-notes b, #gpa-notes strong {{ color: inherit !important; font-weight: 700 !important; }}
#qa-subtitle, #gpa-subtitle {{
    color: #6E6E78 !important; font-size: 15px !important; line-height: 1.7;
    margin-bottom: 34px !important;
}}
#gpa-subtitle h3 {{
    color: #E0E0E0 !important; font-size: 21px !important;
    font-weight: 700 !important; margin-bottom: 14px !important;
}}
#gpa-notes {{ color: #5A5A64 !important; font-size: 13px !important; margin-top: 40px !important; }}
#gpa-notes ul {{ margin: 10px 0 0 0; padding-left: 18px; }}
#gpa-notes li {{ margin-bottom: 10px; line-height: 1.65; }}
#gpa-notes h4 {{
    color: #7A7A86 !important; font-size: 12px !important;
    letter-spacing: 1px; text-transform: uppercase !important;
    margin: 0 0 6px 0; font-weight: 700 !important;
}}

/* ---------- FIELD LABELS ---------- */
#question-label, #answer-label {{
    color: #C8C8D2 !important; font-size: 12px !important; font-weight: 700 !important;
    letter-spacing: 1.6px !important; text-transform: uppercase !important;
    margin: 0 0 14px 4px !important;
}}
#answer-label {{ margin-top: 40px !important; }}

/* ---------- BUTTONS ---------- */
.grad-btn {{
    background: linear-gradient(90deg, {MAGENTA} 0%, {PURPLE} 100%) !important;
    border: none !important; border-radius: 40px !important;
    color: #FFFFFF !important; font-weight: 600 !important;
    font-size: 15px !important; padding: 18px 0 !important;
    margin-top: 18px !important;
    box-shadow: 0 4px 24px rgba(255, 46, 159, 0.20) !important;
}}
.grad-btn:hover {{ filter: brightness(1.12); }}

.ghost-btn {{
    background: transparent !important; border: 1px solid {MAGENTA} !important;
    border-radius: 40px !important; color: {MAGENTA} !important;
    font-weight: 500 !important; font-size: 13px !important;
    padding: 11px 0 !important; box-shadow: none !important;
}}
.ghost-btn:hover {{ background: rgba(255, 46, 159, 0.08) !important; }}

/* ---------- INPUT: kill the gray container ---------- */
.sleek-input, .sleek-input > div, .sleek-input .block, .sleek-input .form,
.sleek-input .wrap, .sleek-input .container {{
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 0 !important;
}}
.sleek-input label {{
    background: transparent !important; border: none !important;
    display: block !important; padding: 0 !important;
}}
.sleek-input label > span {{ display: none !important; }}
.sleek-input textarea, .sleek-input input {{
    background: #08080C !important;
    border: 1px solid #1A1A22 !important;
    border-radius: 24px !important; color: #E0E0E0 !important;
    padding: 20px 24px !important; font-size: 16px !important; line-height: 1.6 !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}}
.sleek-input textarea:focus, .sleek-input input:focus {{
    border-color: {MAGENTA} !important;
    box-shadow: 0 0 0 3px rgba(255, 46, 159, 0.14) !important; outline: none !important;
}}

/* ---------- ANSWER ---------- */
#answer-bubble {{
    border: 1px solid transparent !important; border-radius: 26px !important;
    background:
        linear-gradient(#08080C, #08080C) padding-box,
        linear-gradient(120deg, {MAGENTA}, {PURPLE}) border-box !important;
    padding: 26px 30px !important; min-height: 84px;
}}
#answer-bubble p, #answer-bubble li {{
    color: #D8D8E0 !important; font-size: 15px !important; line-height: 1.75 !important;
}}
#answer-bubble em {{ color: #45454E !important; }}
#answer-bubble ul {{ margin: 4px 0 0 0; padding-left: 20px; }}
#answer-bubble li {{ margin-bottom: 12px; }}
#answer-bubble strong {{ color: {MAGENTA} !important; }}

/* loading dots */
.dots {{ display: flex; gap: 7px; align-items: center; padding: 6px 0; }}
.dots span {{
    width: 8px; height: 8px; border-radius: 50%;
    background: {MAGENTA}; opacity: 0.3;
    animation: pulse 1.3s infinite ease-in-out;
}}
.dots span:nth-child(2) {{ animation-delay: 0.18s; }}
.dots span:nth-child(3) {{ animation-delay: 0.36s; }}
@keyframes pulse {{
    0%, 80%, 100% {{ opacity: 0.25; transform: scale(0.85); }}
    40% {{ opacity: 1; transform: scale(1.1); }}
}}

/* ---------- EXAMPLES ---------- */
.gradio-container .examples button, .gradio-container button.example {{
    background: #08080C !important; border: 1px solid #1E1E26 !important;
    border-radius: 40px !important; color: #8A8A96 !important;
    font-size: 13px !important; padding: 10px 18px !important;
}}
.gradio-container .examples button:hover {{
    border-color: {MAGENTA} !important; color: {MAGENTA} !important;
}}

/* ---------- ACCORDION ---------- */
.gradio-container .accordion, .gradio-container details {{
    background: #08080C !important; border: 1px solid #1C1C22 !important;
    border-radius: 22px !important;
}}
#worked-example table {{
    display: block !important; overflow-x: auto !important;
    white-space: nowrap !important; -webkit-overflow-scrolling: touch;
    width: 100%; font-size: 13px !important;
}}
#worked-example table td, #worked-example table th {{
    white-space: nowrap !important; padding: 11px 14px !important;
}}
#worked-example h3 {{ font-size: 20px !important; color: {MAGENTA} !important; }}

/* ---------- TABLES: floating, hairline separators, no outer border ---------- */
.gradio-container table {{
    background: transparent !important; border: none !important;
    border-collapse: collapse !important; box-shadow: none !important;
}}
.gradio-container table thead th {{
    background: transparent !important; border: none !important;
    border-bottom: 1px solid #22222B !important; color: #5A5A64 !important;
    font-size: 11px !important; font-weight: 700 !important;
    letter-spacing: 0.8px; text-transform: uppercase; padding: 15px 16px !important;
}}
.gradio-container table tbody td {{
    background: transparent !important; border: none !important;
    border-bottom: 1px solid #121218 !important; color: #C8C8D2 !important;
    font-size: 14px !important; padding: 16px !important;
}}
.gradio-container table tbody tr:last-child td {{ border-bottom: none !important; }}
.gradio-container table tbody tr:hover td {{ background: #09090D !important; }}
.wrap.svelte-1cl284s, .block {{ background: transparent !important; border: none !important; }}

#gpa-summary h2 {{
    background: linear-gradient(90deg, {MAGENTA} 0%, {PURPLE} 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; font-size: 32px !important; margin-top: 26px !important;
}}
#gpa-summary p {{ font-size: 14px !important; color: #8A8A96 !important; }}

/* ---------- CREDIT ---------- */
#credit {{
    text-align: center; color: #7A7A86; font-size: 14px;
    padding: 38px 0 30px 0; border-top: 1px solid #1C1C22; margin-top: 56px;
}}
#credit a {{ text-decoration: none !important; color: #7A7A86 !important; transition: opacity 0.15s ease; }}
#credit a:hover {{ opacity: 0.75; }}
#credit a:hover b {{ text-shadow: 0 0 22px rgba(255, 46, 159, 0.6); }}
#credit b {{
    background: linear-gradient(90deg, {MAGENTA} 0%, {PURPLE} 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; font-weight: 700; font-size: 15px;
}}
#credit span {{ color: #4A4A54; font-size: 12px; }}

@media (max-width: 640px) {{
    .gradio-container {{ padding: 0 18px !important; }}
    #app-header h1 {{ font-size: 20px; letter-spacing: 1.5px; }}
    #nav-bar button {{ font-size: 12px !important; padding: 9px 8px !important; letter-spacing: 0.8px !important; }}
    #answer-bubble p, #answer-bubble li {{ font-size: 14px !important; }}
    .gradio-container table tbody td {{ font-size: 13px !important; padding: 12px !important; }}
}}
"""

theme = gr.themes.Base(
    primary_hue=gr.themes.colors.pink,
    secondary_hue=gr.themes.colors.purple,
    neutral_hue=gr.themes.colors.gray,
    radius_size=gr.themes.sizes.radius_lg,
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    font_mono=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
)


# ============================================================
#  UI
# ============================================================
with gr.Blocks(title="NED Regulations Assistant") as demo:

    gr.HTML(
        """
        <div id="app-header">
            <h1>NED REGULATIONS ASSISTANT</h1>
            <p>Grounded answers from the official regulations · Exact clause citations</p>
        </div>
        """
    )

    with gr.Row(elem_id="nav-bar"):
        nav_qa = gr.Button("Ask the question", variant="primary")
        nav_gpa = gr.Button("GPA calculator", variant="secondary")

    # ---------- PANEL 1 ----------
    with gr.Column(visible=True) as panel_qa:
        gr.Markdown(
            "Attendance, CGPA, probation, grades, withdrawal and more. Answers come "
            "**only** from the official regulations. If it isn't in there, the assistant says so.",
            elem_id="qa-subtitle",
        )

        gr.Markdown("Your Question", elem_id="question-label")
        question_box = gr.Textbox(
            label="", show_label=False,
            placeholder="What attendance do I need to sit an exam?",
            lines=2, elem_classes="sleek-input",
        )
        ask_button = gr.Button("Ask", elem_classes="grad-btn")

        gr.Markdown("Your Answer", elem_id="answer-label")
        answer_box = gr.Markdown(EMPTY_ANSWER, elem_id="answer-bubble")

        ask_button.click(fn=thinking, outputs=answer_box).then(
            fn=ask, inputs=question_box, outputs=answer_box
        )
        question_box.submit(fn=thinking, outputs=answer_box).then(
            fn=ask, inputs=question_box, outputs=answer_box
        )

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
            "### Welcome Engineer — Let Me Calculate Your GPA.\n\n"
            "Enter each course: name, what it's **out of**, marks **obtained**, and "
            "**credit hours**. Grades follow **clause 7.10**, the formula follows "
            "**clause 7.11**. Pure arithmetic — no AI involved, so the number is exact.",
            elem_id="gpa-subtitle",
        )

        with gr.Accordion("📋 See a worked example — a full semester", open=False, elem_id="worked-example"):
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
            example_button = gr.Button("Load this example into the table", size="sm", elem_classes="ghost-btn")

        course_table = gr.Dataframe(
            headers=["Course name", "Total marks", "Obtained marks", "Credit hours"],
            datatype=["str", "number", "number", "number"],
            row_count=(1, "dynamic"), column_count=(4, "fixed"),
            value=[["", None, None, None]],
            label="Your courses — click + below the table to add rows",
        )

        gpa_button = gr.Button("Calculate my GPA", elem_classes="grad-btn")
        gpa_summary = gr.Markdown(elem_id="gpa-summary")
        result_table = gr.Dataframe(
            headers=["Course", "Total", "Obtained", "%", "Grade", "Grade point", "Credit hrs", "Points earned"],
            label="Breakdown", interactive=False,
        )

        example_button.click(fn=load_example, outputs=course_table)
        gpa_button.click(fn=compute_gpa, inputs=course_table, outputs=[result_table, gpa_summary])

        gr.Markdown(
            """
#### Notes

- A failing grade (**F**, below 50%) counts as **0.0** and *is* included in your GPA — clause 7.10, note (iv). Calculators that drop failed courses inflate your GPA.
- Grades **W, WU, I, IP, X, P** carry no grade points and are excluded entirely (notes ii–iii). Don't enter them.
- This computes **GPA** for one semester. **CGPA** spans multiple semesters (clause 7.11).
- The regulations specify **absolute** grading. If your department curves, your actual grade may differ — this implements the regulation, not departmental practice.
- Boundaries use `>=`: 93.5% → A, 94% → A+.
            """,
            elem_id="gpa-notes",
        )

    nav_qa.click(fn=show_qa, outputs=[panel_qa, panel_gpa, nav_qa, nav_gpa])
    nav_gpa.click(fn=show_gpa, outputs=[panel_qa, panel_gpa, nav_qa, nav_gpa])

    gr.HTML(
        """
        <div id="credit">
            <a href="https://www.linkedin.com/in/mumerfarooq04/" target="_blank" rel="noopener noreferrer">
                Developed by <b>Muhammad Umer Farooq</b>
            </a><br>
            <span>Batch 2023 · Computer Science &amp; Information Technology · NED University</span>
        </div>
        """
    )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 7860))
    demo.launch(theme=theme, css=CSS, server_name="0.0.0.0", server_port=port)