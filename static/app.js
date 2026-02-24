// Core App Logic
const BASE_URL = "https://student-marks-analyzer-fp4y.onrender.com";
let barChart = null;
let histChart = null;

// State
const state = {
    token: localStorage.getItem('token'),
    user: null, // {username, role}
    currentView: 'overview'
};

// --- DOM Elements ---
const loginSection = document.getElementById('login-section');
const dashboardSection = document.getElementById('dashboard-section');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const adminActions = document.getElementById('admin-actions');
const logoutBtn = document.getElementById('logout-btn');
const reloadBtn = document.getElementById('reload-btn'); // New Reload Icon
const marksTable = document.querySelector('#marks-table tbody');
const navLinks = document.querySelectorAll('.nav-links li');
const views = document.querySelectorAll('.view');
const editModal = document.getElementById('edit-modal');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    if (state.token) {
        verifySession();
    } else {
        showLogin();
    }
});

// --- Auth Functions ---
async function verifySession() {
    try {
        const res = await fetch(`${API_BASE}/auth/me`, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });

        if (res.ok) {
            const data = await res.json();
            state.user = {
                username: data.username,
                role: data.role,
                marks_details: data.marks_details
            };
            initDashboard();
        } else {
            logout();
        }
    } catch (e) {
        console.error("Session verification failed", e);
        logout();
    }
}

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    loginError.textContent = '';

    const formData = new FormData();
    formData.append('username', document.getElementById('username').value);
    formData.append('password', document.getElementById('password').value);

    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: formData
        });

        if (res.ok) {
            const data = await res.json();
            state.token = data.access_token;
            localStorage.setItem('token', state.token);
            verifySession();
        } else {
            const err = await res.json();
            loginError.textContent = err.detail || 'Login failed';
        }
    } catch (err) {
        loginError.textContent = 'Server unreachable';
    }
});

function logout() {
    localStorage.removeItem('token');
    state.token = null;
    state.user = null;
    location.reload();
}

logoutBtn.addEventListener('click', logout);

// --- UI Logic ---
function showLogin() {
    loginSection.classList.remove('hidden');
    dashboardSection.classList.add('hidden');
}

function initDashboard() {
    loginSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');

    document.getElementById('display-name').textContent = state.user.username;
    document.getElementById('display-role').textContent = state.user.role;

    // Load common analytics for everyone
    loadAnalytics();

    if (state.user.role === 'admin') {
        adminActions.classList.remove('hidden');
        document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
        document.querySelector('[data-view="data-table"]').classList.remove('hidden'); // Ensure table is visible for admin
        document.getElementById('student-info-bar').classList.add('hidden'); // Hide info bar for admin
        switchView('overview');
    } else {
        adminActions.classList.add('hidden');
        document.querySelectorAll('.admin-only').forEach(el => el.classList.add('hidden'));
        document.querySelector('[data-view="data-table"]').classList.add('hidden'); // Hide full table for student
        document.getElementById('student-info-bar').classList.remove('hidden'); // Show info bar for student
        showStudentView();
    }
}

async function loadAnalytics() {
    await fetchStats();
    // Cache total data for charts if admin, or just the student's data context
    const res = await fetch(`${API_BASE}/marks/`, {
        headers: { 'Authorization': `Bearer ${state.token}` }
    });
    if (res.ok) {
        state.allData = await res.json();
        renderCharts();
        if (state.user.role === 'admin') renderTable(state.allData);
    }
}

// Sidebar Navigation
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        const viewName = link.getAttribute('data-view');
        switchView(viewName);
        if (viewName === 'data-table') fetchTableData();
        if (viewName === 'reports') renderCharts(); // Refresh PNGs when report tab is opened
    });
});

function switchView(viewName) {
    navLinks.forEach(l => l.classList.remove('active'));
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

    views.forEach(v => v.classList.add('hidden'));
    document.getElementById(`${viewName}-view`).classList.remove('hidden');

    document.getElementById('view-title').textContent = viewName.charAt(0).toUpperCase() + viewName.slice(1).replace('-', ' ');
}

// --- Data Fetching & Rendering ---

async function loadFullAdminData() {
    await fetchStats();
    await fetchTableData();
    renderCharts();
}

async function fetchStats() {
    const res = await fetch(`${API_BASE}/marks/average`, {
        headers: { 'Authorization': `Bearer ${state.token}` }
    });
    if (res.ok) {
        const data = await res.json();
        document.getElementById('stat-avg-marks').textContent = data.average_marks;
        document.getElementById('stat-avg-time').textContent = data.average_study_time + ' hrs';
        document.getElementById('stat-highest').textContent = data.highest_marks;
        document.getElementById('stat-lowest').textContent = data.lowest_marks;
    }
}

