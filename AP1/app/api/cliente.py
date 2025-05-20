from fastapi import APIRouter, Response
from typing import Optional
from datetime import date
from app.schemas.cliente_model import Cliente
from app.services.cliente_service import (
    criar_cliente,
    listar_clientes, listar_cliente_id,
    atualizar_cliente,
    remover_cliente,
    get_qtd_clientes, get_cliente_zip, get_cliente_sha256, get_cliente_xml
)

router = APIRouter(
    prefix="/cliente",
    tags=["Cliente"]
)

@router.get("/", response_model=list[dict])
async def obter_clientes(
    nome: Optional[str] = None,
    email: Optional[str] = None,
    telefone: Optional[str] = None,
    data_nascimento: Optional[date] = None,
    cpf: Optional[str] = None
):
    return listar_clientes(nome=nome, email=email, telefone=telefone, data_nascimento=data_nascimento, cpf=cpf)

@router.get("/count", response_model=dict)
async def quantidade_total_cliente():
    return get_qtd_clientes()

@router.get("/get_zip", response_class=Response)
async def csv_to_zip():
    return Response(content=get_cliente_zip(), media_type="application/zip", headers={"Content-Disposition": "attachment; filename=cliente.zip"})

@router.get("/get_sha256", response_model=dict)
async def get_sha256():
    return {"hash_sha256": get_cliente_sha256()}

@router.get("/get_xml")
async def csv_to_xml():
    return Response(content=get_cliente_xml(), media_type="application/xml", headers={"Content-Disposition": "attachment; filename=cliente.xml"})

@router.get("/{cliente_id}", response_model=dict)
async def obter_cliente_id(cliente_id: int):
    return listar_cliente_id(cliente_id)

@router.post("/", response_model=dict)
async def adicionar_cliente(cliente: Cliente):
    return criar_cliente(cliente)

@router.put("/{cliente_id}", response_model=dict)
async def modificar_cliente(cliente_id: int, cliente: Cliente):
    return atualizar_cliente(cliente_id, cliente)

@router.delete("/{cliente_id}", response_model=dict)
async def deletar_cliente(cliente_id: int):
    return remover_cliente(cliente_id)