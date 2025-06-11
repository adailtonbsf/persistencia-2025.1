from fastapi import APIRouter
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from database import get_db
from models import User
import schemas

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

user_crud_router = SQLAlchemyCRUDRouter(
    schema=schemas.User,
    create_schema=schemas.UserCreate,
    db_model=User,
    db=get_db
)

router.include_router(user_crud_router)