from Demos.mmapfile_demo import offset

from ..models import PedidoPrato, PedidoPratoRead, PedidoPratoCreate, Pedido, Prato
from fastapi import APIRouter, Depends, HTTPException, Query
from ..database import get_session
from typing import List, Optional
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/pedido_pratos",
    tags=["Pedido Pratos"]
)

logger = get_logger("pedido_prato")

@router.get("/", response_model=List[PedidoPratoRead])
async def listar_pedido_pratos(
    session=Depends(get_session),
    pedido_id: Optional[int] = None,
    prato_id: Optional[int] = None,
    quantidade_minima: Optional[int] = None,
    quantidade_maxima: Optional[int] = None,
    preco_unit_minimo: Optional[float] = None,
    preco_unit_maximo: Optional[float] = None,
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
) -> List[PedidoPratoRead]:
    query = session.query(PedidoPrato)

    if pedido_id:
        query = query.filter(PedidoPrato.pedido_id == pedido_id)
    if prato_id:
        query = query.filter(PedidoPrato.prato_id == prato_id)
    if quantidade_minima is not None:
        query = query.filter(PedidoPrato.quantidade >= quantidade_minima)
    if quantidade_maxima is not None:
        query = query.filter(PedidoPrato.quantidade <= quantidade_maxima)
    if preco_unit_minimo is not None:
        query = query.filter(PedidoPrato.preco_unitario >= preco_unit_minimo)
    if preco_unit_maximo is not None:
        query = query.filter(PedidoPrato.preco_unitario <= preco_unit_maximo)

    offset = (page - 1) * limit
    pedido_pratos = query.offset(offset).limit(limit).all()
    return pedido_pratos

@router.get("/count", response_model=int)
async def contar_pedido_prato(session=Depends(get_session)) -> int:
    total = session.query(PedidoPrato).count()
    return total

@router.get("/{pedido_prato_id}", response_model=PedidoPratoRead)
async def obter_pedido_prato(pedido_prato_id: int, session=Depends(get_session)) -> PedidoPratoRead:
    pedido_prato = session.get(PedidoPrato, pedido_prato_id)
    if not pedido_prato:
        raise HTTPException(status_code=404, detail="Pedido Prato não encontrado")
    return pedido_prato

@router.post("/", response_model=PedidoPratoRead)
async def criar_pedido_prato(pedido_prato_data: PedidoPratoCreate, session=Depends(get_session)) -> PedidoPratoRead:
    pedido = session.get(Pedido, pedido_prato_data.pedido_id)
    if not pedido:
        raise HTTPException(status_code=400, detail="Pedido não encontrado")

    prato = session.get(Prato, pedido_prato_data.prato_id)
    if not prato:
        raise HTTPException(status_code=400, detail="Prato não encontrado")

    db_pedido_prato = PedidoPrato.model_validate(pedido_prato_data)
    session.add(db_pedido_prato)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao criar Pedido Prato: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    session.refresh(db_pedido_prato)
    logger.info(f"Pedido Prato criado: {db_pedido_prato.id} (Pedido ID: {db_pedido_prato.pedido_id}, Prato ID: {db_pedido_prato.prato_id})")
    return db_pedido_prato

@router.put("/{pedido_prato_id}", response_model=PedidoPratoRead)
async def atualizar_pedido_prato(pedido_prato_id: int, pedido_prato_update: PedidoPratoCreate, session=Depends(get_session)) -> PedidoPratoRead:
    db_pedido_prato = session.get(PedidoPrato, pedido_prato_id)
    if not db_pedido_prato:
        raise HTTPException(status_code=404, detail="Pedido Prato não encontrado")

    update_data = pedido_prato_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pedido_prato, key, value)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao atualizar Pedido Prato ID {pedido_prato_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    session.refresh(db_pedido_prato)
    logger.info(f"Pedido Prato atualizado: {db_pedido_prato.id} (Pedido ID: {db_pedido_prato.pedido_id}, Prato ID: {db_pedido_prato.prato_id})")
    return db_pedido_prato

@router.delete("/{pedido_prato_id}", response_model=dict)
async def excluir_pedido_prato(pedido_prato_id: int, session=Depends(get_session)) -> dict:
    pedido_prato = session.get(PedidoPrato, pedido_prato_id)
    if not pedido_prato:
        raise HTTPException(status_code=404, detail="Pedido Prato não encontrado")

    session.delete(pedido_prato)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao excluir Pedido Prato ID {pedido_prato_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(f"Pedido Prato excluído: {pedido_prato.id} (Pedido ID: {pedido_prato.pedido_id}, Prato ID: {pedido_prato.prato_id})")
    return {"message": "Pedido Prato excluído com sucesso"}