from flask import Flask, request, jsonify, render_template
import pandas as pd
import io

from analyser import enrich, get_grade, PASS_MARK

app = Flask(__name__)

# ── HOME PAGE ─────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')

# ── ANALYSE ROUTE — receives CSV, returns JSON ────────────────────────────────
@app.route('/analyse', methods=['POST'])
def analyse():
    # 1. Read uploaded file
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    df = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
    df.columns = df.columns.str.strip()
    df = enrich(df)

    subjects = df.attrs['subjects']

    # 2. Topper
    topper_row = df.loc[df['Rank'] == 1].iloc[0]
    topper = {
        'name':    topper_row['Name'],
        'total':   int(topper_row['Total']),
        'average': float(topper_row['Average']),
        'grade':   topper_row['Grade']
    }

    # 3. Class averages
    class_avg = {sub: round(float(df[sub].mean()), 2) for sub in subjects}

    # 4. Subject-wise stats
    subject_stats = {
        sub: {
            'mean': round(float(df[sub].mean()), 2),
            'max':  int(df[sub].max()),
            'min':  int(df[sub].min()),
            'std':  round(float(df[sub].std()), 2),
        }
        for sub in subjects
    }

    # 5. Pass / Fail
    pass_count = int((df['Status'] == 'PASS').sum())
    fail_count = int((df['Status'] == 'FAIL').sum())

    # 6. Leaderboard
    leaderboard = []
    for _, row in df.iterrows():
        leaderboard.append({
            'rank':    int(row['Rank']),
            'name':    row['Name'],
            'total':   int(row['Total']),
            'average': float(row['Average']),
            'grade':   row['Grade'],
            'status':  row['Status'],
        })

    # 7. Weakest subject alerts
    alerts = []
    for _, row in df.iterrows():
        weakest = min(subjects, key=lambda sub: row[sub])
        score   = row[weakest]
        grade   = row[f'{weakest}_Grade']
        if grade in ('F', 'D', 'C'):
            tag = 'urgent'
        elif grade == 'B':
            tag = 'improve'
        else:
            tag = 'good'
        alerts.append({
            'name':    row['Name'],
            'subject': weakest,
            'score':   int(score),
            'grade':   grade,
            'tag':     tag,
        })

    # 8. Grade report (per student per subject)
    grade_report = []
    for _, row in df.iterrows():
        student = {'name': row['Name'], 'subjects': {}}
        for sub in subjects:
            student['subjects'][sub] = {
                'mark':  int(row[sub]),
                'grade': row[f'{sub}_Grade']
            }
        student['average'] = float(row['Average'])
        student['overall_grade'] = row['Grade']
        grade_report.append(student)

    return jsonify({
        'subjects':      subjects,
        'topper':        topper,
        'class_avg':     class_avg,
        'subject_stats': subject_stats,
        'pass_count':    pass_count,
        'fail_count':    fail_count,
        'leaderboard':   leaderboard,
        'alerts':        alerts,
        'grade_report':  grade_report,
        'total_students': len(df),
    })

# ── STUDENT LOOKUP ROUTE ──────────────────────────────────────────────────────
@app.route('/lookup', methods=['POST'])
def lookup():
    data     = request.json
    name     = data.get('name', '').strip().lower()
    students = data.get('students', [])

    match = [s for s in students if s['name'].lower() == name]
    if not match:
        suggestions = [s['name'] for s in students if name in s['name'].lower()]
        return jsonify({'error': f"'{data.get('name')}' not found.", 'suggestions': suggestions})

    return jsonify({'student': match[0]})

if __name__ == '__main__':
    app.run(debug=True)
