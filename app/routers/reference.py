from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models.models import RoleCategory, TargetRole, Skill, TodoItem, LevelEnum
from app.schemas.schemas import RoleCategoryOut, TargetRoleListOut, SkillListOut, TodoItemOut

router = APIRouter(prefix="/reference", tags=["Reference Data"])


@router.get("/categories", response_model=list[RoleCategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(RoleCategory).all()


@router.get("/target-roles", response_model=list[TargetRoleListOut])
def list_target_roles(category_id: UUID = None, db: Session = Depends(get_db)):
    query = db.query(TargetRole)
    if category_id:
        query = query.filter(TargetRole.category_id == category_id)
    return query.all()


@router.get("/skills", response_model=list[SkillListOut])
def list_skills(category_id: UUID = None, db: Session = Depends(get_db)):
    query = db.query(Skill)
    if category_id:
        query = query.filter(Skill.category_id == category_id)
    return query.all()


@router.get("/todos", response_model=list[TodoItemOut])
def list_todos(category_id: UUID = None, level: str = None, db: Session = Depends(get_db)):
    query = db.query(TodoItem)
    if category_id:
        query = query.filter(TodoItem.category_id == category_id)
    if level:
        try:
            query = query.filter(TodoItem.level == LevelEnum(level))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid level: {level}")
    return query.all()


# Admin-only CRUD for reference data

@router.post("/categories", response_model=RoleCategoryOut, status_code=201)
def create_category(name: str, db: Session = Depends(get_db)):
    cat = RoleCategory(name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.post("/target-roles", response_model=TargetRoleListOut, status_code=201)
def create_target_role(name: str, category_id: UUID, keywords: list[str] = [], db: Session = Depends(get_db)):
    role = TargetRole(name=name, category_id=category_id, keywords=keywords)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.post("/skills", response_model=SkillListOut, status_code=201)
def create_skill(name: str, category_id: UUID = None, db: Session = Depends(get_db)):
    skill = Skill(name=name, category_id=category_id)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill


@router.post("/todos", response_model=TodoItemOut, status_code=201)
def create_todo(
    category_id: UUID,
    level: str,
    title: str,
    description: str = None,
    resource_url: str = None,
    db: Session = Depends(get_db)
):
    try:
        level_enum = LevelEnum(level)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid level: {level}")
    item = TodoItem(
        category_id=category_id,
        level=level_enum,
        title=title,
        description=description,
        resource_url=resource_url,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
