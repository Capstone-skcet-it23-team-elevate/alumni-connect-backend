import uuid
from sqlalchemy import (
    Column, String, Integer, Text, Enum, ForeignKey,
    DateTime, Boolean, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class RoleEnum(str, enum.Enum):
    student = "student"
    alumni = "alumni"
    admin = "admin"

class LocationTypeEnum(str, enum.Enum):
    remote = "remote"
    onsite = "onsite"

class StatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ExperienceTypeEnum(str, enum.Enum):
    internship = "internship"
    freelance = "freelance"
    part_time = "part_time"

class LevelEnum(str, enum.Enum):
    foundation = "foundation"
    skill_building = "skill_building"
    internship_ready = "internship_ready"
    interview_ready = "interview_ready"


# ---------------------------------------------------------------------------
# Taxonomy
# ---------------------------------------------------------------------------

class RoleCategory(Base):
    __tablename__ = "role_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)  # e.g. "Cloud & DevOps"

    target_roles = relationship("TargetRole", back_populates="category")
    skills = relationship("Skill", back_populates="category")
    todo_items = relationship("TodoItem", back_populates="category")


class TargetRole(Base):
    __tablename__ = "target_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)              # e.g. "Cloud Security Engineer"
    category_id = Column(UUID(as_uuid=True), ForeignKey("role_categories.id"), nullable=False)
    keywords = Column(ARRAY(String), default=[])       # used for mentor matching

    category = relationship("RoleCategory", back_populates="target_roles")
    profiles = relationship("Profile", back_populates="target_role")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("role_categories.id"), nullable=True)

    category = relationship("RoleCategory", back_populates="skills")


# ---------------------------------------------------------------------------
# Users / Profiles
# ---------------------------------------------------------------------------

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.student)
    department = Column(String, nullable=True)
    batch_year = Column(Integer, nullable=True)
    linkedin_url = Column(String, nullable=True)
    github_url = Column(String, nullable=True)
    target_role_id = Column(UUID(as_uuid=True), ForeignKey("target_roles.id"), nullable=True)
    readiness_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    target_role = relationship("TargetRole", back_populates="profiles")
    student_skills = relationship("StudentSkill", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="profile", cascade="all, delete-orphan")
    experiences = relationship("Experience", back_populates="profile", cascade="all, delete-orphan")

    # alumni side
    public_profile = relationship("AlumniPublicProfile", back_populates="alumni", uselist=False, cascade="all, delete-orphan")
    profile_updates = relationship("AlumniProfileUpdate", back_populates="alumni", cascade="all, delete-orphan")
    job_postings = relationship("JobPosting", back_populates="alumni", cascade="all, delete-orphan")

    # Q&A
    questions_asked = relationship("Question", foreign_keys="Question.student_id", back_populates="student", cascade="all, delete-orphan")
    questions_received = relationship("Question", foreign_keys="Question.alumni_id", back_populates="alumni")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)

    profile = relationship("Profile", back_populates="student_skills")
    skill = relationship("Skill")


# ---------------------------------------------------------------------------
# Student Portfolio
# ---------------------------------------------------------------------------

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    github_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="projects")
    project_skills = relationship("ProjectSkill", back_populates="project", cascade="all, delete-orphan")


class ProjectSkill(Base):
    __tablename__ = "project_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)

    project = relationship("Project", back_populates="project_skills")
    skill = relationship("Skill")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    issuer = Column(String, nullable=True)
    url = Column(String, nullable=True)

    profile = relationship("Profile", back_populates="certifications")


class Experience(Base):
    __tablename__ = "experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(ExperienceTypeEnum), nullable=False)
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    duration = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    profile = relationship("Profile", back_populates="experiences")


# ---------------------------------------------------------------------------
# Roadmap Todos
# ---------------------------------------------------------------------------

class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("role_categories.id"), nullable=False)
    level = Column(Enum(LevelEnum), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    resource_url = Column(String, nullable=True)

    category = relationship("RoleCategory", back_populates="todo_items")


# ---------------------------------------------------------------------------
# Alumni Profile
# ---------------------------------------------------------------------------

class AlumniPublicProfile(Base):
    __tablename__ = "alumni_public_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alumni_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, unique=True)
    company = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    location = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    alumni = relationship("Profile", back_populates="public_profile")


class AlumniProfileUpdate(Base):
    __tablename__ = "alumni_profile_updates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alumni_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    company = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    location = Column(String, nullable=True)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alumni = relationship("Profile", back_populates="profile_updates")


# ---------------------------------------------------------------------------
# Job Postings
# ---------------------------------------------------------------------------

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alumni_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    salary = Column(String, nullable=True)
    location_type = Column(Enum(LocationTypeEnum), nullable=False)
    location_city = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    min_readiness_pct = Column(Integer, default=0)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    alumni = relationship("Profile", back_populates="job_postings")
    required_skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="job", cascade="all, delete-orphan")


class JobSkill(Base):
    __tablename__ = "job_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False)
    skill_id = Column(UUID(as_uuid=True), ForeignKey("skills.id"), nullable=False)

    job = relationship("JobPosting", back_populates="required_skills")
    skill = relationship("Skill")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())

    job = relationship("JobPosting", back_populates="applications")
    student = relationship("Profile")


# ---------------------------------------------------------------------------
# Q&A
# ---------------------------------------------------------------------------

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    alumni_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=False)
    question = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Profile", foreign_keys=[student_id], back_populates="questions_asked")
    alumni = relationship("Profile", foreign_keys=[alumni_id], back_populates="questions_received")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, unique=True)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("Question", back_populates="answer")
