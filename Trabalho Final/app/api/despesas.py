import ast
import csv
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select
from app.models.despesa import Despesa
from app.schemas.Despesa import DespesaRead, DespesaCreate
from app.database import get_session
from app.scripts.populate_db import parse_date
from app.utils.logger import logger

router = APIRouter(prefix="/despesas", tags=["Despesas"])

@router.post("/", response_model=DespesaRead)
def create_despesa(despesa: DespesaCreate, session: Session = Depends(get_session)):
    logger.info(f"Criando despesa: {despesa.model_dump()}")
    db_despesa = Despesa(**despesa.model_dump())
    session.add(db_despesa)
    session.commit()
    session.refresh(db_despesa)
    logger.info(f"Despesa criada com ID: {db_despesa.id}")
    return db_despesa

@router.post("/upload-csv")
async def upload_despesas_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    content = await file.read()
    decoded = content.decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))
    despesas_adicionadas = 0
    for row in reader:
        documento_resumido = row.get('documentoResumido')
        if not documento_resumido:
            continue

        existing_despesa = session.exec(
            select(Despesa).where(Despesa.documento_resumido == documento_resumido)
        ).first()
        if existing_despesa:
            continue

        valor_str = row.get('valor', '0')
        valor_limpo_str = valor_str.replace('.', '').replace(',', '.').replace(' ', '')
        try:
            valor = float(valor_limpo_str)
        except ValueError:
            continue

        data_emissao = parse_date(row.get('data'))

        favorecido_nome = 'Não informado'
        favorecido_str = row.get('favorecido')
        if favorecido_str:
            try:
                favorecido_dict = ast.literal_eval(favorecido_str)
                if isinstance(favorecido_dict, dict):
                    favorecido_nome = favorecido_dict.get('nome', 'Não informado')
            except (ValueError, SyntaxError):
                favorecido_nome = row.get('nomeFavorecido', 'Não informado')

        numero_processo = row.get('numeroProcesso')

        nova_despesa = Despesa(
            documento_resumido=documento_resumido,
            numero_processo=numero_processo,
            fase=row.get('fase', ''),
            especie=row.get('especie', ''),
            favorecido_nome=favorecido_nome,
            valor=valor,
            data_emissao=data_emissao
        )
        session.add(nova_despesa)
        despesas_adicionadas += 1
    if despesas_adicionadas > 0:
        session.commit()
    logger.info(f"Importação de {despesas_adicionadas} despesas realizada via CSV.")
    return {"importadas": despesas_adicionadas}

@router.get("/", response_model=list[DespesaRead])
def list_despesas(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    session: Session = Depends(get_session)
):
    despesas = session.exec(select(Despesa).offset(offset).limit(limit)).all()
    return despesas

@router.get("/{despesa_id}", response_model=DespesaRead)
def get_despesa(despesa_id: int, session: Session = Depends(get_session)):
    despesa = session.get(Despesa, despesa_id)
    if not despesa:
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    return despesa

@router.put("/{despesa_id}", response_model=DespesaRead)
def update_despesa(despesa_id: int, despesa: DespesaCreate, session: Session = Depends(get_session)):
    logger.info(f"Atualizando despesa com ID: {despesa_id}")
    db_despesa = session.get(Despesa, despesa_id)
    if not db_despesa:
        logger.warning(f"Despesa com ID {despesa_id} não encontrada para atualização")
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    for key, value in despesa.model_dump().items():
        setattr(db_despesa, key, value)
    session.add(db_despesa)
    session.commit()
    session.refresh(db_despesa)
    logger.info(f"Despesa com ID {despesa_id} atualizada")
    return db_despesa

@router.delete("/{despesa_id}")
def delete_despesa(despesa_id: int, session: Session = Depends(get_session)):
    logger.info(f"Excluindo despesa com ID: {despesa_id}")
    despesa = session.get(Despesa, despesa_id)
    if not despesa:
        logger.warning(f"Despesa com ID {despesa_id} não encontrada para exclusão")
        raise HTTPException(status_code=404, detail="Despesa não encontrada")
    session.delete(despesa)
    session.commit()
    logger.info(f"Despesa com ID {despesa_id} excluída")
    return {"ok": True}