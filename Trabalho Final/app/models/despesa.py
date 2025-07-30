from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Despesa(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    documento_resumido: str = Field(index=True)
    numero_processo: Optional[str] = Field(default=None, index=True)
    fase: str  # Ex: Empenho, Liquidação, Pagamento
    especie: str
    favorecido_nome: str
    valor: float
    data_emissao: Optional[date] = Field(default=None)