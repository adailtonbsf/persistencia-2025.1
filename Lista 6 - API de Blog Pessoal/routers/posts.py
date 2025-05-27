from fastapi import Depends
from fastapi_crudrouter import SQLAlchemyCRUDRouter

from .. import models, schemas, database

router = SQLAlchemyCRUDRouter(
    schema=schemas.Post,
    create_schema=schemas.PostCreate,
    db_model=models.Post,
    db=Depends(database.get_db),
    prefix="posts"
)