from ..models import Funcionario, FuncionarioRead, FuncionarioCreate
from fastapi import APIRouter, Depends, HTTPException, Query
from ..database import get_session
from typing import List, Optional
from datetime import date
from app.utils.logger import get_logger

router = APIRouter(
    prefix="/funcionarios",
    tags=["Funcionários"]
)

logger = get_logger("funcionario")

@router.get("/", response_model=List[FuncionarioRead])
async def listar_funcionarios(
    session=Depends(get_session),
    nome: Optional[str] = None,
    email: Optional[str] = None,
    cargo: Optional[str] = None,
    data_admissao: Optional[date] = None,
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Quantidade por página")
) -> List[FuncionarioRead]:
    query = session.query(Funcionario)

    if nome:
        query = query.filter(Funcionario.nome.ilike(f"%{nome}%"))
    if email:
        query = query.filter(Funcionario.email.ilike(f"%{email}%"))
    if cargo:
        query = query.filter(Funcionario.cargo.ilike(f"%{cargo}%"))
    if data_admissao:
        query = query.filter(Funcionario.data_admissao == data_admissao)

    offset = (page - 1) * limit
    funcionarios = query.offset(offset).limit(limit).all()
    return funcionarios

@router.get("/count", response_model=int)
async def contar_funcionarios(session=Depends(get_session)) -> int:
    total = session.query(Funcionario).count()
    return total

@router.get("/{funcionario_id}", response_model=FuncionarioRead)
async def obter_funcionario(funcionario_id: int, session=Depends(get_session)) -> FuncionarioRead:
    funcionario = session.get(Funcionario, funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return funcionario

@router.post("/", response_model=FuncionarioRead)
async def criar_funcionario(funcionario_data: FuncionarioCreate, session=Depends(get_session)) -> FuncionarioRead:
    db_funcionario = Funcionario.model_validate(funcionario_data)
    session.add(db_funcionario)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao criar funcionário: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    session.refresh(db_funcionario)
    logger.info(f"Funcionário {db_funcionario.nome} criado com sucesso")
    return db_funcionario

@router.put("/{funcionario_id}", response_model=FuncionarioRead)
async def atualizar_funcionario(funcionario_id: int, funcionario_update: FuncionarioCreate, session=Depends(get_session)) -> FuncionarioRead:
    db_funcionario = session.get(Funcionario, funcionario_id)
    if not db_funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    update_data = funcionario_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_funcionario, key, value)

    session.add(db_funcionario)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao atualizar funcionário: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    session.refresh(db_funcionario)
    logger.info(f"Funcionário {db_funcionario.nome} atualizado com sucesso")
    return db_funcionario

@router.delete("/{funcionario_id}", response_model=dict)
async def excluir_funcionario(funcionario_id: int, session=Depends(get_session)) -> dict:
    funcionario = session.get(Funcionario, funcionario_id)
    if not funcionario:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")

    session.delete(funcionario)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro ao excluir funcionário: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    logger.info(f"Funcionário {funcionario.nome} excluído com sucesso")
    return {"message": "Funcionário excluído com sucesso"}