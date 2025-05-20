from fastapi import FastAPI
from app.api import cliente, cardapio, pedido

app = FastAPI()

@app.get("/")
def home():
    return {"msg": "Home"}

app.include_router(cliente.router)
app.include_router(cardapio.router)
app.include_router(pedido.router)