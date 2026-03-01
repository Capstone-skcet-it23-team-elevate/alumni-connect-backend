from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.routers import auth, student, alumni, admin, qa, jobs, reference

# Import all models so Base.metadata knows about them
import app.models.models  # noqa

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AlumniConnect API",
    description="Backend for the AlumniConnect platform",
    version="1.0.0",
)

# Allow all origins — no auth, demo app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(student.router)
app.include_router(alumni.router)
app.include_router(admin.router)
app.include_router(qa.router)
app.include_router(jobs.router)
app.include_router(reference.router)


@app.get("/")
def root():
    return {"message": "AlumniConnect API is running"}
