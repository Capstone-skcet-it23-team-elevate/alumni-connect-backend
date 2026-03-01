"""
Mentor Matching Engine
-----------------------
Finds alumni whose job titles match a student's target role keywords.
Secondary sort: skill overlap between student and alumni.
Returns top 5.
"""

from sqlalchemy.orm import Session
from app.models.models import Profile, RoleEnum, AlumniPublicProfile


def get_mentor_suggestions(db: Session, student: Profile, limit: int = 5):
    """
    Returns a list of (alumni_profile, skill_overlap_count) tuples.
    """
    if not student.target_role or not student.target_role.keywords:
        return []

    keywords = [k.lower() for k in student.target_role.keywords]

    # Fetch all alumni who have a public profile with a job title
    alumni_list = (
        db.query(Profile)
        .join(AlumniPublicProfile, AlumniPublicProfile.alumni_id == Profile.id)
        .filter(Profile.role == RoleEnum.alumni)
        .filter(AlumniPublicProfile.job_title.isnot(None))
        .all()
    )

    # Filter by keyword match in job title
    matched = []
    for alumni in alumni_list:
        job_title = alumni.public_profile.job_title.lower()
        if any(kw in job_title for kw in keywords):
            # Count skill overlap
            alumni_skill_names = {ss.skill.name.lower() for ss in alumni.student_skills if ss.skill}
            student_skill_names = {ss.skill.name.lower() for ss in student.student_skills if ss.skill}
            overlap = len(alumni_skill_names & student_skill_names)
            matched.append((alumni, overlap))

    # Sort by skill overlap descending
    matched.sort(key=lambda x: x[1], reverse=True)

    return matched[:limit]
