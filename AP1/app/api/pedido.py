from fastapi import APIRouter, Response
from typing import Optional, List, Literal
from datetime import datetime
from app.schemas.pedido_model import Pedido
from app.services.pedido_service import (
    criar_pedido,
    listar_pedidos, listar_pedido_id,
    atualizar_pedido,
    remover_pedido,
    get_qtd_pedidos, get_pedido_zip, get_pedido_sha256, get_pedido_xml
)

router = APIRouter(
    prefix="/pedido",
    tags=["pedido"]
)

@router.get("/", response_model=list[dict])
async def obter_pedidos(
    cliente_id: Optional[int] = None,
    itens: Optional[List[int]] = None,
    data_hora_pedido: Optional[datetime] = None,
    status: Optional[Literal["Em aberto", "Fechado"]] = None,
    forma_pagamento: Optional[Literal["Pix", "Cartão", "Dinheiro"]] = None
):
    return listar_pedidos(cliente_id=cliente_id, itens=itens, data_hora_pedido=data_hora_pedido, status=status, forma_pagamento=forma_pagamento)

@router.get("/count", response_model=dict)
async def quantidade_total_pedido():
    return get_qtd_pedidos()

@router.get("/get_zip", response_class=Response)
async def csv_to_zip():
    return Response(content=get_pedido_zip(), media_type="application/zip", headers={"Content-Disposition": "attachment; filename=pedido.zip"})

@router.get("/get_sha256", response_model=dict)
async def get_sha256():
    return {"hash_sha256": get_pedido_sha256()}

@router.get("/get_xml")
async def csv_to_xml():
    return Response(content=get_pedido_xml(), media_type="application/xml", headers={"Content-Disposition": "attachment; filename=pedido.xml"})

@router.get("/{pedido_id}", response_model=dict)
async def obter_pedido_id(pedido_id: int):
    return listar_pedido_id(pedido_id)

@router.post("/", response_model=dict)
async def adicionar_pedido(pedido: Pedido):
    return criar_pedido(pedido)

@router.put("/{pedido_id}", response_model=dict)
async def modificar_pedido(pedido_id: int, pedido: Pedido):
    return atualizar_pedido(pedido_id, pedido)

@router.delete("/{pedido_id}", response_model=dict)
async def deletar_pedido(pedido_id: int):
    return remover_pedido(pedido_id)