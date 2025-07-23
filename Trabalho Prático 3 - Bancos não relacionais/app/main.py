from fastapi import FastAPI
from app.routes import eventos, participantes, palestrantes, locais, ingressos

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API de Eventos!"}

app.include_router(locais.router)
app.include_router(participantes.router)
app.include_router(palestrantes.router)
app.include_router(ingressos.router)
app.include_router(eventos.router)