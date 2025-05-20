from pydantic import BaseModel
from datetime import date

class Cliente(BaseModel):
    id: int = None
    nome: str
    email: str
    telefone: str
    data_nascimento: date
    cpf: str