from typing import List

from fastapi import Depends, HTTPException, APIRouter
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from database import get_db
from models import Post, Comment
import schemas

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.post("/", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    new_post = Post(title=post.title, content=post.content, user_id=post.user_id)

    categories = db.query(schemas.Category).filter(schemas.Category.id.in_(post.category_ids)).all()
    if not categories:
        raise HTTPException(status_code=404, detail="Categorias não encontradas")

    new_post.categories = categories

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get("/most-commented", response_model=List[schemas.PostWithCommentCount])
def read_most_commented_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    results = (
        db.query(
            Post,
            func.count(Comment.id).label("comment_count")
        )
        .outerjoin(Comment, Post.id == Comment.post_id)
        .group_by(Post.id)
        .order_by(func.count(Comment.id).desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    response_data = []
    for post_orm, count in results:
        post_data = schemas.Post.from_orm(post_orm).dict()
        post_data['comment_count'] = count
        response_data.append(schemas.PostWithCommentCount(**post_data))

    return response_data

post_crud_router = SQLAlchemyCRUDRouter(
    schema=schemas.Post,
    create_schema=schemas.PostCreate,
    db_model=Post,
    db=get_db
)

router.include_router(post_crud_router)