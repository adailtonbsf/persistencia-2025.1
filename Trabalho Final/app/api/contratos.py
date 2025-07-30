import ast
import csv
from datetime import datetime
from io import StringIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.models.contrato import Contrato, ContratoDetalhe
from app.models.fornecedor import Fornecedor
from app.models.orgao import Orgao
from app.schemas.Contrato import ContratoRead, ContratoCreate
from app.database import get_session
from app.utils.logger import logger
from app.scripts.populate_db import get_or_create_fornecedor

router = APIRouter(prefix="/contratos", tags=["Contratos"])

@router.post("/", response_model=ContratoRead)
def create_contrato(contrato: ContratoCreate, session: Session = Depends(get_session)):
    db_contrato = Contrato(**contrato.model_dump())
    session.add(db_contrato)
    session.commit()
    session.refresh(db_contrato)
    logger.info(f"Contrato criado: {db_contrato.id}")
    return db_contrato

@router.post("/upload-csv")
def upload_csv_contratos(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    contratos_adicionados = 0

    for row in reader:
        try:
            contato_id = row.get('id')

            contrato_existente = session.exec(select(Contrato).where(Contrato.id == contato_id)).first()
            if contrato_existente:
                continue

            try:
                unidade_gestora_dict = ast.literal_eval(row.get('unidadeGestora', '{}'))
                orgao_codigo = unidade_gestora_dict.get('orgaoMaximo', {}).get('codigo')
            except (ValueError, SyntaxError):
                print(
                    f"Aviso: Formato inválido na coluna 'unidadeGestora' para o contrato {row.get('numero')}. Pulando.")
                continue

            if not orgao_codigo:
                print(f"Aviso: Código do órgão não encontrado para o contrato {row.get('numero')}. Pulando.")
                continue

            orgao = session.exec(select(Orgao).where(Orgao.codigo_siafi == orgao_codigo)).first()
            if not orgao:
                print(
                    f"Aviso: Órgão com código {orgao_codigo} não encontrado no DB. Pulando contrato {row.get('numero')}.")
                continue

            fornecedor = get_or_create_fornecedor(session, row)
            if not fornecedor:
                print(f"Aviso: Fornecedor não pôde ser identificado para o contrato {row.get('numero')}. Pulando.")
                continue

            try:
                data_assinatura_str = row.get('dataAssinatura')
                data_inicio_str = row.get('dataInicioVigencia')
                data_fim_str = row.get('dataFimVigencia')

                data_assinatura = datetime.strptime(data_assinatura_str,
                                                    '%Y-%m-%d').date() if data_assinatura_str else None
                data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date() if data_inicio_str else None
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date() if data_fim_str else None

                valor = float(row.get('valorInicialCompra', '0.0').replace(',', '.'))
            except (ValueError, KeyError) as e:
                print(f"Aviso: Formato de data/valor inválido para o contrato {row.get('numero')}: {e}. Pulando.")
                continue

            novo_contrato = Contrato(
                id=contato_id,
                numero=row.get('numero'),
                objeto=row.get('objeto', 'Não informado'),
                fundamento_legal=row.get('fundamentoLegal', 'Não informado'),
                valor_inicial=valor,
                data_assinatura=data_assinatura,
                data_inicio_vigencia=data_inicio,
                data_fim_vigencia=data_fim,
                orgao_id=orgao.id,
                fornecedor_id=fornecedor.id
            )
            session.add(novo_contrato)
            session.flush()

            compra_dict = ast.literal_eval(row.get('compra', '{}'))

            detalhes_contrato = ContratoDetalhe(
                modalidade_licitacao_origem=compra_dict.get('modalidadeCompra', 'Não informada'),
                numero_licitacao_origem=compra_dict.get('numeroProcesso', 'Não informado'),
                contrato_id=novo_contrato.id
            )
            session.add(detalhes_contrato)

            contratos_adicionados += 1
        except (ValueError, SyntaxError, KeyError) as e:
            print(f"Erro ao processar linha do contrato: {e} - Linha: {row}")
            continue

    if contratos_adicionados > 0:
        session.commit()
    logger.info(f"Importação de {contratos_adicionados} contratos realizada via CSV.")
    return {"importados": contratos_adicionados}

@router.get("/", response_model=list[ContratoRead])
def list_contratos(
    session: Session = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    contratos = session.exec(
        select(Contrato).options(selectinload(Contrato.detalhes)).offset(offset).limit(limit)
    ).all()
    return contratos

@router.get("/por-fornecedor/{fornecedor_id}", response_model=List[ContratoRead])
def contratos_por_fornecedor(
    fornecedor_id: int,
    session: Session = Depends(get_session)
):
    contratos = session.exec(
        select(Contrato).where(Contrato.fornecedor_id == fornecedor_id)
    ).all()
    if not contratos:
        raise HTTPException(status_code=404, detail="Nenhum contrato encontrado para este fornecedor")
    return contratos

@router.get("/valor-total-por-fornecedor/{fornecedor_id}")
def valor_total_contratos_por_fornecedor(
    fornecedor_id: int,
    session: Session = Depends(get_session)
):
    result = session.exec(
        select(Fornecedor, func.sum(Contrato.valor_inicial))
        .join(Contrato, Contrato.fornecedor_id == Fornecedor.id)
        .where(Fornecedor.id == fornecedor_id)
        .group_by(Fornecedor.id)
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado ou sem contratos")
    fornecedor, total = result
    return {
        "fornecedor": {
            "id": fornecedor.id,
            "cpf_cnpj": fornecedor.cpf_cnpj,
            "nome": fornecedor.nome,
            "razao_social": fornecedor.razao_social,
            "tipo_pessoa": fornecedor.tipo_pessoa
        },
        "valor_total_contratos": total or 0.0
    }

@router.get("/{contrato_id}", response_model=ContratoRead)
def get_contrato(contrato_id: int, session: Session = Depends(get_session)):
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    return contrato

@router.put("/{contrato_id}", response_model=ContratoRead)
def update_contrato(contrato_id: int, contrato: ContratoCreate, session: Session = Depends(get_session)):
    db_contrato = session.get(Contrato, contrato_id)
    if not db_contrato:
        logger.warning(f"Tentativa de atualização de contrato não encontrado: {contrato_id}")
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    for key, value in contrato.model_dump().items():
        setattr(db_contrato, key, value)
    session.add(db_contrato)
    session.commit()
    session.refresh(db_contrato)
    logger.info(f"Contrato atualizado: {contrato_id}")
    return db_contrato

@router.delete("/{contrato_id}")
def delete_contrato(contrato_id: int, session: Session = Depends(get_session)):
    contrato = session.get(Contrato, contrato_id)
    if not contrato:
        logger.warning(f"Tentativa de exclusão de contrato não encontrado: {contrato_id}")
        raise HTTPException(status_code=404, detail="Contrato não encontrado")
    session.delete(contrato)
    session.commit()
    logger.info(f"Contrato excluído: {contrato_id}")
    return {"ok": True}