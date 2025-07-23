from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Response
from odmantic import ObjectId
from odmantic.query import desc, asc

from app.config.database import engine
from app.models.evento import Evento
from app.models.local import Local
from app.models.palestrante import Palestrante
from app.models.participante import Participante

router = APIRouter(
    prefix="/eventos",
    tags=["Eventos"]
)

@router.get("/", response_model=List[Evento])
async def list_eventos(
        page: int = Query(1, ge=1, description="Número da página"),
        limit: int = Query(10, ge=1, le=100, description="Resultados por página"),
        order_by: Optional[str] = Query("data_inicio", description="Campo para ordenação. Use '-' como prefixo para ordem decrescente (ex: -titulo).")
):
    skip = (page - 1) * limit

    sort_expression = None
    if order_by:
        is_desc = order_by.startswith("-")
        field_name = order_by.lstrip("-")

        if hasattr(Evento, field_name):
            field = getattr(Evento, field_name)
            sort_expression = desc(field) if is_desc else asc(field)
        else:
            sort_expression = asc(Evento.data_inicio)

    eventos = await engine.find(Evento, skip=skip, limit=limit, sort=sort_expression)
    return eventos

@router.get("/count", response_model=int)
async def count_eventos():
    count = await engine.count(Evento)
    return count


@router.get("/{id}", response_model=Evento)
async def get_evento_by_id(id: ObjectId):
    evento = await engine.find_one(Evento, Evento.id == id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return evento


@router.post("/", response_model=Evento, status_code=201)
async def create_evento(
    titulo: str,
    descricao: str,
    data_inicio: str,
    data_fim: str,
    local_id: str,
    palestrantes_ids: List[str] = [],
    participantes_ids: List[str] = []
):
    local = await engine.find_one(Local, Local.id == ObjectId(local_id))
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")

    palestrante_object_ids = [ObjectId(pid) for pid in palestrantes_ids]
    if palestrantes_ids:
        count = await engine.count(Palestrante, Palestrante.id.in_(palestrante_object_ids))
        if count != len(palestrantes_ids):
            raise HTTPException(status_code=404, detail="Um ou mais palestrantes não encontrados")

    participante_object_ids = [ObjectId(pid) for pid in participantes_ids]
    if participantes_ids:
        count = await engine.count(Participante, Participante.id.in_(participante_object_ids))
        if count != len(participantes_ids):
            raise HTTPException(status_code=404, detail="Um ou mais participantes não encontrados")

    evento = Evento(
        titulo=titulo,
        descricao=descricao,
        data_inicio=data_inicio,
        data_fim=data_fim,
        local=local,
        palestrantes=palestrante_object_ids,
        participantes=participante_object_ids
    )
    await engine.save(evento)
    return evento


@router.put("/{id}", response_model=Evento)
async def update_evento(
    id: ObjectId,
    titulo: str = None,
    descricao: str = None,
    data_inicio: str = None,
    data_fim: str = None,
    local_id: str = None,
    palestrantes_ids: List[str] = None,
    participantes_ids: List[str] = None
):
    evento = await engine.find_one(Evento, Evento.id == id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if titulo is not None:
        evento.titulo = titulo
    if descricao is not None:
        evento.descricao = descricao
    if data_inicio is not None:
        evento.data_inicio = data_inicio
    if data_fim is not None:
        evento.data_fim = data_fim
    if local_id is not None:
        local = await engine.find_one(Local, Local.id == ObjectId(local_id))
        if not local:
            raise HTTPException(status_code=404, detail="Local não encontrado")
        evento.local = local
    if palestrantes_ids is not None:
        palestrante_object_ids = [ObjectId(pid) for pid in palestrantes_ids]
        count = await engine.count(Palestrante, Palestrante.id.in_(palestrante_object_ids))
        if count != len(palestrantes_ids):
            raise HTTPException(status_code=404, detail="Um ou mais palestrantes não encontrados")
        evento.palestrantes = palestrante_object_ids
    if participantes_ids is not None:
        participante_object_ids = [ObjectId(pid) for pid in participantes_ids]
        count = await engine.count(Participante, Participante.id.in_(participante_object_ids))
        if count != len(participantes_ids):
            raise HTTPException(status_code=404, detail="Um ou mais participantes não encontrados")
        evento.participantes = participante_object_ids

    await engine.save(evento)
    return evento


@router.delete("/{id}", status_code=204)
async def delete_evento(id: ObjectId):
    evento = await engine.find_one(Evento, Evento.id == id)
    if evento is None:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    await engine.delete(evento)
    return Response(status_code=204)

@router.get("/{id}/palestrantes", response_model=List[Palestrante], tags=["Palestrantes"])
async def list_speakers_event(id: ObjectId):
    evento = await engine.find_one(Evento, Evento.id == id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if not evento.palestrantes:
        return []
    palestrantes = await engine.find(Palestrante, Palestrante.id.in_(evento.palestrantes))
    return palestrantes


@router.post("/{id}/palestrantes/{palestrante_id}", response_model=Evento, tags=["Palestrantes"])
async def add_speaker_event(id: ObjectId, palestrante_id: ObjectId):
    evento = await engine.find_one(Evento, Evento.id == id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    palestrante = await engine.find_one(Palestrante, Palestrante.id == palestrante_id)
    if not palestrante:
        raise HTTPException(status_code=404, detail="Palestrante não encontrado")
    if palestrante_id not in evento.palestrantes:
        evento.palestrantes.append(palestrante_id)
        await engine.save(evento)
    return evento


@router.delete("/{id}/palestrantes/{palestrante_id}", response_model=Evento, tags=["Palestrantes"])
async def remove_speaker_event(id: ObjectId, palestrante_id: ObjectId):
    evento = await engine.find_one(Evento, Evento.id == id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if palestrante_id in evento.palestrantes:
        evento.palestrantes.remove(palestrante_id)
        await engine.save(evento)
    else:
        raise HTTPException(status_code=404, detail="Palestrante não encontrado no evento")
    return evento


@router.get("/{id}/participantes", response_model=List[Participante], tags=["Participantes"])
async def list_participants_event(id: ObjectId):
    evento = await engine.find_one(Evento, Evento.id == id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if not evento.participantes:
        return []
    participantes = await engine.find(Participante, Participante.id.in_(evento.participantes))
    return participantes


@router.post("/{id}/participantes/{participante_id}", response_model=Evento, tags=["Participantes"])
async def add_participant_event(id: ObjectId, participante_id: ObjectId):
    evento = await engine.find_one(Evento, Evento.id == id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    participante = await engine.find_one(Participante, Participante.id == participante_id)
    if not participante:
        raise HTTPException(status_code=404, detail="Participante não encontrado")
    if participante_id not in evento.participantes:
        evento.participantes.append(participante_id)
        await engine.save(evento)
    return evento


@router.delete("/{id}/participantes/{participante_id}", response_model=Evento, tags=["Participantes"])
async def remove_participant_event(id: ObjectId, participante_id: ObjectId):
    evento = await engine.find_one(Evento, Evento.id == id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    if participante_id in evento.participantes:
        evento.participantes.remove(participante_id)
        await engine.save(evento)
    else:
        raise HTTPException(status_code=404, detail="Participante não encontrado no evento")
    return evento