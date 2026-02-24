from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate, Token, MyMarksOut
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_student_user
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ---------------- REGISTER (Admin/Teacher Only) ----------------
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new admin (teacher) account. Students are auto-created when CSV/Excel is loaded."""
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    if user.role not in ("admin",):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only admin (teacher) accounts can be registered manually. Student accounts are auto-created on data upload."
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role="admin"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": f"Admin '{user.username}' registered successfully"}


# ---------------- LOGIN ----------------
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with username and password. For students: username=student name, password=student ID."""
    db_user = db.query(User).filter(User.username == form_data.username).first()

    if not db_user or not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token = create_access_token(data={"sub": db_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------------- ME (Common) ----------------
@router.get("/me")
def read_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile and marks (if student). Accessible by all logged-in users."""
    response = {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
    }

    if current_user.marks:
        m = current_user.marks
        response["marks_details"] = {
            "student_id": m.student_id,
            "student_name": m.student_name,
            "time_study": m.time_study,
            "marks": m.marks
        }
    
    return response
