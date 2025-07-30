from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy import func
from sqlmodel import Session, select

from app.database import get_session
from app.models.contrato import Contrato
from app.models.fornecedor import Fornecedor
from app.schemas.Fornecedor import FornecedorRead, FornecedorCreate
from app.utils.logger import logger

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

@router.post("/", response_model=FornecedorRead)
def create_fornecedor(fornecedor: FornecedorCreate, session: Session = Depends(get_session)):
    db_fornecedor = Fornecedor(**fornecedor.model_dump())
    session.add(db_fornecedor)
    session.commit()
    session.refresh(db_fornecedor)
    logger.info(f"Fornecedor criado: {db_fornecedor.id}")
    return db_fornecedor

@router.post("/popular")
async def popular_fornecedores(
    licitacoes_file: UploadFile = File(...),
    contratos_file: UploadFile = File(...),
    despesas_file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    import csv

    files_to_process = [
        (licitacoes_file, 'fornecedorCpfCnpj', 'fornecedorNome', 'fornecedorRazaoSocial'),
        (contratos_file, 'fornecedorCpfCnpj', 'fornecedorNome', 'fornecedorRazaoSocial'),
        (despesas_file, 'codigoFavorecido', 'nomeFavorecido', 'nomeFavorecido')
    ]

    processed_cnpjs = set()
    fornecedores_adicionados = 0

    for upload_file, cnpj_key, nome_key, razao_key in files_to_process:
        contents = await upload_file.read()
        lines = contents.decode('utf-8').splitlines()
        reader = csv.DictReader(lines)
        for row in reader:
            cpf_cnpj = row.get(cnpj_key, '').strip()
            if not cpf_cnpj or cpf_cnpj in processed_cnpjs:
                continue
            fornecedor = session.exec(select(Fornecedor).where(Fornecedor.cpf_cnpj == cpf_cnpj)).first()
            if not fornecedor:
                nome = row.get(nome_key, 'Não informado')
                fornecedor = Fornecedor(
                    cpf_cnpj=cpf_cnpj,
                    nome=nome.strip(),
                    razao_social=row.get(razao_key, '').strip() or nome.strip(),
                    tipo_pessoa='F' if len(cpf_cnpj) == 11 else 'J'
                )
                session.add(fornecedor)
                session.flush()
                fornecedores_adicionados += 1
            processed_cnpjs.add(cpf_cnpj)

    if fornecedores_adicionados > 0:
        session.commit()
    return {"fornecedores_processados": fornecedores_adicionados}

@router.get("/", response_model=list[FornecedorRead])
def list_fornecedores(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    session: Session = Depends(get_session)
):
    fornecedores = session.exec(
        select(Fornecedor).offset(offset).limit(limit)
    ).all()
    return fornecedores

@router.get("/maiores")
def maiores_fornecedores(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session)
):
    query = (
        select(Fornecedor, func.sum(Contrato.valor_inicial).label("valor_total"))
        .join(Contrato, Contrato.fornecedor_id == Fornecedor.id)
        .group_by(Fornecedor.id)
        .order_by(func.sum(Contrato.valor_inicial).desc())
        .offset(offset)
        .limit(limit)
    )
    results = session.exec(query).all()
    return [
        {
            "id": fornecedor.id,
            "cpf_cnpj": fornecedor.cpf_cnpj,
            "nome": fornecedor.nome,
            "razao_social": fornecedor.razao_social,
            "tipo_pessoa": fornecedor.tipo_pessoa,
            "valor_total_contratado": valor_total or 0.0
        }
        for fornecedor, valor_total in results
    ]

@router.get("/{fornecedor_id}", response_model=FornecedorRead)
def get_fornecedor(fornecedor_id: int, session: Session = Depends(get_session)):
    fornecedor = session.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return fornecedor

@router.put("/{fornecedor_id}", response_model=FornecedorRead)
def update_fornecedor(fornecedor_id: int, fornecedor: FornecedorCreate, session: Session = Depends(get_session)):
    db_fornecedor = session.get(Fornecedor, fornecedor_id)
    if not db_fornecedor:
        logger.warning(f"Fornecedor {fornecedor_id} não encontrado para atualização")
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    for key, value in fornecedor.model_dump().items():
        setattr(db_fornecedor, key, value)
    session.add(db_fornecedor)
    session.commit()
    session.refresh(db_fornecedor)
    logger.info(f"Fornecedor atualizado: {fornecedor_id}")
    return db_fornecedor

@router.delete("/{fornecedor_id}")
def delete_fornecedor(fornecedor_id: int, session: Session = Depends(get_session)):
    fornecedor = session.get(Fornecedor, fornecedor_id)
    if not fornecedor:
        logger.warning(f"Fornecedor {fornecedor_id} não encontrado para exclusão")
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    session.delete(fornecedor)
    session.commit()
    logger.info(f"Fornecedor excluído: {fornecedor_id}")
    return {"ok": True}