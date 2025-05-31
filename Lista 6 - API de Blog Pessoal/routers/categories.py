from typing import List

from fastapi import Depends, APIRouter
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models import Category, post_categories
import schemas

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/with-post-count/", response_model=List[schemas.CategoryWithPostCount])
def read_categories_with_post_count(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    results = (
        db.query(
            Category,
            func.count(post_categories.c.post_id).label("post_count")
        )
        .outerjoin(post_categories, Category.id == post_categories.c.category_id)
        .group_by(Category.id)
        .order_by(func.count(post_categories.c.post_id).desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    response_data = []
    for category_orm, count in results:
        category_data = schemas.Category.from_orm(category_orm).dict()
        category_data['post_count'] = count
        response_data.append(schemas.CategoryWithPostCount(**category_data))

    return response_data

categories_crud_router = SQLAlchemyCRUDRouter(
    schema=schemas.Category,
    create_schema=schemas.CategoryCreate,
    db_model=Category,
    db=get_db
)

router.include_router(categories_crud_router)