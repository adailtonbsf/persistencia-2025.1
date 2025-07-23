from typing import List
from fastapi import APIRouter, HTTPException, Query, Response
from odmantic import ObjectId
from app.config.database import engine
from app.models.participante import Participante

router = APIRouter(
    prefix="/participantes",
    tags=["Participantes"]
)

@router.get("/", response_model=List[Participante])
async def list_participantes(
        page: int = Query(1, ge=1, description="Número da página"),
        limit: int = Query(10, ge=1, le=100, description="Resultados por página")
):
    skip = (page - 1) * limit
    participantes = await engine.find(Participante, skip=skip, limit=limit)
    return participantes

@router.get("/count", response_model=int)
async def count_participantes():
    count = await engine.count(Participante)
    return count


@router.get("/{id}", response_model=Participante)
async def get_participante_by_id(id: ObjectId):
    participante = await engine.find_one(Participante, Participante.id == id)
    if participante is None:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    return participante

@router.post("/", response_model=Participante, status_code=201)
async def create_participante(participante: Participante):
    await engine.save(participante)
    return participante


@router.put("/{id}", response_model=Participante)
async def update_participante(id: ObjectId, patch: Participante):
    participante = await engine.find_one(Participante, Participante.id == id)
    if participante is None:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    patch_dict = patch.model_dump(exclude_unset=True)
    for key, value in patch_dict.items():
        setattr(participante, key, value)

    await engine.save(participante)
    return participante


@router.delete("/{id}", status_code=204)
async def delete_participante(id: ObjectId):
    participante = await engine.find_one(Participante, Participante.id == id)
    if participante is None:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    await engine.delete(participante)
    return Response(status_code=204)