from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")  # "student" or "admin"

    # A student user has one linked marks record
    marks = relationship("StudentMark", back_populates="user", uselist=False)


class StudentMark(Base):
    __tablename__ = "student_marks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, unique=True, nullable=False)  # e.g. "2210A31" (real roll number)
    student_name = Column(String, nullable=False)             # real student name
    time_study = Column(Float, nullable=False)                # hours studied per day
    marks = Column(Float, nullable=False)

    # Link to user account
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="marks")
