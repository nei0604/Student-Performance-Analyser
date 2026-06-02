// ── STATE ─────────────────────────────────────────────────────────────────────
let appData = null;   // stores full analysis result for lookup use
let subjectChart   = null;
let passFailChart  = null;

// ── FILE UPLOAD ───────────────────────────────────────────────────────────────
const csvInput  = document.getElementById('csv-input');
const uploadBox = document.getElementById('upload-box');

csvInput.addEventListener('change', e => {
  if (e.target.files[0]) uploadFile(e.target.files[0]);
});

// drag and drop support
uploadBox.addEventListener('dragover',  e => { e.preventDefault(); uploadBox.classList.add('drag-over'); });
uploadBox.addEventListener('dragleave', () => uploadBox.classList.remove('drag-over'));
uploadBox.addEventListener('drop', e => {
  e.preventDefault();
  uploadBox.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.name.endsWith('.csv')) uploadFile(file);
});

function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  fetch('/analyse', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
      if (data.error) { alert(data.error); return; }
      appData = data;
      renderAll(data);
      document.getElementById('results').classList.remove('hidden');
      document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    })
    .catch(() => alert('Something went wrong. Please try again.'));
}

// ── RENDER ALL ────────────────────────────────────────────────────────────────
function renderAll(data) {
  renderCards(data);
  renderSubjectChart(data);
  renderPassFailChart(data);
  renderGradeReport(data);
  renderLeaderboard(data);
  renderAlerts(data);
}

// ── STAT CARDS ────────────────────────────────────────────────────────────────
function renderCards(data) {
  const container = document.getElementById('stat-cards');
  const overallAvg = (data.leaderboard.reduce((s, r) => s + r.average, 0) / data.total_students).toFixed(2);

  const cards = [
    { label: 'Total Students', value: data.total_students, sub: `${data.subjects.length} subjects` },
    { label: 'Topper',         value: data.topper.name,    sub: `${data.topper.total} total · ${data.topper.grade}` },
    { label: 'Class Average',  value: overallAvg,          sub: 'across all subjects' },
    { label: 'Pass Rate',      value: `${Math.round(data.pass_count / data.total_students * 100)}%`, sub: `${data.pass_count} of ${data.total_students} passed` },
  ];

  container.innerHTML = cards.map(c => `
    <div class="card">
      <div class="card-label">${c.label}</div>
      <div class="card-value">${c.value}</div>
      <div class="card-sub">${c.sub}</div>
    </div>
  `).join('');
}

// ── SUBJECT CHART ─────────────────────────────────────────────────────────────
const COLORS = ['#4f46e5', '#7c3aed', '#db2777', '#059669', '#d97706', '#0891b2'];

function renderSubjectChart(data) {
  if (subjectChart) subjectChart.destroy();
  const ctx = document.getElementById('subjectChart').getContext('2d');
  subjectChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.subjects,
      datasets: [{
        data: data.subjects.map(s => data.class_avg[s]),
        backgroundColor: COLORS.slice(0, data.subjects.length),
        borderRadius: 6,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: { y: { min: 0, max: 100, ticks: { stepSize: 20 } } }
    }
  });
}

// ── PASS FAIL CHART ───────────────────────────────────────────────────────────
function renderPassFailChart(data) {
  if (passFailChart) passFailChart.destroy();
  const ctx = document.getElementById('passFailChart').getContext('2d');
  passFailChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Pass', 'Fail'],
      datasets: [{
        data: [data.pass_count, data.fail_count],
        backgroundColor: ['#059669', '#dc2626'],
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      cutout: '65%',
    }
  });
}

// ── GRADE REPORT TABLE ────────────────────────────────────────────────────────
function gradeBadge(g) {
  const cls = g === 'A+' ? 'Aplus' : g;
  return `<span class="grade grade-${cls}">${g}</span>`;
}

