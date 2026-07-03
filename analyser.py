"""
Student Performance Analyser
=============================
Reads student marks from a CSV file, calculates totals/averages/grades/ranks,
and prints a set of reports (topper, class average, leaderboard, etc.)

Expected CSV format:
    Name, Subject1, Subject2, Subject3, ...
"""

import pandas as pd

# ── CONFIG ─────────────────────────────────────────────────────────────────
PASS_MARK = 40          # Minimum mark needed in EVERY subject to "PASS"
INPUT_FILE = "fetch.csv"
OUTPUT_FILE = "results.csv"

DIVIDER = "=" * 50      # Used for big section breaks
LINE = "-" * 50         # Used for smaller separators


# ── GRADE HELPER ───────────────────────────────────────────────────────────
def get_grade(score):
    """Convert a numeric score into a letter grade."""
    if score >= 85:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'


# ── 1. LOAD DATA ───────────────────────────────────────────────────────────
def load_data(filepath):
    """Read the CSV file and clean up column names (strip stray whitespace)."""
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()

    subject_columns = list(df.columns[1:])  # everything after "Name"
    print(f"✅ Loaded {len(df)} students | Subjects: {subject_columns}")
    return df


# ── 2. ENRICH DATA ─────────────────────────────────────────────────────────
def enrich(df):
    """
    Add calculated columns to the dataframe:
    Total, Average, Rank, Status (PASS/FAIL), per-subject grades, overall grade.
    """
    subjects = list(df.columns[1:])

    df['Total'] = df[subjects].sum(axis=1)
    df['Average'] = df[subjects].mean(axis=1).round(2)

    # Rank 1 = highest total. method='min' means tied scores share the same rank.
    df['Rank'] = df['Total'].rank(ascending=False, method='min').astype(int)

    # A student only "PASSES" if EVERY subject is above PASS_MARK.
    df['Status'] = df[subjects].apply(
        lambda row: 'PASS' if (row >= PASS_MARK).all() else 'FAIL', axis=1
    )

    # Per-subject letter grade (e.g. "Math_Grade")
    for subject in subjects:
        df[f'{subject}_Grade'] = df[subject].apply(get_grade)

    # Overall letter grade, based on average score
    df['Grade'] = df['Average'].apply(get_grade)

    # Sort by rank so every later report is already in leaderboard order
    df = df.sort_values('Rank').reset_index(drop=True)

    # Stash the subject list on the dataframe itself so other functions
    # don't need to know which columns are "real" subjects vs calculated ones.
    # NOTE: must be set AFTER sort_values, since some pandas operations
    # silently drop .attrs metadata.
    df.attrs['subjects'] = subjects
    return df


# ── 3. TOPPER ──────────────────────────────────────────────────────────────
def find_topper(df):
    """Print the student with Rank == 1."""
    topper = df.loc[df['Rank'] == 1].iloc[0]
    print("\n🏆  TOPPER")
    print(f"    {topper['Name']}  |  Total: {topper['Total']}  |  Avg: {topper['Average']}")


# ── 4. CLASS AVERAGE ───────────────────────────────────────────────────────
def class_average(df):
    """Print the average score per subject, plus the overall class average."""
    subjects = df.attrs['subjects']
    subject_averages = df[subjects].mean().round(2)
    overall_average = df['Average'].mean().round(2)

    print("\n📊  CLASS AVERAGES")
    for subject, avg in subject_averages.items():
        print(f"    {subject:<12} {avg}")
    print(f"    {'Overall':<12} {overall_average}")


# ── 5. SUBJECT-WISE PERFORMANCE ────────────────────────────────────────────
def subject_performance(df):
    """Print mean / max / min / std-dev for each subject."""
    subjects = df.attrs['subjects']

    print("\n📚  SUBJECT-WISE PERFORMANCE")
    print(f"  {'Subject':<12} {'Mean':>6} {'Max':>6} {'Min':>6} {'Std':>6}")
    print("  " + "-" * 38)

    for subject in subjects:
        col = df[subject]
        print(f"  {subject:<12} {col.mean():>6.1f} {col.max():>6} {col.min():>6} {col.std():>6.1f}")


# ── 6. PASS / FAIL ANALYSIS ────────────────────────────────────────────────
def pass_fail(df):
    """Print overall pass/fail counts, plus a per-subject failure breakdown."""
    subjects = df.attrs['subjects']
    status_counts = df['Status'].value_counts()
    total_students = len(df)

    print("\n✅❌  PASS / FAIL ANALYSIS")
    for status, count in status_counts.items():
        percentage = round(count / total_students * 100, 1)
        print(f"    {status}: {count} students ({percentage}%)")

    print("\n  Subject-wise failures:")
    for subject in subjects:
        failed_count = (df[subject] < PASS_MARK).sum()
        print(f"    {subject:<12}: {failed_count} failed")


