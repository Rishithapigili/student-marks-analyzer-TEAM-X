from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import auth_router, marks_router

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Marks Analyzer API",
    description="A FastAPI backend for analyzing student marks with JWT authentication and role-based access.",
    version="2.0.0",
)

# Include routers
app.include_router(auth_router.router)
app.include_router(marks_router.router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the Student Marks Analyzer API",
        "docs": "/docs",
        "workflow": [
            "1. Admin registers at /auth/register",
            "2. Admin logs in at /auth/login",
            "3. Admin uploads CSV at /marks/upload or loads default at /marks/load-csv",
            "4. Student accounts are auto-created (username=Name_RollNo e.g. Ishaan Rao_2210A31, password=Roll Number)",
            "5. Students login and access /auth/me to see their marks",
        ],
        "endpoints": {
            "auth": ["/auth/register (admin)", "/auth/login", "/auth/me (student)"],
            "marks_admin": ["/marks/upload", "/marks/load-csv", "/marks/"],
            "marks_all": ["/marks/average", "/marks/highest", "/marks/lowest", "/marks/bar-chart", "/marks/histogram"],
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
