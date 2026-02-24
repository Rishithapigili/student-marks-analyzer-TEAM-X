from pydantic import BaseModel, ConfigDict
from typing import Optional


# ---------- Auth Schemas ----------

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "admin"  # Only admins register manually


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Student Mark Schemas ----------

class StudentMarkOut(BaseModel):
    id: int
    student_id: str       # real roll number e.g. "2210A31"
    student_name: str     # real student name
    time_study: float     # hours studied per day
    marks: float

    model_config = ConfigDict(from_attributes=True)


class StudentMarkUpdate(BaseModel):
    student_name: Optional[str] = None
    time_study: Optional[float] = None
    marks: Optional[float] = None


class StatsOut(BaseModel):
    average_marks: float
    average_study_time: float
    highest_marks: float
    lowest_marks: float


class ScorerOut(BaseModel):
    id: int
    student_id: str
    student_name: str
    time_study: float
    marks: float

    model_config = ConfigDict(from_attributes=True)


class MyMarksOut(BaseModel):
    student_id: str
    student_name: str
    time_study: float
    marks: float

    model_config = ConfigDict(from_attributes=True)
