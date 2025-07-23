from typing import List
from fastapi import APIRouter, HTTPException, Query, Response
from odmantic import ObjectId
from app.config.database import engine
from app.models.palestrante import Palestrante

router = APIRouter(
    prefix="/palestrantes",
    tags=["Palestrantes"]
)

@router.get("/", response_model=List[Palestrante])
async def list_palestrantes(
        page: int = Query(1, ge=1, description="Número da página"),
        limit: int = Query(10, ge=1, le=100, description="Resultados por página")
):
    skip = (page - 1) * limit
    palestrantes = await engine.find(Palestrante, skip=skip, limit=limit)
    return palestrantes

@router.get("/count", response_model=int)
async def count_palestrantes():
    count = await engine.count(Palestrante)
    return count

@router.get("/{id}", response_model=Palestrante)
async def get_palestrante_by_id(id: ObjectId):
    palestrante = await engine.find_one(Palestrante, Palestrante.id == id)
    if palestrante is None:
        raise HTTPException(status_code=404, detail="Palestrante não encontrado")
    return palestrante

@router.post("/", response_model=Palestrante, status_code=201)
async def create_palestrante(palestrante: Palestrante):
    await engine.save(palestrante)
    return palestrante

@router.put("/{id}", response_model=Palestrante)
async def update_palestrante(id: ObjectId, patch: Palestrante):
    palestrante = await engine.find_one(Palestrante, Palestrante.id == id)
    if palestrante is None:
        raise HTTPException(status_code=404, detail="Palestrante não encontrado")

    patch_dict = patch.model_dump(exclude_unset=True)
    for key, value in patch_dict.items():
        setattr(palestrante, key, value)

    await engine.save(palestrante)
    return palestrante

@router.delete("/{id}", status_code=204)
async def delete_palestrante(id: ObjectId):
    palestrante = await engine.find_one(Palestrante, Palestrante.id == id)
    if palestrante is None:
        raise HTTPException(status_code=404, detail="Palestrante não encontrado")
    await engine.delete(palestrante)
    return Response(status_code=204)