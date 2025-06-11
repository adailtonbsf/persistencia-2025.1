from ..models import Cliente, ClienteCreate, ClienteRead
from fastapi import APIRouter, Depends, HTTPException, Query
from ..database import get_session
from typing import List, Optional
from datetime import date
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

logger = get_logger("cliente")

@router.get("/", response_model=List[ClienteRead])
async def listar_clientes(
    session=Depends(get_session),
    nome: Optional[str] = None,
    email: Optional[str] = None,
    data_cadastro: Optional[date] = None,
    telefone: Optional[str] = None,
    cpf: Optional[str] = None,
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Limite de registros por página")
) -> List[Cliente]:
    query = session.query(Cliente)

    if nome:
        query = query.filter(Cliente.nome.ilike(f"%{nome}%"))
    if email:
        query = query.filter(Cliente.email.ilike(f"%{email}%"))
    if data_cadastro:
        query = query.filter(Cliente.data_cadastro == data_cadastro)
    if telefone:
        query = query.filter(Cliente.telefone.ilike(f"%{telefone}%"))
    if cpf:
        query = query.filter(Cliente.cpf.ilike(f"%{cpf}%"))

    skip = (page - 1) * limit
    clientes = query.offset(skip).limit(limit).all()
    return clientes

@router.get("/count", response_model=int)
async def contar_clientes(session=Depends(get_session)) -> int:
    total = session.query(Cliente).count()
    return total

@router.get("/{cliente_id}", response_model=ClienteRead)
async def obter_cliente(cliente_id: int, session=Depends(get_session)) -> Cliente:
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente

@router.post("/", response_model=ClienteRead)
async def criar_cliente(cliente_data: ClienteCreate, session=Depends(get_session)) -> Cliente:
    db_cliente = Cliente.model_validate(cliente_data)
    session.add(db_cliente)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao criar cliente: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    session.refresh(db_cliente)
    logger.info(f"Cliente criado: {db_cliente.nome} (ID: {db_cliente.id})")
    return db_cliente

@router.put("/{cliente_id}", response_model=ClienteRead)
async def atualizar_cliente(cliente_id: int, cliente_update: ClienteCreate, session=Depends(get_session)) -> Cliente:
    db_cliente = session.get(Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    update_data = cliente_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_cliente, key, value)

    session.add(db_cliente)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao atualizar cliente ID {cliente_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    session.refresh(db_cliente)
    logger.info(f"Cliente atualizado: {db_cliente.nome} (ID: {db_cliente.id})")
    return db_cliente

@router.delete("/{cliente_id}", response_model=dict)
async def excluir_cliente(cliente_id: int, session=Depends(get_session)) -> dict:
    cliente = session.get(Cliente, cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    session.delete(cliente)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao excluir cliente ID {cliente_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(f"Cliente excluído: {cliente.nome} (ID: {cliente.id})")
    return {"message": "Cliente excluído com sucesso"}