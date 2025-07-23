from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from odmantic import ObjectId, query

from app.config.database import engine
from app.models.local import Local

router = APIRouter(
    prefix="/locais",
    tags=["Locais"]
)

@router.get("/", response_model=List[Local])
async def list_locais(
        cidade: Optional[str] = Query(None, description="Filtrar locais por cidade"),
        page: int = Query(1, ge=1, description="Número da página"),
        limit: int = Query(10, ge=1, le=100, description="Resultados por página")
):
    skip = (page - 1) * limit

    queries = []
    if cidade:
        queries.append(query.match(Local.cidade, f"(?i).*{cidade}.*"))

    locais = await engine.find(Local, *queries, skip=skip, limit=limit)
    return locais

@router.get("/count", response_model=int)
async def count_locais():
    count = await engine.count(Local)
    return count


@router.get("/{id}", response_model=Local)
async def get_local_by_id(id: ObjectId):
    local = await engine.find_one(Local, Local.id == id)
    if local is None:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return local

@router.post("/", response_model=Local, status_code=201)
async def create_local(local: Local):
    await engine.save(local)
    return local


@router.put("/{id}", response_model=Local)
async def update_local(id: ObjectId, patch: Local):
    local = await engine.find_one(Local, Local.id == id)
    if local is None:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    patch_dict = patch.model_dump(exclude_unset=True)
    for key, value in patch_dict.items():
        setattr(local, key, value)

    await engine.save(local)
    return local


@router.delete("/{id}", status_code=204)
async def delete_local(id: ObjectId):
    local = await engine.find_one(Local, Local.id == id)
    if local is None:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    await engine.delete(local)
    return Response(status_code=204)