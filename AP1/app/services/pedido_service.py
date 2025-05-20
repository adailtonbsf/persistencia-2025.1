import os
import pandas as pd
from app.schemas.pedido_model import Pedido
from fastapi import HTTPException
from http import HTTPStatus
from app.utils import csv_utils
from app.utils.logger import get_logger
from app.services.cliente_service import carregar_dados_csv as carregar_clientes
from app.services.cardapio_service import carregar_dados_csv as carregar_cardapio

PEDIDO_FILE = "app/data/pedido.csv"
logger = get_logger("pedido")

def carregar_dados_csv() -> pd.DataFrame:
    os.makedirs(os.path.dirname(PEDIDO_FILE), exist_ok=True)
    
    if os.path.exists(PEDIDO_FILE) and os.path.getsize(PEDIDO_FILE) > 0:
        return pd.read_csv(PEDIDO_FILE, index_col=False)
    
    df_vazio = pd.DataFrame(columns=Pedido.model_fields.keys())
    df_vazio.to_csv(PEDIDO_FILE, index=False)
    return df_vazio

def criar_pedido(pedido_item: Pedido) -> dict:
    try:
        clientes = carregar_clientes()
        cardapio = carregar_cardapio()
        if clientes[clientes["id"] == pedido_item.cliente_id].empty:
            logger.error(f"ID {pedido_item.cliente_id} de cliente inválido")
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"ID {pedido_item.cliente_id} de cliente inválido")
        for id in pedido_item.itens:
            if cardapio[cardapio["id"] == id].empty:
                logger.error(f"Não foi possível encontrar o ID {id} no cardapio")
                raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Não foi possível encontrar o ID {id} no cardapio")

        pedidos = carregar_dados_csv()
        novo_id = 0
        if not pedidos.empty and "id" in pedidos.columns:
            novo_id = int(pedidos["id"].max()) + 1
        
        pedido_item.id = novo_id
        novo_df = pd.DataFrame([pedido_item.model_dump()])

        pedidos = pd.concat([pedidos, novo_df], ignore_index=True)
        novo_df.to_csv(PEDIDO_FILE, mode="a", index=False, header=False)

        logger.info("Pedido criado com sucesso")
        return {"id": pedido_item.id, "message": "Pedido criado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar pedido: {e}")
        raise RuntimeError(f"Erro ao criar pedido: {e}")
    
def listar_pedidos(**filtros) -> list[dict]:
    df = carregar_dados_csv()
    for campo, valor in filtros.items():
        if valor:
            if campo in df.columns:
                df = df[df[campo].astype(str).str.contains(str(valor), case=False, na=False)]
    return df.to_dict(orient="records")

def listar_pedido_id(pedido_id) -> dict:
    try:
        pedidos = carregar_dados_csv()
        pedido = pedidos[pedidos["id"] == pedido_id]
        if pedido.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pedido não encontrado")
        else:
            return pedido.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar pedido por ID: {e}")
        raise RuntimeError(f"Erro ao buscar pedido por ID: {e}")
    
def atualizar_pedido(pedido_id: int, dados_atualizados: Pedido) -> dict:
    try:
        pedidos = carregar_dados_csv()
        indice = pedidos[pedidos["id"] == pedido_id].index

        if indice.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pedido não encontrado")

        dados_dict = dados_atualizados.model_dump()
        dados_dict["id"] = pedido_id

        pedidos.loc[indice[0]] = dados_dict
        pedidos.to_csv(PEDIDO_FILE, index=False)
        logger.info(f"Pedido {pedido_id} atualizado com sucesso")
        return {"message": f"Pedido {pedido_id} atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar pedido: {e}")
        raise RuntimeError(f"Erro ao atualizar pedido: {e}")
    
def remover_pedido(pedido_id) -> dict:
    try:
        pedidos = carregar_dados_csv()
        if pedidos.size == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhum pedido cadastrado no banco")
        
        pedido = pedidos[pedidos["id"] == pedido_id]
        if pedido.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Pedido não encontrado")
        
        pedidos = pedidos.drop(pedidos[pedidos["id"] == pedido_id].index)
        pedidos.to_csv(PEDIDO_FILE, index=False)
        logger.info("Pedido removido com sucesso")
        return {"id": pedido_id, "message": "Pedido removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar o pedido: {e}")
        raise RuntimeError(f"Erro ao deletar o pedido: {e}")
    
def get_qtd_pedidos() -> dict:
    return csv_utils.get_quantidade_total(PEDIDO_FILE)

def get_pedido_zip() -> bytes:
    return csv_utils.csv_to_zip(PEDIDO_FILE)

def get_pedido_sha256() -> str:
    return csv_utils.get_sha256(PEDIDO_FILE)

def get_pedido_xml() -> str:
    return csv_utils.csv_to_xml(PEDIDO_FILE)