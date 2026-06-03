# 🎓 Student Performance Analyser

A Python + Flask project that reads student marks from a CSV file and analyses
class performance — through both a terminal CLI and a full web interface.

---

## 📁 Project Structure

```
student_analyser/
  ├── analyser.py          # Core analysis logic (pandas)
  ├── app.py               # Flask web server (backend)
  ├── fetch.csv            # Your student data
  ├── results.csv          # Auto-generated after running analyser.py
  ├── README.md            # This file
  ├── templates/
  │     └── index.html     # The webpage (frontend HTML)
  └── static/
        ├── style.css      # Styling
        └── main.js        # Frontend logic (charts, tables, lookup)
```

---

## 📄 CSV Format

Your CSV file must have a `Name` column first, followed by subject columns:

```
Name, Math, Physics, English
Aman, 85, 90, 78
Priya, 92, 88, 95
Rahul, 70, 75, 80
```

- Any number of subjects is supported
- Pass mark is set to **40** by default (change `PASS_MARK` in `analyser.py`)

---

## ⚙️ Requirements

Install dependencies before running:

```bash
pip install pandas flask
```

---

## 🖥️ Option 1 — Run in Terminal (CLI)

```bash
python analyser.py
```

What it prints:
- 🏆 Topper
- 📊 Class averages
- 📚 Subject-wise performance (mean, max, min, std)
- ✅❌ Pass / Fail analysis
- 🎓 Grade report with letter grades per subject
- 🥇 Ranked leaderboard
- ⚠️ Weakest subject alerts
- 🔍 Interactive student lookup (type a name, get their report card)

A `results.csv` file is also saved with all enriched data (Total, Average, Rank, Grade, Status).

---

## 🌐 Option 2 — Run as a Website (Flask)

**Step 1** — Open terminal inside your `student_analyser` folder:
- **Windows:** open the folder → click the address bar → type `cmd` → Enter
- **Mac:** right-click the folder → New Terminal at Folder

**Step 2** — Start the Flask server:
```bash
python app.py
```

**Step 3** — Open your browser and go to:
```
http://127.0.0.1:5000
```

**Step 4** — Upload your CSV file and see the full dashboard!

---

## 🔢 Grade Scale

| Marks  | Grade |
|--------|-------|
| 90–100 | A+    |
| 80–89  | A     |
| 70–79  | B     |
| 60–69  | C     |
| 50–59  | D     |
| Below 50 | F  |

---

## 📦 File Breakdown

### `analyser.py`
The core brain of the project. Contains all analysis logic using `pandas`.

| Function | What it does |
|---|---|
| `get_grade(score)` | Returns letter grade for a given score |
| `load_data(filepath)` | Reads CSV into a pandas DataFrame |
| `enrich(df)` | Adds Total, Average, Rank, Status, Grade columns |
| `find_topper(df)` | Prints the student with the highest total |
| `class_average(df)` | Prints average per subject and overall |
| `subject_performance(df)` | Prints mean, max, min, std per subject |
| `pass_fail(df)` | Prints pass/fail counts and per-subject failures |
| `grade_report(df)` | Prints mark + grade per student per subject |
| `leaderboard(df)` | Prints ranked table of all students |
| `weakest_subject_alert(df)` | Flags each student's weakest subject |
| `student_lookup(df)` | Interactive search — type a name, get report card |

---

### `app.py`
The Flask backend. Connects Python to the browser.

| Route | Method | What it does |
|---|---|---|
| `/` | GET | Serves the homepage (`index.html`) |
| `/analyse` | POST | Receives uploaded CSV, runs analysis, returns JSON |
| `/lookup` | POST | Receives a student name, returns their data |

---

### `templates/index.html`
The webpage structure. Contains:
- Upload box (drag & drop supported)
- Stat cards (topper, class average, pass rate, total students)
- Subject averages bar chart
- Pass/Fail doughnut chart
- Grade report table
- Leaderboard table
- Weakest subject alerts
- Student lookup with search box

---

### `static/style.css`
All the styling for the website — colors, layout, badges, tables, charts.

---

### `static/main.js`
Frontend JavaScript. Handles:
- CSV file upload (including drag & drop)
- Sending the file to Flask via `fetch()`
- Receiving JSON from Flask
- Building all charts using **Chart.js**
- Rendering all tables and alerts dynamically
- Student lookup search

---

## 🛠️ Things You Can Customise

| What | Where | How |
|---|---|---|
| Pass mark threshold | `analyser.py` line 3 | Change `PASS_MARK = 40` to any number |
| Grade scale | `analyser.py` `get_grade()` | Adjust the score ranges |
| CSV filename (CLI) | `analyser.py` line 162 | Change `"fetch.csv"` to your filename |
| Chart colors | `static/main.js` | Edit the `COLORS` array |

---

## 💡 How the Web Version Works

```
1. You upload a CSV in the browser
2. main.js sends it to Flask at /analyse
3. Flask reads it with pandas, runs enrich()
4. Flask sends back all results as JSON
5. main.js receives the JSON
6. main.js builds charts, tables, and alerts from the JSON
```

The browser never runs Python — Flask is the bridge between your Python
analysis and the webpage.

---

## 🚀 Built With

- [Python](https://python.org) — core language
- [pandas](https://pandas.pydata.org) — data analysis
- [Flask](https://flask.palletsprojects.com) — web framework
- [Chart.js](https://chartjs.org) — charts in the browser
- HTML + CSS + JavaScript — frontend
