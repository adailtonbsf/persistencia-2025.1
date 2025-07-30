import ast
import csv
from datetime import datetime
from io import StringIO

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.models.licitacao import Licitacao
from app.models.orgao import Orgao
from app.schemas.Licitacao import LicitacaoRead, LicitacaoCreate
from app.utils.logger import logger

router = APIRouter(prefix="/licitacoes", tags=["Licitações"])

@router.post("/", response_model=LicitacaoRead)
def create_licitacao(licitacao: LicitacaoCreate, session: Session = Depends(get_session)):
    db_licitacao = Licitacao(**licitacao.model_dump())
    session.add(db_licitacao)
    session.commit()
    session.refresh(db_licitacao)
    logger.info(f"Licitação criada: {db_licitacao.id}")
    return db_licitacao

@router.post("/upload-csv/")
async def upload_licitacoes_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    if file.content_type != "text/csv":
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    content = await file.read()
    csv_reader = csv.DictReader(StringIO(content.decode("utf-8")))
    licitacoes_adicionadas = 0
    for row in csv_reader:
        try:
            unidade_gestora_str = row.get('unidadeGestora')
            if not unidade_gestora_str:
                print("Aviso: Coluna 'unidadeGestora' não encontrada. Pulando linha.")
                continue

            unidade_gestora = ast.literal_eval(unidade_gestora_str)
            orgao_codigo = unidade_gestora.get('orgaoMaximo', {}).get('codigo')

            if not orgao_codigo:
                print(f"Aviso: Código do órgão não encontrado na 'unidadeGestora'. Pulando licitação.")
                continue

            orgao = session.exec(select(Orgao).where(Orgao.codigo_siafi == orgao_codigo)).first()
            if not orgao:
                print(f"Aviso: Órgão com código {orgao_codigo} não encontrado. Pulando licitação.")
                continue

            licitacao_info = ast.literal_eval(row.get('licitacao', '{}'))
            municipio_info = ast.literal_eval(row.get('municipio', '{}'))

            numero_processo = licitacao_info.get('numero')
            licitacao_id = row.get('id')
            if not numero_processo:
                print("Aviso: Número de processo não encontrado na licitação. Pulando linha.")
                continue

            existing_licitacao = session.exec(
                select(Licitacao).where(Licitacao.id == licitacao_id)).first()
            if existing_licitacao:
                print(f"Aviso: Licitação com número de processo {licitacao_id} já existe. Pulando.")
                continue

            nova_licitacao = Licitacao(
                id = licitacao_id,
                numero_processo=numero_processo,
                objeto=licitacao_info.get('objeto', 'Não informado'),
                modalidade=row.get('modalidadeLicitacao', 'Não informada'),
                situacao=row.get('situacaoCompra', 'Não informada'),
                valor_estimado=float(row.get('valor', 0.0)),
                data_abertura=datetime.strptime(row['dataAbertura'], '%Y-%m-%d').date(),
                data_publicacao=datetime.strptime(row['dataPublicacao'], '%Y-%m-%d').date(),
                municipio=municipio_info.get('nomeIBGE', 'Não informado'),
                uf=municipio_info.get('uf', {}).get('sigla', 'NI'),
                orgao_id=orgao.id
            )

            session.add(nova_licitacao)
            licitacoes_adicionadas += 1

        except (KeyError, TypeError, ValueError, ast.literal_eval) as e:
            print(f"Erro ao processar linha da licitação: {e} - Linha: {row}")
            continue
    if licitacoes_adicionadas > 0:
        session.commit()
    logger.info(f"Importação de {licitacoes_adicionadas} licitações realizada via CSV.")
    return {"importados": licitacoes_adicionadas}

@router.get("/", response_model=list[LicitacaoRead])
def list_licitacoes(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    session: Session = Depends(get_session)
):
    licitacoes = session.exec(
        select(Licitacao).offset(offset).limit(limit)
    ).all()
    return licitacoes

@router.get("/qtd-licitacoes-por-orgao")
def qtd_licitacoes_por_orgao(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    orgao_nome: str = Query(None, description="Filtrar por nome do órgão"),
    orgao_id: int = Query(None, description="Filtrar por id do órgão"),
    session: Session = Depends(get_session)
):
    query = (
        select(Orgao.id, Orgao.descricao, func.count(Licitacao.id).label("num_licitacoes"))
        .join(Licitacao, Licitacao.orgao_id == Orgao.id)
        .group_by(Orgao.id)
        .order_by(func.count(Licitacao.id).desc())
    )
    if orgao_nome:
        query = query.where(Orgao.descricao.ilike(f"%{orgao_nome}%"))
    if orgao_id:
        query = query.where(Orgao.id == orgao_id)
    query = query.offset(offset).limit(limit)
    results = session.exec(query).all()
    return [{"orgao_id": id, "orgao": descricao, "num_licitacoes": num_licitacoes} for id, descricao, num_licitacoes in results]

@router.get("/com-licitacoes-municipio")
def orgaos_com_licitacoes_municipio(
    municipio_nome: str = Query(..., description="Nome do município"),
    orgao_nome: str = Query(None, description="Filtrar por nome do órgão"),
    orgao_id: int = Query(None, description="Filtrar por id do órgão"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session)
):
    query = (
        select(Orgao, Licitacao)
        .join(Licitacao, Licitacao.orgao_id == Orgao.id)
        .where(Licitacao.municipio.ilike(f"%{municipio_nome}%"))
    )
    if orgao_nome:
        query = query.where(Orgao.descricao.ilike(f"%{orgao_nome}%"))
    if orgao_id:
        query = query.where(Orgao.id == orgao_id)
    query = query.offset(offset).limit(limit)
    results = session.exec(query).all()
    return [
        {
            "orgao": orgao,
            "licitacao": licitacao
        } for orgao, licitacao in results
    ]

@router.get("/{licitacao_id}", response_model=LicitacaoRead)
def get_licitacao(licitacao_id: int, session: Session = Depends(get_session)):
    licitacao = session.get(Licitacao, licitacao_id)
    if not licitacao:
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    return licitacao

@router.put("/{licitacao_id}", response_model=LicitacaoRead)
def update_licitacao(licitacao_id: int, licitacao: LicitacaoCreate, session: Session = Depends(get_session)):
    db_licitacao = session.get(Licitacao, licitacao_id)
    if not db_licitacao:
        logger.warning(f"Tentativa de atualização de licitação inexistente: {licitacao_id}")
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    for key, value in licitacao.model_dump().items():
        setattr(db_licitacao, key, value)
    session.add(db_licitacao)
    session.commit()
    session.refresh(db_licitacao)
    logger.info(f"Licitação atualizada: {licitacao_id}")
    return db_licitacao

@router.delete("/{licitacao_id}")
def delete_licitacao(licitacao_id: int, session: Session = Depends(get_session)):
    licitacao = session.get(Licitacao, licitacao_id)
    if not licitacao:
        logger.warning(f"Tentativa de exclusão de licitação inexistente: {licitacao_id}")
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    session.delete(licitacao)
    session.commit()
    logger.info(f"Licitação excluída: {licitacao_id}")
    return {"ok": True}