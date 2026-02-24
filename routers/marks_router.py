import io
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from auth import get_admin_user, get_current_user, hash_password
from database import get_db
from models import StudentMark, User
from schemas import StudentMarkOut, StatsOut, ScorerOut, StudentMarkUpdate

router = APIRouter(prefix="/marks", tags=["Student Marks"])


# ──────────────────────────────────────────────
#  Helper: Load DataFrame from CSV or Excel
# ──────────────────────────────────────────────
def _read_file(file: UploadFile) -> pd.DataFrame:
    """Read an uploaded CSV or Excel file into a DataFrame."""
    filename = file.filename.lower()
    if filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file.file, engine="openpyxl")
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Upload a .csv or .xlsx file."
        )
    return df


# ──────────────────────────────────────────────
#  Upload CSV/Excel & auto-create student accounts
# ──────────────────────────────────────────────
@router.post("/upload", response_model=dict)
def upload_data(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """
    Admin uploads CSV/Excel file.
    Expected columns: Student Name, Student Roll Number, Marks, Time Studied Per Day (hrs)
    - Loads student marks into the database using real names and roll numbers.
    - Auto-creates student user accounts (username=Student Name, password=Roll Number).
    """
    df = _read_file(file)

    # Validate required columns
    required_cols = {"Student Name", "Student Roll Number", "Marks", "Time Studied Per Day (hrs)"}
    if not required_cols.issubset(set(df.columns)):
        raise HTTPException(
            status_code=400,
            detail=f"File must contain columns: {required_cols}. Found: {list(df.columns)}"
        )

    # Clear existing student marks and student user accounts
    db.query(StudentMark).delete()
    db.query(User).filter(User.role == "student").delete()
    db.commit()

    created_students = []

    for idx, row in df.iterrows():
        student_name = str(row["Student Name"]).strip()
        student_id = str(row["Student Roll Number"]).strip()

        # Create the student marks record
        mark_record = StudentMark(
            student_id=student_id,
            student_name=student_name,
            time_study=float(row["Time Studied Per Day (hrs)"]),
            marks=float(row["Marks"]),
        )
        db.add(mark_record)
        db.flush()  # Get the mark_record.id

        # Make username unique: "Student Name_RollNumber" (e.g. Ananya Gupta_2210A52)
        username = f"{student_name}_{student_id}"
        student_user = User(
            username=username,
            email=f"{student_id.lower()}@student.edu",
            password=hash_password(student_id),
            role="student"
        )
        db.add(student_user)
        db.flush()  # Get the student_user.id

        # Link mark to user
        mark_record.user_id = student_user.id

        created_students.append({
            "username": username,
            "password (roll number)": student_id
        })

    db.commit()

    return {
        "message": f"Loaded {len(df)} records. Created {len(created_students)} student accounts.",
        "student_credentials": created_students,
        "note": "Students login with username=<Student Name> and password=<Roll Number>"
    }


# ──────────────────────────────────────────────
#  Load from default CSV (admin only, backward compat)
# ──────────────────────────────────────────────
@router.post("/load-csv", response_model=dict)
def load_csv(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    """Load student_dataset_100_records.csv from project directory and auto-create student accounts."""
    csv_path = "student_dataset_100_records.csv"
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"{csv_path} not found in project directory")

    required_cols = {"Student Name", "Student Roll Number", "Marks", "Time Studied Per Day (hrs)"}
    if not required_cols.issubset(set(df.columns)):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain columns: {required_cols}. Found: {list(df.columns)}"
        )

    # Clear existing
    db.query(StudentMark).delete()
    db.query(User).filter(User.role == "student").delete()
    db.commit()

    created_students = []

    for idx, row in df.iterrows():
        student_name = str(row["Student Name"]).strip()
        student_id = str(row["Student Roll Number"]).strip()

        mark_record = StudentMark(
            student_id=student_id,
            student_name=student_name,
            time_study=float(row["Time Studied Per Day (hrs)"]),
            marks=float(row["Marks"]),
        )
        db.add(mark_record)
        db.flush()

        username = f"{student_name}_{student_id}"
        student_user = User(
            username=username,
            email=f"{student_id.lower()}@student.edu",
            password=hash_password(student_id),
            role="student"
        )
        db.add(student_user)
        db.flush()

        mark_record.user_id = student_user.id

        created_students.append({
            "username": username,
            "password (roll number)": student_id
        })

    db.commit()

    return {
        "message": f"Loaded {len(df)} records. Created {len(created_students)} student accounts.",
        "student_credentials": created_students[:5],
        "note": "Showing first 5. Students login with username=<Student Name>, password=<Roll Number>"
    }


