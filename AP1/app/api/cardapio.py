from fastapi import APIRouter, Response
from typing import Optional, Literal
from app.schemas.cardapio_model import Cardapio
from app.services.cardapio_service import (
    atualizar_item_cardapio,
    criar_item_cardapio,
    listar_item_cardapio_id, listar_itens_cardapio,
    remover_item_cardapio,
    get_qtd_itens_cardapio, get_cardapio_zip, get_cardapio_sha256, get_cardapio_xml
)

router = APIRouter(
    prefix="/cardapio",
    tags=["Cardapio"]
)

@router.get("/", response_model=list[dict])
async def obter_itens_cardapio(
    nome: Optional[str] = None, 
    descricao: Optional[str] = None, 
    preco: Optional[float] = None, 
    categoria: Optional[Literal["Entrada", "Principal", "Sobremesa", "Bebida", "Acompanhamento", "Outro"]] = None, 
    disponivel: Optional[bool] = None):
    return listar_itens_cardapio(nome=nome, descricao=descricao, preco=preco, categoria=categoria, disponivel=disponivel)

@router.get("/count", response_model=dict)
async def quantidade_total_cardapio():
    return get_qtd_itens_cardapio()

@router.get("/get_zip", response_class=Response)
async def csv_to_zip():
    return Response(content=get_cardapio_zip(), media_type="application/zip", headers={"Content-Disposition": "attachment; filename=cardapio.zip"})

@router.get("/get_sha256", response_model=dict)
async def get_sha256():
    return {"hash_sha256": get_cardapio_sha256()}

@router.get("/get_xml")
async def csv_to_xml():
    return Response(content=get_cardapio_xml(), media_type="application/xml", headers={"Content-Disposition": "attachment; filename=cardapio.xml"})

@router.get("/{cardapio_id}", response_model=dict)
async def obter_item_cardapio_id(cardapio_id: int):
    return listar_item_cardapio_id(cardapio_id)

@router.post("/", response_model=dict)
async def adicionar_item_cardapio(cardapio: Cardapio):
    return criar_item_cardapio(cardapio)

@router.put("/{cardapio_id}", response_model=dict)
async def modificar_item_cardapio(cardapio_id: int, cardapio: Cardapio):
    return atualizar_item_cardapio(cardapio_id, cardapio)

@router.delete("/{cardapio_id}", response_model=dict)
async def deletar_item_cardapio(cardapio_id: int):
    return remover_item_cardapio(cardapio_id)