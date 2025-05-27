from fastapi import FastAPI
from fastapi_crudrouter import SQLAlchemyCRUDRouter
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

user_router = SQLAlchemyCRUDRouter(
    schema=User,
    db_model=User,
    db=SessionLocal,
    prefix="Users"
)

app.include_router(user_router)
