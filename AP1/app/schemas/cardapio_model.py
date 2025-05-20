from pydantic import BaseModel
from typing import Literal

class Cardapio(BaseModel):
    id: int = None
    nome: str
    descricao: str
    preco: float
    categoria: Literal["Entrada", "Principal", "Sobremesa", "Bebida", "Acompanhamento", "Outro"]
    disponivel: bool