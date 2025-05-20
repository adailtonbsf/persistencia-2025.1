import os
import pandas as pd
from app.schemas.cliente_model import Cliente
from fastapi import HTTPException
from http import HTTPStatus
from app.utils.logger import get_logger
from app.utils import csv_utils

CLIENTE_FILE = "app/data/cliente.csv"
logger = get_logger("cliente")

def carregar_dados_csv() -> pd.DataFrame:
    os.makedirs(os.path.dirname(CLIENTE_FILE), exist_ok=True)
    
    if os.path.exists(CLIENTE_FILE) and os.path.getsize(CLIENTE_FILE) > 0:
        return pd.read_csv(CLIENTE_FILE, index_col=False)
    
    df_vazio = pd.DataFrame(columns=Cliente.model_fields.keys())
    df_vazio.to_csv(CLIENTE_FILE, index=False)
    return df_vazio

def criar_cliente(cliente_item: Cliente) -> dict:
    try:
        clientes = carregar_dados_csv()
        novo_id = 0
        if not clientes.empty and "id" in clientes.columns:
            novo_id = int(clientes["id"].max()) + 1
        
        cliente_item.id = novo_id
        novo_df = pd.DataFrame([cliente_item.model_dump()])

        clientes = pd.concat([clientes, novo_df], ignore_index=True)
        novo_df.to_csv(CLIENTE_FILE, mode="a", index=False, header=False)

        logger.info("Cliente criado com sucesso")
        return {"id": cliente_item.id, "message": "Cliente criado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao criar cliente: {e}")
        raise RuntimeError(f"Erro ao criar cliente: {e}")

def listar_clientes(**filtros) -> list[dict]:
    df = carregar_dados_csv()
    for campo, valor in filtros.items():
        if valor:
            if campo in df.columns:
                df = df[df[campo].astype(str).str.contains(str(valor), case=False, na=False)]
    return df.to_dict(orient="records")

def listar_cliente_id(cliente_id) -> dict:
    try:
        clientes = carregar_dados_csv()
        cliente = clientes[clientes["id"] == cliente_id]
        if cliente.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cliente não encontrado")
        else:
            return cliente.iloc[0].to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar cliente por ID: {e}")
        raise RuntimeError(f"Erro ao buscar cliente por ID: {e}")
    
def atualizar_cliente(cliente_id: int, dados_atualizados: Cliente) -> dict:
    try:
        clientes = carregar_dados_csv()
        indice = clientes[clientes["id"] == cliente_id].index

        if indice.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cliente não encontrado")

        dados_dict = dados_atualizados.model_dump()
        dados_dict["id"] = cliente_id

        clientes.loc[indice[0]] = dados_dict
        clientes.to_csv(CLIENTE_FILE, index=False)
        logger.info(f"Cliente {cliente_id} atualizado com sucesso")
        return {"message": f"Cliente {cliente_id} atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente: {e}")
        raise RuntimeError(f"Erro ao atualizar cliente: {e}")
    
def remover_cliente(cliente_id) -> dict:
    try:
        clientes = carregar_dados_csv()
        if clientes.size == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Nenhum cliente cadastrado no banco")
        
        cliente = clientes[clientes["id"] == cliente_id]
        if cliente.empty:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cliente não encontrado")
        
        clientes = clientes.drop(clientes[clientes["id"] == cliente_id].index)
        clientes.to_csv(CLIENTE_FILE, index=False)
        logger.info("Cliente removido com sucesso")
        return {"id": cliente_id, "message": "Cliente removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar o cliente: {e}")
        raise RuntimeError(f"Erro ao deletar o cliente: {e}")
    
def get_qtd_clientes() -> dict:
    return csv_utils.get_quantidade_total(CLIENTE_FILE)

def get_cliente_zip() -> bytes:
    return csv_utils.csv_to_zip(CLIENTE_FILE)

def get_cliente_sha256() -> str:
    return csv_utils.get_sha256(CLIENTE_FILE)

def get_cliente_xml() -> str:
    return csv_utils.csv_to_xml(CLIENTE_FILE)