# ── 7. GRADE REPORT ─────────────────────────────────────────────────────────
def grade_report(df):
    """Print a table of marks + grade for every subject, for every student."""
    subjects = df.attrs['subjects']

    print("\n🎓  GRADE REPORT")
    header = f"  {'Name':<12}" + "".join(f"  {s[:8]:<10}" for s in subjects) + f"  {'Overall':<10}"
    print(header)
    print("  " + "-" * (12 + 12 * len(subjects) + 12))

    for _, student in df.iterrows():
        line = f"  {student['Name']:<12}"
        for subject in subjects:
            mark_and_grade = f"{str(student[subject]):>3}({student[f'{subject}_Grade']:<2})"
            line += f"  {mark_and_grade:<10}"
        line += f"  {str(student['Average']):>5}({student['Grade']:<2})"
        print(line)


# ── 8. LEADERBOARD ──────────────────────────────────────────────────────────
def leaderboard(df):
    """Print a simple ranked leaderboard of all students."""
    print("\n🥇  STUDENT LEADERBOARD")
    print(f"  {'Rank':<6} {'Name':<12} {'Total':>7} {'Average':>9} {'Grade':<6} {'Status':<6}")
    print("  " + "-" * 48)

    for _, student in df.iterrows():
        print(f"  {student['Rank']:<6} {student['Name']:<12} {student['Total']:>7} "
              f"{student['Average']:>9} {student['Grade']:<6} {student['Status']:<6}")


# ── 9. WEAKEST SUBJECT ALERT ────────────────────────────────────────────────
def weakest_subject_alert(df):
    """
    For each student, flag their weakest subject and how concerning it is
    (based on the grade they got in that subject).
    """
    subjects = df.attrs['subjects']

    print("\n⚠️   WEAKEST SUBJECT ALERTS")
    print("  " + "-" * 48)

    for _, student in df.iterrows():
        weakest_subject = min(subjects, key=lambda subject: student[subject])
        score = student[weakest_subject]
        grade = student[f'{weakest_subject}_Grade']

        if grade in ('F', 'D', 'C'):
            tag = "❌ needs urgent attention in"
        elif grade == 'B':
            tag = "📈 needs improvement in"
        else:
            tag = "✅ doing well, weakest is"

        print(f"  {student['Name']:<10} {tag} {weakest_subject} ({score}, {grade})")


# ── 10. STUDENT LOOKUP (interactive) ────────────────────────────────────────
def student_lookup(df):
    """
    Interactive loop: type a student's name to see their full report card.
    Type 'quit' to exit. Suggests close matches if the name isn't found.
    """
    subjects = df.attrs['subjects']

    while True:
        name = input("\n🔍  Enter student name (or 'quit' to exit): ").strip()

        if name.lower() == 'quit':
            print("👋  Exiting lookup.")
            break

        match = df[df['Name'].str.lower() == name.lower()]

        if match.empty:
            _print_not_found(df, name)
            continue

        student = match.iloc[0]
        _print_report_card(student, subjects, total_students=len(df))


def _print_not_found(df, searched_name):
    """Helper for student_lookup: shows close-match suggestions when a name isn't found."""
    all_names = df['Name'].str.lower().tolist()
    suggestions = [
        df['Name'].iloc[i] for i, name in enumerate(all_names)
        if searched_name.lower() in name
    ]

    print(f"  ❌ '{searched_name}' not found.")
    if suggestions:
        print(f"  💡 Did you mean: {', '.join(suggestions)}?")


def _print_report_card(student, subjects, total_students):
    """Helper for student_lookup: prints one student's full report card."""
    print("\n" + DIVIDER)
    print(f"  📋  REPORT CARD — {student['Name'].upper()}")
    print(DIVIDER)
    print(f"  {'Rank':<14} #{student['Rank']} out of {total_students}")
    print(f"  {'Status':<14} {student['Status']}")
    print(f"  {'Overall Grade':<14} {student['Grade']}")
    print(f"  {'Total':<14} {student['Total']}")
    print(f"  {'Average':<14} {student['Average']}")
    print()
    print(f"  {'Subject':<12} {'Marks':>6} {'Grade':>6}")
    print("  " + "-" * 26)
    for subject in subjects:
        print(f"  {subject:<12} {student[subject]:>6} {student[f'{subject}_Grade']:>6}")
    print(DIVIDER)


# ── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    print(DIVIDER)
    print("      🎓 STUDENT PERFORMANCE ANALYSER")
    print(DIVIDER)

    df = load_data(INPUT_FILE)
    df = enrich(df)

    print(DIVIDER)
    find_topper(df)
    class_average(df)
    subject_performance(df)
    pass_fail(df)
    grade_report(df)
    leaderboard(df)
    weakest_subject_alert(df)
    print("\n" + DIVIDER)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"💾  Full results saved to {OUTPUT_FILE}")
    print(DIVIDER)

    student_lookup(df)


if __name__ == "__main__":
    main()