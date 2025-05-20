from pydantic import BaseModel
from typing import List, Literal, Optional
from datetime import datetime

class Pedido(BaseModel):
    id: int = None
    cliente_id: int
    itens: List[int]
    data_hora_pedido : datetime = datetime.now
    status: Literal["Em aberto", "Fechado"]
    forma_pagamento: Optional[Literal["Pix", "Cartão", "Dinheiro"]] = None