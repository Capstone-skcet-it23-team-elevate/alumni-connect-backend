"""
Roadmap Service
---------------
Fetches todo items for a student based on:
  - Their target role's category
  - Their current readiness level
  
Items for levels above the student's current level are also returned
but marked accordingly so the frontend can grey them out.
"""

from sqlalchemy.orm import Session
from app.models.models import TodoItem, TargetRole, LevelEnum
from uuid import UUID


LEVEL_ORDER = [
    LevelEnum.foundation,
    LevelEnum.skill_building,
    LevelEnum.internship_ready,
    LevelEnum.interview_ready,
]


def get_roadmap(db: Session, target_role_id: UUID, current_level: LevelEnum):
    """
    Returns all todo items for the role category, grouped/ordered by level.
    The current level and all levels below are "unlocked".
    Levels above are "locked" (frontend handles the greying).
    """
    # Get the category from the target role
    target_role = db.query(TargetRole).filter(TargetRole.id == target_role_id).first()
    if not target_role:
        return []

    items = (
        db.query(TodoItem)
        .filter(TodoItem.category_id == target_role.category_id)
        .order_by(TodoItem.level)
        .all()
    )

    current_index = LEVEL_ORDER.index(current_level)

    result = []
    for item in items:
        item_index = LEVEL_ORDER.index(item.level)
        result.append({
            "id": item.id,
            "level": item.level,
            "title": item.title,
            "description": item.description,
            "resource_url": item.resource_url,
            "locked": item_index > current_index,
        })

    return result
