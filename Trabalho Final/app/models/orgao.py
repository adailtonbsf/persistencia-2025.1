from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel

class Orgao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    codigo_siafi: str = Field(index=True, unique=True)
    descricao: str

    licitacoes: List["Licitacao"] = Relationship(back_populates="orgao")
    contratos: List["Contrato"] = Relationship(back_populates="orgao")