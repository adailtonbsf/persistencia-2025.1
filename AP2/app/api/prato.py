from ..models import Prato, PratoCreate, PratoRead
from fastapi import APIRouter, Depends, HTTPException, Query
from ..database import get_session
from typing import List, Optional
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/pratos",
    tags=["Pratos"]
)

logger = get_logger("prato")

@router.get("/", response_model=List[PratoRead])
async def listar_pratos(
    session=Depends(get_session),
    nome: Optional[str] = None,
    categoria: Optional[str] = None,
    disponibilidade: Optional[bool] = None,
    preco_minimo: Optional[float] = None,
    preco_maximo: Optional[float] = None,
    descricao: Optional[str] = None,
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
) -> List[PratoRead]:
    query = session.query(Prato)

    if nome:
        query = query.filter(Prato.nome.ilike(f"%{nome}%"))
    if categoria:
        query = query.filter(Prato.categoria.ilike(f"%{categoria}%"))
    if disponibilidade is not None:
        query = query.filter(Prato.disponibilidade == disponibilidade)
    if preco_minimo is not None:
        query = query.filter(Prato.preco >= preco_minimo)
    if preco_maximo is not None:
        query = query.filter(Prato.preco <= preco_maximo)
    if descricao:
        query = query.filter(Prato.descricao.ilike(f"%{descricao}%"))

    offset = (page - 1) * limit
    pratos = query.offset(offset).limit(limit).all()
    return pratos

@router.get("/count", response_model=int)
async def contar_pratos(session=Depends(get_session)) -> int:
    total = session.query(Prato).count()
    return total

@router.get("/{prato_id}", response_model=PratoRead)
async def obter_prato(prato_id: int, session=Depends(get_session)) -> PratoRead:
    prato = session.get(Prato, prato_id)
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")
    return prato

@router.post("/", response_model=PratoRead)
async def criar_prato(prato_data: PratoCreate, session=Depends(get_session)) -> PratoRead:
    db_prato = Prato.model_validate(prato_data)
    session.add(db_prato)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao criar prato: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    session.refresh(db_prato)
    logger.info(f"Prato criado: {db_prato.nome} (ID: {db_prato.id})")
    return db_prato

@router.put("/{prato_id}", response_model=PratoRead)
async def atualizar_prato(prato_id: int, prato_update: PratoCreate, session=Depends(get_session)) -> PratoRead:
    db_prato = session.get(Prato, prato_id)
    if not db_prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    update_data = prato_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prato, key, value)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao atualizar prato ID {prato_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    session.refresh(db_prato)
    logger.info(f"Prato atualizado: {db_prato.nome} (ID: {db_prato.id})")
    return db_prato

@router.delete("/{prato_id}", response_model=PratoRead)
async def excluir_prato(prato_id: int, session=Depends(get_session)) -> PratoRead:
    prato = session.get(Prato, prato_id)
    if not prato:
        raise HTTPException(status_code=404, detail="Prato não encontrado")

    session.delete(prato)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao excluir prato ID {prato_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(f"Prato excluído: {prato.nome} (ID: {prato.id})")
    return prato