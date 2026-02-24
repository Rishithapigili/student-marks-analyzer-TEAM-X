# Student Marks Analyzer (v2.0)

A premium, full-stack web application designed for analyzing and managing student mark records with interactive visualizations and role-based access control.

---

## 🚀 Key Features

- **Admin Dashboard**:
    - Manage student records (Add, Edit, Delete).
    - Bulk upload data via CSV/Excel.
    - View advanced analytics (Average, Highest, Lowest Marks).
    - Real-time performance distribution reports.
- **Student Portal**:
    - Personal marks profile with study time tracking.
    - Class-wide performance insights (Analytics & Graphs).
- **Interactive Visualizations**:
    - Live Chart.js bar charts and histograms.
    - Backend-generated static PNG reports for detailed analysis.
- **Premium Design**: Dark-themed SPA with glassmorphism, sticky sidebar, and Flaticon premium icons.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python), SQLAlchemy, SQLite, Pandas, Matplotlib.
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), Vanilla JavaScript.
- **Charts**: Chart.js 4.x.
- **Authentication**: JWT (JSON Web Tokens) with role-based access.

---

## 📦 Getting Started

### Prerequisites

- Python 3.9+
- A modern web browser.

### 1. Installation

Clone the repository and set up a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Server

Start the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`.

### 3. Accessing the Dashboard

Open your browser and navigate to:
👉 **[http://localhost:8000/static/index.html](http://localhost:8000/static/index.html)**

---

## 🔑 Login Credentials

### For Admin:
1. Register an admin account at `POST /auth/register` (using tools like Postman or Swagger UI at `/docs`).
2. Login with your registered username/password.

### For Student (Default Data):
- **Username**: `Ishaan Rao_2210A31`
- **Password**: `2210A31`  *(Roll Number serves as the default password)*

---

## 📁 Project Structure

```bash
Student_Marks_Analyzer/
├── main.py              # FastAPI Entry Point
├── models.py            # SQLAlchemy Database Models
├── schemas.py           # Pydantic Request/Response Models
├── database.py          # DB Connection Logic
├── routers/             # Authentication & Marks Endpoints
├── static/              # Frontend Assets
│   ├── index.html       # Single Page Application Shell
│   ├── style.css        # Premium UI Design
│   └── app.js           # Frontend Logic & API Integration
├── requirements.txt     # Backend Dependencies
└── marks.db             # SQLite Database (Auto-generated)
```

---

## 📊 Usage Tips

- **Reloading Data**: Use the 🔄 icon in the Admin header to reload the default dataset.
- **Uploading**: Admins can upload custom `.csv` files using the **+ Upload File** button.
- **Interactive Charts**: Hover over the live charts in the **Overview** tab for detailed values.
- **Static Reports**: Navigate to the **Reports** tab to view backend-generated distribution analyses.
