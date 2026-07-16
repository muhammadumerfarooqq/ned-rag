"""Deterministic GPA calculator for NED University.

NO LLM. Pure arithmetic. Grade points read directly from clause 7.10 of the
academic regulations. LLMs are unreliable at arithmetic and a wrong CGPA is
worse than no feature.
"""

# Clause 7.10 — Grade / Grade Point equated with percentage of marks.
# (minimum_percentage, letter, grade_point) — ordered high to low.
GRADE_TABLE = [
    (94, "A+", 4.0),
    (85, "A",  4.0),
    (80, "A-", 3.7),
    (75, "B+", 3.4),
    (70, "B",  3.0),
    (67, "B-", 2.7),
    (64, "C+", 2.4),
    (60, "C",  2.0),
    (57, "C-", 1.7),
    (54, "D+", 1.4),
    (50, "D",  1.0),
    (0,  "F",  0.0),   # note (iv): F IS counted toward GPA/CGPA
]


def marks_to_grade(percentage: float):
    """Map a percentage to (letter, grade_point) per clause 7.10."""
    for threshold, letter, point in GRADE_TABLE:
        if percentage >= threshold:
            return letter, point
    return "F", 0.0


def calculate_gpa(courses):
    """courses: list of dicts with keys: name, total, obtained, credits.

    Returns (rows, gpa, total_credits, total_points).
    GPA = sum(credit_hours * grade_point) / sum(credit_hours)   [clause 7.11]
    """
    rows = []
    total_points = 0.0
    total_credits = 0.0

    for c in courses:
        pct = (c["obtained"] / c["total"]) * 100.0
        letter, point = marks_to_grade(pct)
        weighted = point * c["credits"]
        total_points += weighted
        total_credits += c["credits"]
        rows.append([
            c["name"],
            c["total"],
            c["obtained"],
            round(pct, 2),
            letter,
            point,
            c["credits"],
            round(weighted, 2),
        ])

    gpa = total_points / total_credits if total_credits else 0.0
    return rows, round(gpa, 2), total_credits, round(total_points, 2)


if __name__ == "__main__":
    tests = [
        {"name": "Pre Production", "total": 100, "obtained": 80,  "credits": 3},
        {"name": "Game Design",    "total": 150, "obtained": 130, "credits": 4},
    ]
    rows, gpa, credits, points = calculate_gpa(tests)
    for r in rows:
        print(r)
    print(f"\ntotal credits = {credits}, total points = {points}")
    print(f"GPA = {gpa}")

    # boundary checks
    for pct in [100, 94, 93.5, 93, 85, 84.9, 80, 75, 70, 67, 64, 60, 57, 54, 50, 49.9, 0]:
        print(f"{pct:6} -> {marks_to_grade(pct)}")