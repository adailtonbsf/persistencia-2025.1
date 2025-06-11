from fastapi import APIRouter
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from database import get_db
from models import Like
import schemas

router = APIRouter(
    prefix="/likes",
    tags=["likes"]
)

like_crud_router = SQLAlchemyCRUDRouter(
    schema=schemas.Like,
    create_schema=schemas.LikeCreate,
    db_model=Like,
    db=get_db
)

router.include_router(like_crud_router)