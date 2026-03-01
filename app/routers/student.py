from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from passlib.context import CryptContext
from uuid import UUID

from app.database import get_db
from app.models.models import (
    Profile, RoleEnum, StudentSkill, Skill, Project, ProjectSkill,
    Certification, Experience, JobPosting, StatusEnum
)
from app.schemas.schemas import (
    ProfileCreate, ProfileUpdate, ProfileOut, StudentSkillSet,
    ProjectCreate, ProjectUpdate, ProjectOut,
    CertCreate, CertUpdate, CertOut,
    ExperienceCreate, ExperienceUpdate, ExperienceOut,
    ReadinessOut, MentorOut,
)
from app.services.scoring import compute_readiness, score_to_level
from app.services.matching import get_mentor_suggestions
from app.services.roadmap import get_roadmap

router = APIRouter(prefix="/students", tags=["Students"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _load_profile(student_id: UUID, db: Session) -> Profile:
    profile = (
        db.query(Profile)
        .options(
            joinedload(Profile.student_skills).joinedload(StudentSkill.skill),
            joinedload(Profile.projects).joinedload(Project.project_skills).joinedload(ProjectSkill.skill),
            joinedload(Profile.certifications),
            joinedload(Profile.experiences),
            joinedload(Profile.target_role),
        )
        .filter(Profile.id == student_id, Profile.role == RoleEnum.student)
        .first()
    )
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found")
    return profile


def _recompute_and_save(profile: Profile, db: Session):
    score = compute_readiness(profile)
    profile.readiness_score = score
    db.commit()
    db.refresh(profile)
    return score


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@router.post("/register", response_model=ProfileOut, status_code=201)
def register_student(payload: ProfileCreate, db: Session = Depends(get_db)):
    existing = db.query(Profile).filter(Profile.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    profile = Profile(
        name=payload.name,
        email=payload.email,
        password_hash=pwd_context.hash(payload.password),
        role=RoleEnum.student,
        department=payload.department,
        batch_year=payload.batch_year,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

@router.get("/{student_id}", response_model=ProfileOut)
def get_student(student_id: UUID, db: Session = Depends(get_db)):
    return _load_profile(student_id, db)


@router.patch("/{student_id}", response_model=ProfileOut)
def update_student(student_id: UUID, payload: ProfileUpdate, db: Session = Depends(get_db)):
    profile = _load_profile(student_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    _recompute_and_save(profile, db)
    return _load_profile(student_id, db)


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

@router.put("/{student_id}/skills", response_model=ProfileOut)
def set_skills(student_id: UUID, payload: StudentSkillSet, db: Session = Depends(get_db)):
    profile = _load_profile(student_id, db)

    # Validate all skill IDs exist
    for skill_id in payload.skill_ids:
        if not db.query(Skill).filter(Skill.id == skill_id).first():
            raise HTTPException(status_code=404, detail=f"Skill {skill_id} not found")

    # Replace all skills
    db.query(StudentSkill).filter(StudentSkill.student_id == student_id).delete()
    for skill_id in payload.skill_ids:
        db.add(StudentSkill(student_id=student_id, skill_id=skill_id))
    db.commit()

    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)
    return _load_profile(student_id, db)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

@router.get("/{student_id}/projects", response_model=list[ProjectOut])
def list_projects(student_id: UUID, db: Session = Depends(get_db)):
    profile = _load_profile(student_id, db)
    return profile.projects


@router.post("/{student_id}/projects", response_model=ProjectOut, status_code=201)
def add_project(student_id: UUID, payload: ProjectCreate, db: Session = Depends(get_db)):
    _load_profile(student_id, db)
    project = Project(
        student_id=student_id,
        title=payload.title,
        description=payload.description,
        github_url=payload.github_url,
    )
    db.add(project)
    db.flush()
    for skill_id in payload.skill_ids:
        db.add(ProjectSkill(project_id=project.id, skill_id=skill_id))
    db.commit()
    db.refresh(project)

    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)
    return project


@router.patch("/{student_id}/projects/{project_id}", response_model=ProjectOut)
def update_project(student_id: UUID, project_id: UUID, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.student_id == student_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in payload.model_dump(exclude_unset=True, exclude={"skill_ids"}).items():
        setattr(project, field, value)

    if payload.skill_ids is not None:
        db.query(ProjectSkill).filter(ProjectSkill.project_id == project_id).delete()
        for skill_id in payload.skill_ids:
            db.add(ProjectSkill(project_id=project_id, skill_id=skill_id))

    db.commit()
    db.refresh(project)
    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)
    return project


@router.delete("/{student_id}/projects/{project_id}", status_code=204)
def delete_project(student_id: UUID, project_id: UUID, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id, Project.student_id == student_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)


# ---------------------------------------------------------------------------
# Certifications
# ---------------------------------------------------------------------------

@router.post("/{student_id}/certifications", response_model=CertOut, status_code=201)
def add_cert(student_id: UUID, payload: CertCreate, db: Session = Depends(get_db)):
    _load_profile(student_id, db)
    cert = Certification(student_id=student_id, **payload.model_dump())
    db.add(cert)
    db.commit()
    db.refresh(cert)
    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)
    return cert


@router.patch("/{student_id}/certifications/{cert_id}", response_model=CertOut)
def update_cert(student_id: UUID, cert_id: UUID, payload: CertUpdate, db: Session = Depends(get_db)):
    cert = db.query(Certification).filter(Certification.id == cert_id, Certification.student_id == student_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(cert, field, value)
    db.commit()
    db.refresh(cert)
    return cert


@router.delete("/{student_id}/certifications/{cert_id}", status_code=204)
def delete_cert(student_id: UUID, cert_id: UUID, db: Session = Depends(get_db)):
    cert = db.query(Certification).filter(Certification.id == cert_id, Certification.student_id == student_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")
    db.delete(cert)
    db.commit()
    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

@router.post("/{student_id}/experiences", response_model=ExperienceOut, status_code=201)
def add_experience(student_id: UUID, payload: ExperienceCreate, db: Session = Depends(get_db)):
    _load_profile(student_id, db)
    exp = Experience(student_id=student_id, **payload.model_dump())
    db.add(exp)
    db.commit()
    db.refresh(exp)
    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)
    return exp


@router.patch("/{student_id}/experiences/{exp_id}", response_model=ExperienceOut)
def update_experience(student_id: UUID, exp_id: UUID, payload: ExperienceUpdate, db: Session = Depends(get_db)):
    exp = db.query(Experience).filter(Experience.id == exp_id, Experience.student_id == student_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(exp, field, value)
    db.commit()
    db.refresh(exp)
    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)
    return exp


@router.delete("/{student_id}/experiences/{exp_id}", status_code=204)
def delete_experience(student_id: UUID, exp_id: UUID, db: Session = Depends(get_db)):
    exp = db.query(Experience).filter(Experience.id == exp_id, Experience.student_id == student_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Experience not found")
    db.delete(exp)
    db.commit()
    profile = _load_profile(student_id, db)
    _recompute_and_save(profile, db)


# ---------------------------------------------------------------------------
# Readiness Score
# ---------------------------------------------------------------------------

@router.get("/{student_id}/readiness", response_model=ReadinessOut)
def get_readiness(student_id: UUID, db: Session = Depends(get_db)):
    profile = _load_profile(student_id, db)
    score = compute_readiness(profile)
    profile.readiness_score = score
    db.commit()
    level = score_to_level(score)
    return ReadinessOut(score=score, level=level, percentage=float(score))


# ---------------------------------------------------------------------------
# Roadmap
# ---------------------------------------------------------------------------

@router.get("/{student_id}/roadmap")
def get_student_roadmap(student_id: UUID, db: Session = Depends(get_db)):
    profile = _load_profile(student_id, db)
    if not profile.target_role_id:
        raise HTTPException(status_code=400, detail="Student has no target role set")
    level = score_to_level(profile.readiness_score)
    return get_roadmap(db, profile.target_role_id, level)


# ---------------------------------------------------------------------------
# Mentor Suggestions
# ---------------------------------------------------------------------------

@router.get("/{student_id}/mentors", response_model=list[MentorOut])
def get_mentors(student_id: UUID, db: Session = Depends(get_db)):
    profile = _load_profile(student_id, db)
    matches = get_mentor_suggestions(db, profile)
    result = []
    for alumni, overlap in matches:
        result.append(MentorOut(
            id=alumni.id,
            name=alumni.name,
            department=alumni.department,
            linkedin_url=alumni.linkedin_url,
            public_profile=alumni.public_profile,
            skill_overlap=overlap,
        ))
    return result


# ---------------------------------------------------------------------------
# Browse Jobs (approved only, filtered by readiness)
# ---------------------------------------------------------------------------

@router.get("/{student_id}/jobs")
def browse_jobs(student_id: UUID, db: Session = Depends(get_db)):
    profile = _load_profile(student_id, db)
    jobs = (
        db.query(JobPosting)
        .filter(
            JobPosting.status == StatusEnum.approved,
            JobPosting.min_readiness_pct <= profile.readiness_score
        )
        .all()
    )
    return jobs


# ---------------------------------------------------------------------------
# Questions (student view — questions they asked)
# ---------------------------------------------------------------------------

@router.get("/{student_id}/questions")
def my_questions(student_id: UUID, db: Session = Depends(get_db)):
    profile = _load_profile(student_id, db)
    return profile.questions_asked