async function fetchTableData() {
    if (state.user.role !== 'admin') return;
    const res = await fetch(`${API_BASE}/marks/`, {
        headers: { 'Authorization': `Bearer ${state.token}` }
    });
    if (res.ok) {
        const data = await res.json();
        renderTable(data);
        state.allData = data;
    }
}

function renderTable(data) {
    marksTable.innerHTML = '';
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row.student_id}</td>
            <td>${row.student_name}</td>
            <td>${row.marks}</td>
            <td>${row.time_study} hrs</td>
            <td class="admin-only ${state.user.role !== 'admin' ? 'hidden' : ''}">
                <button class="btn-edit" onclick="openEditModal('${row.student_id}', '${row.student_name}', ${row.marks}, ${row.time_study})">Edit</button>
            </td>
        `;
        marksTable.appendChild(tr);
    });
}

function showStudentView() {
    switchView('overview'); // Show graphs and stats by default
    document.querySelector('[data-view="overview"]').classList.add('active'); // Highlight overview tab

    if (state.user.marks_details) {
        const m = state.user.marks_details;
        document.getElementById('stu-name').textContent = m.student_name;
        document.getElementById('stu-id').textContent = m.student_id;
        document.getElementById('stu-marks').textContent = m.marks;
        document.getElementById('stu-time').textContent = m.time_study + ' hrs';
    }
}

// --- Charts ---
async function renderCharts() {
    if (!state.allData) return;

    // Update Backend Images (Authenticated Fetch)
    const timestamp = new Date().getTime();
    fetchAuthenticatedImage(`${API_BASE}/marks/histogram?t=${timestamp}`, 'histogram-img');
    fetchAuthenticatedImage(`${API_BASE}/marks/bar-chart?t=${timestamp}`, 'bar-chart-img');

    const marks = state.allData.map(d => d.marks);
    const labels = state.allData.map(d => d.student_name);

    if (barChart) barChart.destroy();
    if (histChart) histChart.destroy();

    const ctxBar = document.getElementById('barChart').getContext('2d');
    barChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: labels.slice(0, 10), // Top 10 for bar
            datasets: [{
                label: 'Student Marks',
                data: marks.slice(0, 10),
                backgroundColor: '#6366f1'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });

    const ctxHist = document.getElementById('histogramChart').getContext('2d');
    // Simple distribution grouping
    const bins = [0, 20, 40, 60, 80, 100];
    const binCounts = new Array(5).fill(0);
    marks.forEach(m => {
        for (let i = 0; i < 5; i++) {
            if (m >= bins[i] && m < bins[i + 1]) { binCounts[i]++; break; }
        }
    });

    histChart = new Chart(ctxHist, {
        type: 'bar',
        data: {
            labels: ['0-20', '20-40', '40-60', '60-80', '80-100'],
            datasets: [{
                label: 'Frequency',
                data: binCounts,
                backgroundColor: '#06b6d4'
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// --- Admin Actions ---

if (reloadBtn) {
    reloadBtn.addEventListener('click', async () => {
        const res = await fetch(`${API_BASE}/marks/load-csv`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (res.ok) loadAnalytics();
    });
}

document.getElementById('upload-btn').addEventListener('click', () => {
    document.getElementById('upload-csv-input').click();
});

document.getElementById('upload-csv-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/marks/upload`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${state.token}` },
        body: formData
    });

    if (res.ok) loadFullAdminData();
    else alert('Upload failed');
});

// --- Edit Modal Logic ---
window.openEditModal = (id, name, marks, time) => {
    document.getElementById('edit-id').value = id;
    document.getElementById('edit-name').value = name;
    document.getElementById('edit-marks').value = marks;
    document.getElementById('edit-time').value = time;
    editModal.classList.remove('hidden');
};

document.getElementById('close-modal').addEventListener('click', () => editModal.classList.add('hidden'));

async function fetchAuthenticatedImage(url, imgId) {
    try {
        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        if (res.ok) {
            const blobData = await res.blob();
            const objectURL = URL.createObjectURL(blobData);
            document.getElementById(imgId).src = objectURL;
        }
    } catch (e) {
        console.error("Image fetch failed", e);
    }
}

document.getElementById('edit-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('edit-id').value;
    const body = {
        student_name: document.getElementById('edit-name').value,
        marks: parseFloat(document.getElementById('edit-marks').value),
        time_study: parseFloat(document.getElementById('edit-time').value)
    };

    const res = await fetch(`${API_BASE}/marks/${id}`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${state.token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(body)
    });

    if (res.ok) {
        editModal.classList.add('hidden');
        loadFullAdminData();
    } else {
        alert('Update failed');
    }
});
