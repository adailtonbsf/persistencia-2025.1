from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.models.contrato import ContratoDetalhe
from app.schemas.Contrato import ContratoDetalheRead, ContratoDetalheCreate
from app.database import get_session
from app.utils.logger import logger

router = APIRouter(prefix="/contratos-detalhes", tags=["ContratoDetalhe"])

@router.post("/", response_model=ContratoDetalheRead)
def create_contrato_detalhe(contrato_detalhe: ContratoDetalheCreate, session: Session = Depends(get_session)):
    db_contrato_detalhe = ContratoDetalhe(**contrato_detalhe.model_dump())
    session.add(db_contrato_detalhe)
    session.commit()
    session.refresh(db_contrato_detalhe)
    logger.info(f"ContratoDetalhe criado: {db_contrato_detalhe.id}")
    return db_contrato_detalhe

@router.get("/", response_model=List[ContratoDetalheRead])
def list_contratos_detalhes(
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    contratos_detalhes = session.exec(
        select(ContratoDetalhe).offset(offset).limit(limit)
    ).all()
    return contratos_detalhes

@router.put("/{contrato_detalhe_id}", response_model=ContratoDetalheRead)
def update_contrato_detalhe(contrato_detalhe_id: int, contrato_detalhe: ContratoDetalheCreate, session: Session = Depends(get_session)):
    db_contrato_detalhe = session.get(ContratoDetalhe, contrato_detalhe_id)
    if not db_contrato_detalhe:
        logger.warning(f"Tentativa de atualizar ContratoDetalhe inexistente: {contrato_detalhe_id}")
        raise HTTPException(status_code=404, detail="ContratoDetalhe não encontrado")
    for key, value in contrato_detalhe.model_dump().items():
        setattr(db_contrato_detalhe, key, value)
    session.add(db_contrato_detalhe)
    session.commit()
    session.refresh(db_contrato_detalhe)
    logger.info(f"ContratoDetalhe atualizado: {contrato_detalhe_id}")
    return db_contrato_detalhe

@router.delete("/{contrato_detalhe_id}")
def delete_contrato_detalhe(contrato_detalhe_id: int, session: Session = Depends(get_session)):
    contrato_detalhe = session.get(ContratoDetalhe, contrato_detalhe_id)
    if not contrato_detalhe:
        logger.warning(f"Tentativa de deletar ContratoDetalhe inexistente: {contrato_detalhe_id}")
        raise HTTPException(status_code=404, detail="ContratoDetalhe não encontrado")
    session.delete(contrato_detalhe)
    session.commit()
    logger.info(f"ContratoDetalhe deletado: {contrato_detalhe_id}")
    return {"ok": True}