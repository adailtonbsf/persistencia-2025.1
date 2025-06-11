from ..models import Pedido, PedidoRead, PedidoCreate, FormaPagamento, StatusPedido, Cliente, Funcionario
from fastapi import APIRouter, Depends, HTTPException, Query
from ..database import get_session
from typing import List, Optional
from datetime import datetime
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

logger = get_logger("pedido")

@router.get("/", response_model=List[PedidoRead])
async def listar_pedidos(
    session=Depends(get_session),
    status: Optional[StatusPedido] = None,
    cliente_id: Optional[int] = None,
    funcionario_id: Optional[int] = None,
    forma_pagamento: Optional[FormaPagamento] = None,
    data_pedido: Optional[datetime] = None,
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
) -> List[PedidoRead]:
    query = session.query(Pedido)

    if status:
        query = query.filter(Pedido.status.ilike(f"%{status}%"))
    if cliente_id:
        query = query.filter(Pedido.cliente_id == cliente_id)
    if funcionario_id:
        query = query.filter(Pedido.funcionario_id == funcionario_id)
    if data_pedido:
        query = query.filter(Pedido.data_pedido == data_pedido)
    if forma_pagamento:
        query = query.filter(Pedido.forma_pagamento.ilike(f"%{forma_pagamento}%"))

    offset = (page - 1) * limit
    pedidos = query.offset(offset).limit(limit).all()
    return pedidos

@router.get("/count", response_model=int)
async def contar_pedidos(session=Depends(get_session)) -> int:
    total = session.query(Pedido).count()
    return total

@router.get("/{pedido_id}", response_model=PedidoRead)
async def obter_pedido(pedido_id: int, session=Depends(get_session)) -> PedidoRead:
    pedido = session.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido

@router.post("/", response_model=PedidoRead)
async def criar_pedido(pedido_data: PedidoCreate, session=Depends(get_session)) -> PedidoRead:
    cliente = session.get(Cliente, pedido_data.cliente_id)
    if not cliente:
        raise HTTPException(status_code=400, detail="Cliente não encontrado")

    funcionario = session.get(Funcionario, pedido_data.funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=400, detail="Funcionário não encontrado")

    db_pedido = Pedido.model_validate(pedido_data)
    session.add(db_pedido)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao criar pedido: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    session.refresh(db_pedido)
    logger.info(f"Pedido criado: {db_pedido.id} (Cliente: {cliente.nome}, Funcionário: {funcionario.nome})")
    return db_pedido

@router.put("/{pedido_id}", response_model=PedidoRead)
async def atualizar_pedido(pedido_id: int, pedido_update: PedidoCreate, session=Depends(get_session)) -> PedidoRead:
    db_pedido = session.get(Pedido, pedido_id)
    if not db_pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    update_data = pedido_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pedido, key, value)

    session.add(db_pedido)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao atualizar pedido ID {pedido_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    session.refresh(db_pedido)
    logger.info(f"Pedido atualizado: {db_pedido.id} (Cliente: {db_pedido.cliente_id}, Funcionário: {db_pedido.funcionario_id})")
    return db_pedido

@router.delete("/{pedido_id}", response_model=dict)
async def excluir_pedido(pedido_id: int, session=Depends(get_session)) -> dict:
    pedido = session.get(Pedido, pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    session.delete(pedido)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao excluir pedido ID {pedido_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(f"Pedido excluído: {pedido.id} (Cliente: {pedido.cliente_id}, Funcionário: {pedido.funcionario_id})")
    return {"message": "Pedido excluído com sucesso"}