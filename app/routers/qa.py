from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.models import Question, Profile, RoleEnum
from app.schemas.schemas import QuestionCreate, QuestionOut

router = APIRouter(prefix="/questions", tags=["Q&A"])


@router.post("/", response_model=QuestionOut, status_code=201)
def ask_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    """
    Any student can ask any alumni a question.
    student_id is stored in DB but never exposed to alumni in responses.
    """
    alumni = db.query(Profile).filter(Profile.id == payload.alumni_id, Profile.role == RoleEnum.alumni).first()
    if not alumni:
        raise HTTPException(status_code=404, detail="Alumni not found")

    question = Question(
        student_id=payload.student_id,
        alumni_id=payload.alumni_id,
        question=payload.question,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.get("/alumni/{alumni_id}", response_model=list[QuestionOut])
def public_qa_thread(alumni_id: UUID, db: Session = Depends(get_db)):
    """
    Public Q&A thread for an alumni — visible to everyone.
    student_id is not included in QuestionOut schema.
    """
    questions = (
        db.query(Question)
        .filter(Question.alumni_id == alumni_id)
        .order_by(Question.created_at.desc())
        .all()
    )
    return questions
