from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.models import JobPosting, JobApplication, Profile, RoleEnum, StatusEnum
from app.schemas.schemas import JobApplicationOut

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/", )
def list_approved_jobs(db: Session = Depends(get_db)):
    """List all approved job postings — no readiness filter here, that's per-student."""
    return db.query(JobPosting).filter(JobPosting.status == StatusEnum.approved).all()


@router.get("/{job_id}")
def get_job(job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/{job_id}/apply", response_model=JobApplicationOut, status_code=201)
def apply_to_job(job_id: UUID, student_id: UUID, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id, JobPosting.status == StatusEnum.approved).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not approved")

    student = db.query(Profile).filter(Profile.id == student_id, Profile.role == RoleEnum.student).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.readiness_score < job.min_readiness_pct:
        raise HTTPException(
            status_code=403,
            detail=f"Readiness score {student.readiness_score} is below the required {job.min_readiness_pct}"
        )

    existing = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.student_id == student_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already applied")

    application = JobApplication(job_id=job_id, student_id=student_id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/{job_id}/applications", response_model=list[JobApplicationOut])
def get_applications(job_id: UUID, db: Session = Depends(get_db)):
    """Get all applications for a job — admin or alumni use."""
    return db.query(JobApplication).filter(JobApplication.job_id == job_id).all()
