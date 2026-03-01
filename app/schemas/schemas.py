from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


# ---------------------------------------------------------------------------
# Enums (mirroring model enums for Pydantic)
# ---------------------------------------------------------------------------

class RoleEnum(str, Enum):
    student = "student"
    alumni = "alumni"
    admin = "admin"

class LocationTypeEnum(str, Enum):
    remote = "remote"
    onsite = "onsite"

class StatusEnum(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ExperienceTypeEnum(str, Enum):
    internship = "internship"
    freelance = "freelance"
    part_time = "part_time"

class LevelEnum(str, Enum):
    foundation = "foundation"
    skill_building = "skill_building"
    internship_ready = "internship_ready"
    interview_ready = "interview_ready"


# ---------------------------------------------------------------------------
# Auth / Login
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: RoleEnum
    department: Optional[str]
    batch_year: Optional[int]
    readiness_score: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class ProfileCreate(BaseModel):
    name: str
    email: str
    password: str
    role: RoleEnum = RoleEnum.student
    department: Optional[str] = None
    batch_year: Optional[int] = None

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    batch_year: Optional[int] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    target_role_id: Optional[UUID] = None

class SkillOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class ProjectOut(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    github_url: Optional[str]
    project_skills: List[SkillOut] = []

    class Config:
        from_attributes = True

class CertOut(BaseModel):
    id: UUID
    name: str
    issuer: Optional[str]
    url: Optional[str]

    class Config:
        from_attributes = True

class ExperienceOut(BaseModel):
    id: UUID
    type: ExperienceTypeEnum
    company: str
    role: str
    duration: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True

class TargetRoleOut(BaseModel):
    id: UUID
    name: str
    keywords: List[str]

    class Config:
        from_attributes = True

class ProfileOut(BaseModel):
    id: UUID
    name: str
    email: str
    role: RoleEnum
    department: Optional[str]
    batch_year: Optional[int]
    linkedin_url: Optional[str]
    github_url: Optional[str]
    target_role: Optional[TargetRoleOut]
    readiness_score: int
    created_at: datetime
    student_skills: List[SkillOut] = []
    projects: List[ProjectOut] = []
    certifications: List[CertOut] = []
    experiences: List[ExperienceOut] = []

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Skills
# ---------------------------------------------------------------------------

class StudentSkillSet(BaseModel):
    skill_ids: List[UUID]  # replaces all existing skills


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    github_url: Optional[str] = None
    skill_ids: List[UUID] = []

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    github_url: Optional[str] = None
    skill_ids: Optional[List[UUID]] = None


# ---------------------------------------------------------------------------
# Certifications
# ---------------------------------------------------------------------------

class CertCreate(BaseModel):
    name: str
    issuer: Optional[str] = None
    url: Optional[str] = None

class CertUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    url: Optional[str] = None


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

class ExperienceCreate(BaseModel):
    type: ExperienceTypeEnum
    company: str
    role: str
    duration: Optional[str] = None
    description: Optional[str] = None

class ExperienceUpdate(BaseModel):
    type: Optional[ExperienceTypeEnum] = None
    company: Optional[str] = None
    role: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


# ---------------------------------------------------------------------------
# Readiness / Roadmap
# ---------------------------------------------------------------------------

class ReadinessOut(BaseModel):
    score: int
    level: LevelEnum
    percentage: float  # 0.0 - 100.0, represents position within the 100-point scale

class TodoItemOut(BaseModel):
    id: UUID
    level: LevelEnum
    title: str
    description: Optional[str]
    resource_url: Optional[str]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Mentor Matching
# ---------------------------------------------------------------------------

class AlumniPublicProfileOut(BaseModel):
    company: Optional[str]
    job_title: Optional[str]
    location: Optional[str]

    class Config:
        from_attributes = True

class MentorOut(BaseModel):
    id: UUID
    name: str
    department: Optional[str]
    linkedin_url: Optional[str]
    public_profile: Optional[AlumniPublicProfileOut]
    skill_overlap: int  # how many skills match with the student

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Alumni Profile Updates
# ---------------------------------------------------------------------------

class AlumniProfileUpdateCreate(BaseModel):
    company: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None

class AlumniProfileUpdateOut(BaseModel):
    id: UUID
    alumni_id: UUID
    company: Optional[str]
    job_title: Optional[str]
    location: Optional[str]
    status: StatusEnum
    created_at: datetime

    class Config:
        from_attributes = True

class StatusAction(BaseModel):
    status: StatusEnum  # approved or rejected


# ---------------------------------------------------------------------------
# Job Postings
# ---------------------------------------------------------------------------

class JobPostingCreate(BaseModel):
    title: str
    company: str
    salary: Optional[str] = None
    location_type: LocationTypeEnum
    location_city: Optional[str] = None
    description: str
    min_readiness_pct: int = 0
    skill_ids: List[UUID] = []

class JobPostingOut(BaseModel):
    id: UUID
    alumni_id: UUID
    title: str
    company: str
    salary: Optional[str]
    location_type: LocationTypeEnum
    location_city: Optional[str]
    description: str
    min_readiness_pct: int
    status: StatusEnum
    created_at: datetime
    required_skills: List[SkillOut] = []

    class Config:
        from_attributes = True

class JobApplicationOut(BaseModel):
    id: UUID
    job_id: UUID
    student_id: UUID
    applied_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Q&A
# ---------------------------------------------------------------------------

class QuestionCreate(BaseModel):
    student_id: UUID
    alumni_id: UUID
    question: str

class AnswerCreate(BaseModel):
    answer: str

class AnswerOut(BaseModel):
    id: UUID
    answer: str
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionOut(BaseModel):
    id: UUID
    alumni_id: UUID
    question: str
    created_at: datetime
    answer: Optional[AnswerOut]
    # student_id intentionally excluded — alumni sees anonymous questions
    # admin endpoint will use QuestionAdminOut

    class Config:
        from_attributes = True

class QuestionAdminOut(BaseModel):
    id: UUID
    student_id: UUID          # visible to admin only
    alumni_id: UUID
    question: str
    created_at: datetime
    answer: Optional[AnswerOut]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Taxonomy (read-only reference data)
# ---------------------------------------------------------------------------

class RoleCategoryOut(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class TargetRoleListOut(BaseModel):
    id: UUID
    name: str
    category_id: UUID
    keywords: List[str]

    class Config:
        from_attributes = True

class SkillListOut(BaseModel):
    id: UUID
    name: str
    category_id: Optional[UUID]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

class AdminProfileOut(BaseModel):
    id: UUID
    name: str
    email: str
    role: RoleEnum
    department: Optional[str]
    batch_year: Optional[int]
    readiness_score: int
    created_at: datetime

    class Config:
        from_attributes = True

class TransitionToAlumni(BaseModel):
    student_id: UUID
