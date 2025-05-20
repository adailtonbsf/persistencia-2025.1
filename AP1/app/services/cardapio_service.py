import os
import pandas as pd
from app.schemas.cardapio_model import Cardapio
from fastapi import HTTPException
from http import HTTPStatus
from app.utils import csv_utils
from app.utils.logger import get_logger

CARDAPIO_FILE = "app/data/cardapio.csv"
logger = get_logger("cardapio")

def carregar_dados_csv() -> pd.DataFrame:
    os.makedirs(os.path.dirname(CARDAPIO_FILE), exist_ok=True)
    
    if os.path.exists(CARDAPIO_FILE) and os.path.getsize(CARDAPIO_FILE) > 0:
        return pd.read_csv(CARDAPIO_FILE, index_col=False)
    
    df_vazio = pd.DataFrame(columns=Cardapio.model_fields.keys())
    df_vazio.to_csv(CARDAPIO_FILE, index=False)
    return df_vazio

def criar_item_cardapio(cardapio_item: Cardapio) -> dict:
    try:
        cardapio = carregar_dados_csv()
        novo_id = 0
        if not cardapio.empty and "id" in cardapio.columns:
            novo_id = int(cardapio["id"].max()) + 1
        
        cardapio_item.id = novo_id
        novo_df = pd.DataFrame([cardapio_item.model_dump()])

        cardapio = pd.concat([cardapio, novo_df], ignore_index=True)
        novo_df.to_csv(CARDAPIO_FILE, mode="a", index=False, header=False)

        logger.info("Item do cardapio criado com sucesso")
        return {"id": cardapio_item.id, "message": "Item do cardapio criado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao criar item do cardapio: {e}")
        raise RuntimeError(f"Erro ao criar item do cardapio: {e}")

def listar_itens_cardapio(**filtros) -> list[dict]:
    df = carregar_dados_csv()
    for campo, valor in filtros.items():
        if valor:
            if campo in df.columns:
                df = df[df[campo].astype(str).str.contains(str(valor), case=False, na=False)]
    return df.to_dict(orient="records")

def listar_item_cardapio_id(cardapio_id) -> dict:
    try:
        cardapio = carregar_dados_csv()
        item_cardapio = cardapio[cardapio["id"] == cardapio_id]
        if item_cardapio.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item do cardapio não encontrado")
        else:
            return item_cardapio.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar item do cardapio por ID: {e}")
        raise RuntimeError(f"Erro ao buscar item do cardapio por ID: {e}")
    
def atualizar_item_cardapio(cardapio_id: int, dados_atualizados: Cardapio) -> dict:
    try:
        cardapio = carregar_dados_csv()
        indice = cardapio[cardapio["id"] == cardapio_id].index

        if indice.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item do cardapio não encontrado")

        dados_dict = dados_atualizados.model_dump()
        dados_dict["id"] = cardapio_id

        cardapio.loc[indice[0]] = dados_dict
        cardapio.to_csv(CARDAPIO_FILE, index=False)
        logger.info(f"Item {cardapio_id} do cardapio atualizado com sucesso")
        return {"message": f"Item {cardapio_id} do cardapio atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar item do cardapio: {e}")
        raise RuntimeError(f"Erro ao atualizar item do cardapio: {e}")
    
def remover_item_cardapio(cardapio_id) -> dict:
    try:
        cardapio = carregar_dados_csv()
        if cardapio.size == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhum item do cardapio cadastrado no banco")
        
        item_cardapio = cardapio[cardapio["id"] == cardapio_id]
        if item_cardapio.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item do cardapio não encontrado")
        
        cardapio = cardapio.drop(cardapio[cardapio["id"] == cardapio_id].index)
        cardapio.to_csv(CARDAPIO_FILE, index=False)
        logger.info("Item do cardapio removido com sucesso")
        return {"id": cardapio_id, "message": "Item do cardapio removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar o item do cardapio: {e}")
        raise RuntimeError(f"Erro ao deletar o item do cardapio: {e}")
    
def get_qtd_itens_cardapio() -> dict:
    return csv_utils.get_quantidade_total(CARDAPIO_FILE)

def get_cardapio_zip() -> bytes:
    return csv_utils.csv_to_zip(CARDAPIO_FILE)

def get_cardapio_sha256() -> str:
    return csv_utils.get_sha256(CARDAPIO_FILE)

def get_cardapio_xml() -> str:
    return csv_utils.csv_to_xml(CARDAPIO_FILE)