# ──────────────────────────────────────────────
#  List all records (Admin only)
# ──────────────────────────────────────────────
@router.get("/", response_model=list[StudentMarkOut])
def get_all_marks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Return all student mark records. Accessible by all users for charts/analytics."""
    return db.query(StudentMark).all()


# ──────────────────────────────────────────────
#  Update record (Admin only)
# ──────────────────────────────────────────────
@router.patch("/{student_id}", response_model=StudentMarkOut)
def update_student_mark(
    student_id: str,
    mark_update: StudentMarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update a student mark record and its linked user account. Admin only."""
    student_record = db.query(StudentMark).filter(StudentMark.student_id == student_id).first()
    if not student_record:
        raise HTTPException(status_code=404, detail="Student record not found")

    # Update StudentMark record
    if mark_update.student_name is not None:
        student_record.student_name = mark_update.student_name
    if mark_update.time_study is not None:
        student_record.time_study = mark_update.time_study
    if mark_update.marks is not None:
        student_record.marks = mark_update.marks

    # If name changed, update linked User account username
    if mark_update.student_name is not None and student_record.user:
        new_username = f"{student_record.student_name}_{student_record.student_id}"
        # Check if username already exists for another user
        existing_user = db.query(User).filter(User.username == new_username, User.id != student_record.user_id).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Generated username already exists")
        student_record.user.username = new_username

    db.commit()
    db.refresh(student_record)
    return student_record


# ──────────────────────────────────────────────
#  Average statistics (Any authenticated user)
# ──────────────────────────────────────────────
@router.get("/average", response_model=StatsOut)
def get_average(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Calculate and return average marks, study time, highest and lowest marks. Accessible by all users."""
    result = db.query(
        func.avg(StudentMark.marks).label("average_marks"),
        func.avg(StudentMark.time_study).label("average_study_time"),
        func.max(StudentMark.marks).label("highest_marks"),
        func.min(StudentMark.marks).label("lowest_marks")
    ).first()

    return StatsOut(
        average_marks=round(result.average_marks or 0.0, 2),
        average_study_time=round(result.average_study_time or 0.0, 2),
        highest_marks=round(result.highest_marks or 0.0, 2),
        lowest_marks=round(result.lowest_marks or 0.0, 2)
    )


# ──────────────────────────────────────────────
#  Highest scorer (Any authenticated user)
# ──────────────────────────────────────────────
@router.get("/highest", response_model=ScorerOut)
def get_highest(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Return the student with the highest marks."""
    student = db.query(StudentMark).order_by(StudentMark.marks.desc()).first()
    if not student:
        raise HTTPException(status_code=404, detail="No records found. Load data first.")
    return student


# ──────────────────────────────────────────────
#  Lowest scorer (Any authenticated user)
# ──────────────────────────────────────────────
@router.get("/lowest", response_model=ScorerOut)
def get_lowest(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Return the student with the lowest marks."""
    student = db.query(StudentMark).order_by(StudentMark.marks.asc()).first()
    if not student:
        raise HTTPException(status_code=404, detail="No records found. Load data first.")
    return student


# ──────────────────────────────────────────────
#  Bar chart (Any authenticated user)
# ──────────────────────────────────────────────
@router.get("/bar-chart")
def get_bar_chart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate and return a bar chart of student marks as PNG."""
    students = db.query(StudentMark).all()
    if not students:
        raise HTTPException(status_code=404, detail="No records found. Load data first.")

    marks = [s.marks for s in students]
    indices = list(range(1, len(marks) + 1))

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(indices, marks, color="steelblue", edgecolor="black")
    ax.set_title("Student Marks - Bar Chart", fontsize=16, fontweight="bold")
    ax.set_xlabel("Student Index", fontsize=12)
    ax.set_ylabel("Marks", fontsize=12)
    ax.set_xticks(range(1, len(marks) + 1, 5))
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


# ──────────────────────────────────────────────
#  Histogram (Any authenticated user)
# ──────────────────────────────────────────────
@router.get("/histogram")
def get_histogram(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate and return a histogram of marks distribution as PNG."""
    students = db.query(StudentMark).all()
    if not students:
        raise HTTPException(status_code=404, detail="No records found. Load data first.")

    marks = [s.marks for s in students]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(marks, bins=15, color="coral", edgecolor="black", alpha=0.85)
    ax.set_title("Marks Distribution - Histogram", fontsize=16, fontweight="bold")
    ax.set_xlabel("Marks", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
