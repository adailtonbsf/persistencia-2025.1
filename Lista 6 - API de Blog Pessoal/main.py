from fastapi import FastAPI

from database import Base, engine
from routers import users, posts, comments, categories, likes

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Hello World"}

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(categories.router)
app.include_router(likes.router)

