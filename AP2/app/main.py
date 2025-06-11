from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from contextlib import asynccontextmanager
from app.api import cliente, pedido, funcionario, pedido_prato, prato

@asynccontextmanager
async def lifespan(_):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

app.include_router(cliente.router)
app.include_router(pedido.router)
app.include_router(funcionario.router)
app.include_router(pedido_prato.router)
app.include_router(prato.router)