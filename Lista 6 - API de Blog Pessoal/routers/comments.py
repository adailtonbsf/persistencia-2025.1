from fastapi import APIRouter
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from database import get_db
from models import Comment
import schemas

router = APIRouter(
    prefix="/comments",
    tags=["comments"]
)

comment_crud_router = SQLAlchemyCRUDRouter(
    schema=schemas.Comment,
    create_schema=schemas.CommentCreate,
    db_model=Comment,
    db=get_db
)

router.include_router(comment_crud_router)