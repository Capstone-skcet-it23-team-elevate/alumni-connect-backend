"""
Career Readiness Scoring Engine
--------------------------------
Disguised as an AI system but is fully rule-based.

Scale: 0 - 100 points
Levels:
  0  - 24  → Foundation
  25 - 49  → Skill Building
  50 - 74  → Internship Ready
  75 - 100 → Interview Ready
"""

from app.models.models import Profile, LevelEnum


def compute_readiness(profile: Profile) -> int:
    """
    Compute readiness score for a student profile.
    Returns integer score 0-100.
    """
    score = 0

    # ------------------------------------------------------------------
    # 1. Profile Completeness — max 10 pts
    # ------------------------------------------------------------------
    if profile.linkedin_url:
        score += 3
    if profile.github_url:
        score += 3
    if profile.target_role_id:
        score += 4

    # ------------------------------------------------------------------
    # 2. Skills — max 30 pts
    #    +2 per skill (cap 10 skills = 20 pts)
    #    +1 bonus per skill matching target role keywords (cap 10 pts)
    # ------------------------------------------------------------------
    student_skills = profile.student_skills or []
    skill_count = min(len(student_skills), 10)
    score += skill_count * 2

    # keyword bonus — compare skill names to target role's keywords
    if profile.target_role and profile.target_role.keywords:
        keywords = [k.lower() for k in profile.target_role.keywords]
        matching = 0
        for ss in student_skills:
            if ss.skill and ss.skill.name.lower() in keywords:
                matching += 1
        score += min(matching, 10)

    # ------------------------------------------------------------------
    # 3. Projects — max 30 pts
    #    +5 per project (cap 4 = 20 pts)
    #    +1 per project with description (cap 4 = 4 pts)
    #    +1 per project with github_url (cap 4 = 4 pts)
    #    +0.5 per project with tech stack tagged (cap 4 = 2 pts)
    # ------------------------------------------------------------------
    projects = profile.projects or []
    project_count = min(len(projects), 4)
    score += project_count * 5

    desc_count = sum(1 for p in projects[:4] if p.description)
    score += min(desc_count, 4)

    github_count = sum(1 for p in projects[:4] if p.github_url)
    score += min(github_count, 4)

    tech_count = sum(1 for p in projects[:4] if p.project_skills)
    score += min(tech_count, 4) * 0.5

    # ------------------------------------------------------------------
    # 4. Certifications — max 15 pts
    #    +7.5 per cert (cap 2 = 15 pts)
    # ------------------------------------------------------------------
    certs = profile.certifications or []
    cert_count = min(len(certs), 2)
    score += cert_count * 7.5

    # ------------------------------------------------------------------
    # 5. Experience — max 15 pts
    #    Internship → +15
    #    Freelance or Part-time → +8
    #    Takes the higher value (doesn't stack)
    # ------------------------------------------------------------------
    experiences = profile.experiences or []
    exp_types = {e.type.value for e in experiences}

    if "internship" in exp_types:
        score += 15
    elif "freelance" in exp_types or "part_time" in exp_types:
        score += 8

    return min(int(score), 100)


def score_to_level(score: int) -> LevelEnum:
    if score >= 75:
        return LevelEnum.interview_ready
    elif score >= 50:
        return LevelEnum.internship_ready
    elif score >= 25:
        return LevelEnum.skill_building
    else:
        return LevelEnum.foundation