function renderGradeReport(data) {
  const head = document.getElementById('grade-head');
  const body = document.getElementById('grade-body');

  head.innerHTML = `<tr>
    <th>Name</th>
    ${data.subjects.map(s => `<th>${s}</th>`).join('')}
    <th>Overall</th>
  </tr>`;

  body.innerHTML = data.grade_report.map(s => `
    <tr>
      <td><strong>${s.name}</strong></td>
      ${data.subjects.map(sub => `
        <td>${s.subjects[sub].mark} ${gradeBadge(s.subjects[sub].grade)}</td>
      `).join('')}
      <td>${s.average} ${gradeBadge(s.overall_grade)}</td>
    </tr>
  `).join('');
}

// ── LEADERBOARD ───────────────────────────────────────────────────────────────
function rankBadge(r) {
  if (r <= 3) return `<span class="rank-${r}">#${r}</span>`;
  return `#${r}`;
}

function renderLeaderboard(data) {
  document.getElementById('leaderboard-body').innerHTML = data.leaderboard.map(s => `
    <tr>
      <td>${rankBadge(s.rank)}</td>
      <td><strong>${s.name}</strong></td>
      <td>${s.total}</td>
      <td>${s.average}</td>
      <td>${gradeBadge(s.grade)}</td>
      <td class="status-${s.status.toLowerCase()}">${s.status}</td>
    </tr>
  `).join('');
}

// ── ALERTS ────────────────────────────────────────────────────────────────────
function renderAlerts(data) {
  const icons = { urgent: '❌', improve: '📈', good: '✅' };
  const messages = {
    urgent:  'needs urgent attention in',
    improve: 'needs improvement in',
    good:    'doing well, weakest is',
  };

  document.getElementById('alerts-list').innerHTML = data.alerts.map(a => `
    <div class="alert-item alert-${a.tag}">
      <span>${icons[a.tag]}</span>
      <span class="alert-name">${a.name}</span>
      <span>${messages[a.tag]} <strong>${a.subject}</strong> (${a.score}, ${a.grade})</span>
    </div>
  `).join('');
}

// ── STUDENT LOOKUP ────────────────────────────────────────────────────────────
function lookupStudent() {
  const name   = document.getElementById('lookup-input').value.trim();
  const result = document.getElementById('lookup-result');
  if (!name || !appData) return;

  const match = appData.leaderboard.find(s => s.name.toLowerCase() === name.toLowerCase());
  const gradeInfo = appData.grade_report.find(s => s.name.toLowerCase() === name.toLowerCase());

  if (!match) {
    const suggestions = appData.leaderboard
      .filter(s => s.name.toLowerCase().includes(name.toLowerCase()))
      .map(s => s.name);
    result.innerHTML = `
      <p class="lookup-error">❌ '${name}' not found.</p>
      ${suggestions.length ? `<p class="lookup-suggest">💡 Did you mean: ${suggestions.join(', ')}?</p>` : ''}
    `;
    return;
  }

  const subjectRows = appData.subjects.map(sub => `
    <div class="lookup-row-item">
      <span>${sub}</span>
      <span>${gradeInfo.subjects[sub].mark} ${gradeBadge(gradeInfo.subjects[sub].grade)}</span>
    </div>
  `).join('');

  result.innerHTML = `
    <div class="lookup-card">
      <h3>📋 ${match.name}</h3>
      <div class="lookup-row-item"><span>Rank</span><span>${rankBadge(match.rank)} out of ${appData.total_students}</span></div>
      <div class="lookup-row-item"><span>Status</span><span class="status-${match.status.toLowerCase()}">${match.status}</span></div>
      <div class="lookup-row-item"><span>Overall Grade</span><span>${gradeBadge(match.grade)}</span></div>
      <div class="lookup-row-item"><span>Total</span><span>${match.total}</span></div>
      <div class="lookup-row-item"><span>Average</span><span>${match.average}</span></div>
      ${subjectRows}
    </div>
  `;
}

// allow pressing Enter in lookup input
document.getElementById('lookup-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') lookupStudent();
});
