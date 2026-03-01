from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from passlib.context import CryptContext
from uuid import UUID

from app.database import get_db
from app.models.models import (
    Profile, RoleEnum, AlumniPublicProfile, AlumniProfileUpdate,
    JobPosting, JobSkill, StatusEnum, Question, Answer, StudentSkill
)
from app.schemas.schemas import (
    ProfileCreate, AlumniProfileUpdateCreate, AlumniProfileUpdateOut,
    JobPostingCreate, JobPostingOut, QuestionOut, AnswerCreate, AnswerOut,
    StatusAction,
)

router = APIRouter(prefix="/alumni", tags=["Alumni"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _load_alumni(alumni_id: UUID, db: Session) -> Profile:
    alumni = db.query(Profile).filter(Profile.id == alumni_id, Profile.role == RoleEnum.alumni).first()
    if not alumni:
        raise HTTPException(status_code=404, detail="Alumni not found")
    return alumni


# ---------------------------------------------------------------------------
# Get alumni profile (public — visible to all)
# ---------------------------------------------------------------------------

@router.get("/{alumni_id}", )
def get_alumni(alumni_id: UUID, db: Session = Depends(get_db)):
    alumni = _load_alumni(alumni_id, db)
    return {
        "id": alumni.id,
        "name": alumni.name,
        "department": alumni.department,
        "batch_year": alumni.batch_year,
        "linkedin_url": alumni.linkedin_url,
        "github_url": alumni.github_url,
        "public_profile": alumni.public_profile,
    }


@router.get("/", response_model=list)
def list_all_alumni(db: Session = Depends(get_db)):
    alumni_list = db.query(Profile).filter(Profile.role == RoleEnum.alumni).all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "department": a.department,
            "batch_year": a.batch_year,
            "linkedin_url": a.linkedin_url,
            "public_profile": a.public_profile,
        }
        for a in alumni_list
    ]


# ---------------------------------------------------------------------------
# Profile update request (goes to admin for approval)
# ---------------------------------------------------------------------------

@router.post("/{alumni_id}/profile-updates", response_model=AlumniProfileUpdateOut, status_code=201)
def submit_profile_update(alumni_id: UUID, payload: AlumniProfileUpdateCreate, db: Session = Depends(get_db)):
    _load_alumni(alumni_id, db)
    update = AlumniProfileUpdate(
        alumni_id=alumni_id,
        company=payload.company,
        job_title=payload.job_title,
        location=payload.location,
        status=StatusEnum.pending,
    )
    db.add(update)
    db.commit()
    db.refresh(update)
    return update


@router.get("/{alumni_id}/profile-updates", response_model=list[AlumniProfileUpdateOut])
def get_my_profile_updates(alumni_id: UUID, db: Session = Depends(get_db)):
    _load_alumni(alumni_id, db)
    updates = (
        db.query(AlumniProfileUpdate)
        .filter(AlumniProfileUpdate.alumni_id == alumni_id)
        .order_by(AlumniProfileUpdate.created_at.desc())
        .all()
    )
    return updates


# ---------------------------------------------------------------------------
# Job Postings
# ---------------------------------------------------------------------------

@router.post("/{alumni_id}/jobs", response_model=JobPostingOut, status_code=201)
def create_job(alumni_id: UUID, payload: JobPostingCreate, db: Session = Depends(get_db)):
    _load_alumni(alumni_id, db)
    job = JobPosting(
        alumni_id=alumni_id,
        title=payload.title,
        company=payload.company,
        salary=payload.salary,
        location_type=payload.location_type,
        location_city=payload.location_city,
        description=payload.description,
        min_readiness_pct=payload.min_readiness_pct,
        status=StatusEnum.pending,
    )
    db.add(job)
    db.flush()
    for skill_id in payload.skill_ids:
        db.add(JobSkill(job_id=job.id, skill_id=skill_id))
    db.commit()
    db.refresh(job)
    return job


@router.get("/{alumni_id}/jobs", response_model=list[JobPostingOut])
def list_my_jobs(alumni_id: UUID, db: Session = Depends(get_db)):
    _load_alumni(alumni_id, db)
    jobs = db.query(JobPosting).filter(JobPosting.alumni_id == alumni_id).all()
    return jobs


@router.delete("/{alumni_id}/jobs/{job_id}", status_code=204)
def delete_job(alumni_id: UUID, job_id: UUID, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id, JobPosting.alumni_id == alumni_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    db.delete(job)
    db.commit()


# ---------------------------------------------------------------------------
# Q&A — Alumni inbox (questions are anonymous)
# ---------------------------------------------------------------------------

@router.get("/{alumni_id}/questions", response_model=list[QuestionOut])
def get_questions(alumni_id: UUID, db: Session = Depends(get_db)):
    """
    Returns questions received by this alumni.
    student_id is NOT included in the response (anonymous).
    """
    _load_alumni(alumni_id, db)
    questions = (
        db.query(Question)
        .filter(Question.alumni_id == alumni_id)
        .order_by(Question.created_at.desc())
        .all()
    )
    return questions


@router.post("/{alumni_id}/questions/{question_id}/answer", response_model=AnswerOut, status_code=201)
def answer_question(alumni_id: UUID, question_id: UUID, payload: AnswerCreate, db: Session = Depends(get_db)):
    _load_alumni(alumni_id, db)
    question = db.query(Question).filter(Question.id == question_id, Question.alumni_id == alumni_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    if question.answer:
        raise HTTPException(status_code=400, detail="Question already answered")
    answer = Answer(question_id=question_id, answer=payload.answer)
    db.add(answer)
    db.commit()
    db.refresh(answer)
    return answer


@router.patch("/{alumni_id}/questions/{question_id}/answer", response_model=AnswerOut)
def update_answer(alumni_id: UUID, question_id: UUID, payload: AnswerCreate, db: Session = Depends(get_db)):
    _load_alumni(alumni_id, db)
    question = db.query(Question).filter(Question.id == question_id, Question.alumni_id == alumni_id).first()
    if not question or not question.answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    question.answer.answer = payload.answer
    db.commit()
    db.refresh(question.answer)
    return question.answer
