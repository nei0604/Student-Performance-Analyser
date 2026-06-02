import pandas as pd

PASS_MARK = 40  # Change this to whatever passing threshold you want
DIVIDER   = "=" * 50
LINE      = "-" * 50

# ── GRADE HELPER ──────────────────────────────────────────────────────────────
def get_grade(score):
    if   score >= 90: return 'A+'
    elif score >= 80: return 'A'
    elif score >= 70: return 'B'
    elif score >= 60: return 'C'
    elif score >= 50: return 'D'
    else:             return 'F'

# ── 1. LOAD DATA ──────────────────────────────────────────────────────────────
def load_data(filepath):
    df = pd.read_csv(filepath)
    df.columns = df.columns.str.strip()
    print(f"✅ Loaded {len(df)} students | Subjects: {list(df.columns[1:])}")
    return df

# ── 2. ENRICH DATA ────────────────────────────────────────────────────────────
def enrich(df):
    subjects = list(df.columns[1:])
    df['Total']   = df[subjects].sum(axis=1)
    df['Average'] = df[subjects].mean(axis=1).round(2)
    df['Rank']    = df['Total'].rank(ascending=False, method='min').astype(int)
    df['Status']  = df[subjects].apply(
        lambda row: 'PASS' if (row >= PASS_MARK).all() else 'FAIL', axis=1
    )
    for sub in subjects:
        df[f'{sub}_Grade'] = df[sub].apply(get_grade)
    df['Grade'] = df['Average'].apply(get_grade)
    df = df.sort_values('Rank').reset_index(drop=True)
    df.attrs['subjects'] = subjects   # set AFTER sort so it isn't wiped
    return df

# ── 3. TOPPER ─────────────────────────────────────────────────────────────────
def find_topper(df):
    topper = df.loc[df['Rank'] == 1].iloc[0]
    print("\n🏆  TOPPER")
    print(f"    {topper['Name']}  |  Total: {topper['Total']}  |  Avg: {topper['Average']}")

# ── 4. CLASS AVERAGE ──────────────────────────────────────────────────────────
def class_average(df):
    subjects = df.attrs['subjects']
    avg      = df[subjects].mean().round(2)
    overall  = df['Average'].mean().round(2)
    print("\n📊  CLASS AVERAGES")
    for sub, val in avg.items():
        print(f"    {sub:<12} {val}")
    print(f"    {'Overall':<12} {overall}")

# ── 5. SUBJECT-WISE PERFORMANCE ───────────────────────────────────────────────
def subject_performance(df):
    subjects = df.attrs['subjects']
    print("\n📚  SUBJECT-WISE PERFORMANCE")
    print(f"  {'Subject':<12} {'Mean':>6} {'Max':>6} {'Min':>6} {'Std':>6}")
    print("  " + "-" * 38)
    for sub in subjects:
        col = df[sub]
        print(f"  {sub:<12} {col.mean():>6.1f} {col.max():>6} {col.min():>6} {col.std():>6.1f}")

# ── 6. PASS / FAIL ANALYSIS ───────────────────────────────────────────────────
def pass_fail(df):
    subjects = df.attrs['subjects']
    counts   = df['Status'].value_counts()
    total    = len(df)
    print("\n✅❌  PASS / FAIL ANALYSIS")
    for status, count in counts.items():
        pct = round(count / total * 100, 1)
        print(f"    {status}: {count} students ({pct}%)")
    print("\n  Subject-wise failures:")
    for sub in subjects:
        failed = (df[sub] < PASS_MARK).sum()
        print(f"    {sub:<12}: {failed} failed")

# ── 7. GRADE REPORT ───────────────────────────────────────────────────────────
def grade_report(df):
    subjects = df.attrs['subjects']
    print("\n🎓  GRADE REPORT")
    header = f"  {'Name':<12}" + "".join(f"  {s[:8]:<10}" for s in subjects) + f"  {'Overall':<10}"
    print(header)
    print("  " + "-" * (12 + 12 * len(subjects) + 12))
    for _, row in df.iterrows():
        line = f"  {row['Name']:<12}"
        for sub in subjects:
            mark_grade = f"{str(row[sub]):>3}({row[f'{sub}_Grade']:<2})"
            line += f"  {mark_grade:<10}"
        line += f"  {str(row['Average']):>5}({row['Grade']:<2})"
        print(line)

# ── 8. LEADERBOARD ────────────────────────────────────────────────────────────
def leaderboard(df):
    print("\n🥇  STUDENT LEADERBOARD")
    print(f"  {'Rank':<6} {'Name':<12} {'Total':>7} {'Average':>9} {'Grade':<6} {'Status':<6}")
    print("  " + "-" * 48)
    for _, row in df.iterrows():
        print(f"  {row['Rank']:<6} {row['Name']:<12} {row['Total']:>7} {row['Average']:>9} {row['Grade']:<6} {row['Status']:<6}")

# ── 9. WEAKEST SUBJECT ALERT ──────────────────────────────────────────────────
def weakest_subject_alert(df):
    subjects = df.attrs['subjects']
    print("\n⚠️   WEAKEST SUBJECT ALERTS")
    print("  " + "-" * 48)
    for _, row in df.iterrows():
        weakest = min(subjects, key=lambda sub: row[sub])
        score   = row[weakest]
        grade   = row[f'{weakest}_Grade']
        if grade in ('F', 'D', 'C'):
            tag = "❌ needs urgent attention in"
        elif grade == 'B':
            tag = "📈 needs improvement in"
        else:
            tag = "✅ doing well, weakest is"
        print(f"  {row['Name']:<10} {tag} {weakest} ({score}, {grade})")

# ── 10. STUDENT LOOKUP ────────────────────────────────────────────────────────
def student_lookup(df):
    subjects = df.attrs['subjects']

    while True:
        name = input("\n🔍  Enter student name (or 'quit' to exit): ").strip()

        if name.lower() == 'quit':
            print("👋  Exiting lookup.")
            break

        match = df[df['Name'].str.lower() == name.lower()]

        if match.empty:
            all_names   = df['Name'].str.lower().tolist()
            suggestions = [df['Name'].iloc[i] for i, n in enumerate(all_names) if name.lower() in n]
            print(f"  ❌ '{name}' not found.")
            if suggestions:
                print(f"  💡 Did you mean: {', '.join(suggestions)}?")
            continue

        row = match.iloc[0]
        print("\n" + DIVIDER)
        print(f"  📋  REPORT CARD — {row['Name'].upper()}")
        print(DIVIDER)
        print(f"  {'Rank':<14} #{row['Rank']} out of {len(df)}")
        print(f"  {'Status':<14} {row['Status']}")
        print(f"  {'Overall Grade':<14} {row['Grade']}")
        print(f"  {'Total':<14} {row['Total']}")
        print(f"  {'Average':<14} {row['Average']}")
        print()
        print(f"  {'Subject':<12} {'Marks':>6} {'Grade':>6}")
        print("  " + "-" * 26)
        for sub in subjects:
            print(f"  {sub:<12} {row[sub]:>6} {row[f'{sub}_Grade']:>6}")
        print(DIVIDER)

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(DIVIDER)
    print("      🎓 STUDENT PERFORMANCE ANALYSER")
    print(DIVIDER)

    df = load_data("fetch.csv")
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

    df.to_csv("results.csv", index=False)
    print("💾  Full results saved to results.csv")
    print(DIVIDER)

    student_lookup(df)