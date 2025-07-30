import csv
import io
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.database import get_session
from app.models.contrato import Contrato
from app.models.despesa import Despesa
from app.models.fornecedor import Fornecedor
from app.models.orgao import Orgao
from app.schemas.Orgao import OrgaoRead, OrgaoCreate, OrgaoComContratosRead
from app.utils.logger import logger

router = APIRouter(prefix="/orgaos", tags=["Órgãos"])

@router.post("/", response_model=OrgaoRead)
def create_orgao(orgao: OrgaoCreate, session: Session = Depends(get_session)):
    db_orgao = Orgao(**orgao.model_dump())
    session.add(db_orgao)
    session.commit()
    session.refresh(db_orgao)
    logger.info(f"Órgão criado: {db_orgao.id} - {db_orgao.nome}")
    return db_orgao

@router.post("/upload-csv")
async def upload_orgaos_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="O arquivo deve ser CSV")
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    orgaos_adicionados = 0
    for row in reader:
        codigo_siafi = row.get("codigo")
        if not codigo_siafi or "CODIGO INVALIDO" in row.get("descricao", ""):
            continue
        if session.exec(select(Orgao).where(Orgao.codigo_siafi == codigo_siafi)).first():
            continue
        orgao = Orgao(
            codigo_siafi=codigo_siafi,
            descricao=row['descricao']
        )
        session.add(orgao)
        orgaos_adicionados += 1
    if orgaos_adicionados > 0:
        session.commit()
    return {"orgaos_adicionados": orgaos_adicionados}

@router.get("/", response_model=list[OrgaoRead])
def list_orgaos(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    session: Session = Depends(get_session)
):
    orgaos = session.exec(
        select(Orgao).offset(offset).limit(limit)
    ).all()
    return orgaos

@router.get("/com-contratos-acima", response_model=list[OrgaoComContratosRead])
def orgaos_com_contratos_acima(
    valor_minimo: float = Query(..., ge=0),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    orgaos = session.exec(
        select(Orgao)
        .options(selectinload(Orgao.contratos))
        .join(Contrato, Contrato.orgao_id == Orgao.id)
        .where(Contrato.valor_inicial > valor_minimo)
        .order_by(Orgao.descricao)
        .offset(offset)
        .limit(limit)
    ).unique().all()

    result = []
    for orgao in orgaos:
        contratos_filtrados = [c for c in orgao.contratos if c.valor_inicial > valor_minimo]
        if contratos_filtrados:
            orgao_dict = orgao.dict()
            orgao_dict["contratos"] = contratos_filtrados
            result.append(orgao_dict)
    return result

@router.get("/com-despesas-acima")
def orgaos_com_despesas_acima(
    valor_minimo: float = Query(..., ge=0),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = (
        select(Orgao, Despesa)
        .join(Contrato, Contrato.orgao_id == Orgao.id)
        .join(Fornecedor, Fornecedor.id == Contrato.fornecedor_id)
        .join(Despesa, Despesa.favorecido_nome == Fornecedor.nome)
        .where(Despesa.valor > valor_minimo)
    )

    if data_inicio and data_fim:
        query = query.where(Despesa.data_emissao.between(data_inicio, data_fim))
    elif data_inicio:
        query = query.where(Despesa.data_emissao >= data_inicio)
    elif data_fim:
        query = query.where(Despesa.data_emissao <= data_fim)

    query = query.order_by(Orgao.descricao).offset(offset).limit(limit)
    results = session.exec(query).all()
    return [
        {
            "orgao": orgao,
            "despesa": despesa
        }
        for orgao, despesa in results
    ]

@router.get("/{orgao_id}", response_model=OrgaoRead)
def get_orgao(orgao_id: int, session: Session = Depends(get_session)):
    orgao = session.get(Orgao, orgao_id)
    if not orgao:
        raise HTTPException(status_code=404, detail="Órgão não encontrado")
    return orgao

@router.get("/{orgao_id}/valor-total-despesas")
def valor_total_despesas_orgao(orgao_id: int, session: Session = Depends(get_session)):
    orgao = session.get(Orgao, orgao_id)
    if not orgao:
        raise HTTPException(status_code=404, detail="Órgão não encontrado")

    subquery = (
        select(Fornecedor.nome)
        .join(Contrato, Contrato.fornecedor_id == Fornecedor.id)
        .where(Contrato.orgao_id == orgao_id)
    )

    total_query = (
        select(func.sum(Despesa.valor).label("valor_total_despesas"))
        .where(Despesa.favorecido_nome.in_(subquery))
    )
    valor_total = session.exec(total_query).one()
    valor_total = valor_total if valor_total is not None else 0.0

    return {"orgao_id": orgao_id, "valor_total_despesas": valor_total}

@router.put("/{orgao_id}", response_model=OrgaoRead)
def update_orgao(orgao_id: int, orgao: OrgaoCreate, session: Session = Depends(get_session)):
    db_orgao = session.get(Orgao, orgao_id)
    if not db_orgao:
        logger.warning(f"Tentativa de atualização de órgão inexistente: {orgao_id}")
        raise HTTPException(status_code=404, detail="Órgão não encontrado")
    for key, value in orgao.model_dump().items():
        setattr(db_orgao, key, value)
    session.add(db_orgao)
    session.commit()
    session.refresh(db_orgao)
    logger.info(f"Órgão atualizado: {orgao_id}")
    return db_orgao

@router.delete("/{orgao_id}")
def delete_orgao(orgao_id: int, session: Session = Depends(get_session)):
    orgao = session.get(Orgao, orgao_id)
    if not orgao:
        logger.warning(f"Tentativa de exclusão de órgão inexistente: {orgao_id}")
        raise HTTPException(status_code=404, detail="Órgão não encontrado")
    session.delete(orgao)
    session.commit()
    logger.info(f"Órgão excluído: {orgao_id}")
    return {"ok": True}