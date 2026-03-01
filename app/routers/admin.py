from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from uuid import UUID

from app.database import get_db
from app.models.models import (
    Profile, RoleEnum, AlumniProfileUpdate, AlumniPublicProfile,
    JobPosting, StatusEnum, Question
)
from app.schemas.schemas import (
    ProfileCreate, AdminProfileOut, StatusAction,
    AlumniProfileUpdateOut, JobPostingOut, QuestionAdminOut,
    TransitionToAlumni,
)

router = APIRouter(prefix="/admin", tags=["Admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# User Management
# ---------------------------------------------------------------------------

@router.get("/users", response_model=list[AdminProfileOut])
def list_users(role: str = None, db: Session = Depends(get_db)):
    query = db.query(Profile)
    if role:
        try:
            query = query.filter(Profile.role == RoleEnum(role))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    return query.order_by(Profile.created_at.desc()).all()


@router.post("/users", response_model=AdminProfileOut, status_code=201)
def create_user(payload: ProfileCreate, db: Session = Depends(get_db)):
    """Admin can create users of any role including other admins."""
    existing = db.query(Profile).filter(Profile.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = Profile(
        name=payload.name,
        email=payload.email,
        password_hash=pwd_context.hash(payload.password),
        role=payload.role,
        department=payload.department,
        batch_year=payload.batch_year,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    user = db.query(Profile).filter(Profile.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


# ---------------------------------------------------------------------------
# Student → Alumni Transition
# ---------------------------------------------------------------------------

@router.post("/transition-to-alumni", response_model=AdminProfileOut)
def transition_to_alumni(payload: TransitionToAlumni, db: Session = Depends(get_db)):
    student = db.query(Profile).filter(Profile.id == payload.student_id, Profile.role == RoleEnum.student).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.role = RoleEnum.alumni
    # Create empty public profile slot for the new alumni
    if not student.public_profile:
        db.add(AlumniPublicProfile(alumni_id=student.id))
    db.commit()
    db.refresh(student)
    return student


# ---------------------------------------------------------------------------
# Alumni Profile Update Approvals
# ---------------------------------------------------------------------------

@router.get("/profile-updates", response_model=list[AlumniProfileUpdateOut])
def list_profile_updates(status: str = None, db: Session = Depends(get_db)):
    query = db.query(AlumniProfileUpdate)
    if status:
        try:
            query = query.filter(AlumniProfileUpdate.status == StatusEnum(status))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    return query.order_by(AlumniProfileUpdate.created_at.desc()).all()


@router.post("/profile-updates/{update_id}/action", response_model=AlumniProfileUpdateOut)
def action_profile_update(update_id: UUID, payload: StatusAction, db: Session = Depends(get_db)):
    update = db.query(AlumniProfileUpdate).filter(AlumniProfileUpdate.id == update_id).first()
    if not update:
        raise HTTPException(status_code=404, detail="Update not found")

    update.status = payload.status

    # If approved, apply changes to the live public profile
    if payload.status == StatusEnum.approved:
        public = db.query(AlumniPublicProfile).filter(AlumniPublicProfile.alumni_id == update.alumni_id).first()
        if not public:
            public = AlumniPublicProfile(alumni_id=update.alumni_id)
            db.add(public)
        public.company = update.company
        public.job_title = update.job_title
        public.location = update.location

    db.commit()
    db.refresh(update)
    return update


# ---------------------------------------------------------------------------
# Job Posting Approvals
# ---------------------------------------------------------------------------

@router.get("/job-postings", response_model=list[JobPostingOut])
def list_job_postings(status: str = None, db: Session = Depends(get_db)):
    query = db.query(JobPosting)
    if status:
        try:
            query = query.filter(JobPosting.status == StatusEnum(status))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    return query.order_by(JobPosting.created_at.desc()).all()


@router.post("/job-postings/{job_id}/action", response_model=JobPostingOut)
def action_job_posting(job_id: UUID, payload: StatusAction, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    job.status = payload.status
    db.commit()
    db.refresh(job)
    return job


# ---------------------------------------------------------------------------
# Q&A with student identities visible
# ---------------------------------------------------------------------------

@router.get("/qa", response_model=list[QuestionAdminOut])
def list_all_qa(db: Session = Depends(get_db)):
    return db.query(Question).order_by(Question.created_at.desc()).all()


# ---------------------------------------------------------------------------
# Stats overview
# ---------------------------------------------------------------------------

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total_students = db.query(Profile).filter(Profile.role == RoleEnum.student).count()
    total_alumni = db.query(Profile).filter(Profile.role == RoleEnum.alumni).count()
    pending_profile_updates = db.query(AlumniProfileUpdate).filter(AlumniProfileUpdate.status == StatusEnum.pending).count()
    pending_jobs = db.query(JobPosting).filter(JobPosting.status == StatusEnum.pending).count()
    return {
        "total_students": total_students,
        "total_alumni": total_alumni,
        "pending_profile_updates": pending_profile_updates,
        "pending_job_postings": pending_jobs,
    }
