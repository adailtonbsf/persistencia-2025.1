from pydantic import BaseModel
from typing import Optional
from datetime import date

class DespesaRead(BaseModel):
    id: int
    documento_resumido: str
    numero_processo: Optional[str]
    fase: str
    especie: str
    favorecido_nome: str
    valor: float
    data_emissao: Optional[date]

class DespesaCreate(BaseModel):
    documento_resumido: str
    numero_processo: Optional[str]
    fase: str
    especie: str
    favorecido_nome: str
    valor: float
    data_emissao: Optional[date]