from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, HTTPException, Query, Response
from odmantic import ObjectId

from app.config.database import engine
from app.models.ingresso import Ingresso, IngressoCreate
from app.models.evento import Evento
from app.models.participante import Participante


router = APIRouter(
    prefix="/ingressos",
    tags=["Ingressos"]
)

@router.get("/", response_model=List[Ingresso])
async def list_ingressos(
        data: Optional[str] = Query(None, description="Filtrar ingressos por data da compra (formato: AAAA-MM-DD)"),
        page: int = Query(1, ge=1, description="Número da página"),
        limit: int = Query(10, ge=1, le=100, description="Resultados por página")
):
    skip = (page - 1) * limit

    queries = []
    if data:
        try:
            filter_date = date.fromisoformat(data)
            start_datetime = datetime.combine(filter_date, datetime.min.time())
            end_datetime = start_datetime + timedelta(days=1)
            queries.append(Ingresso.data_compra >= start_datetime)
            queries.append(Ingresso.data_compra < end_datetime)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de data inválido. Use AAAA-MM-DD.")

    ingressos = await engine.find(Ingresso, *queries, skip=skip, limit=limit)
    return ingressos


@router.get("/count", response_model=int)
async def count_ingressos():
    count = await engine.count(Ingresso)
    return count


@router.get("/{id}", response_model=Ingresso)
async def get_ingresso_by_id(id: ObjectId):
    ingresso = await engine.find_one(Ingresso, Ingresso.id == id)
    if ingresso is None:
        raise HTTPException(status_code=404, detail="Ingresso não encontrado")
    return ingresso

@router.post("/", response_model=Ingresso, status_code=201)
async def create_ingresso(ingresso_data: IngressoCreate):
    # Busca o evento e o participante pelos IDs fornecidos
    evento = await engine.find_one(Evento, Evento.id == ingresso_data.evento)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    participante = await engine.find_one(Participante, Participante.id == ingresso_data.participante)
    if participante is None:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    ingresso = Ingresso(
        tipo=ingresso_data.tipo,
        preco=ingresso_data.preco,
        evento=evento,
        participante=participante,
        data_compra=datetime.now()
    )
    await engine.save(ingresso)
    return ingresso


@router.put("/{id}", response_model=Ingresso)
async def update_ingresso(id: ObjectId, patch: IngressoCreate):
    ingresso = await engine.find_one(Ingresso, Ingresso.id == id)
    if ingresso is None:
        raise HTTPException(status_code=404, detail="Ingresso não encontrado")

    patch_dict = patch.model_dump(exclude_unset=True)

    if 'evento' in patch_dict:
        evento = await engine.find_one(Evento, Evento.id == patch_dict['evento'])
        if evento is None:
            raise HTTPException(status_code=404, detail="Evento para atualização não encontrado")
        ingresso.evento = evento
        del patch_dict['evento']

    if 'participante' in patch_dict:
        participante = await engine.find_one(Participante, Participante.id == patch_dict['participante'])
        if participante is None:
            raise HTTPException(status_code=404, detail="Participante para atualização não encontrado")
        ingresso.participante = participante
        del patch_dict['participante']

    for key, value in patch_dict.items():
        setattr(ingresso, key, value)

    await engine.save(ingresso)
    return ingresso


@router.delete("/{id}", status_code=204)
async def delete_ingresso(id: ObjectId):
    ingresso = await engine.find_one(Ingresso, Ingresso.id == id)
    if ingresso is None:
        raise HTTPException(status_code=404, detail="Ingresso não encontrado")
    await engine.delete(ingresso)
    return Response(status_code=204)