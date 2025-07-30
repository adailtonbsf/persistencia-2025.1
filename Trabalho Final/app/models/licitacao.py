from datetime import date
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Licitacao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero_processo: str = Field(index=True)
    objeto: str
    modalidade: str
    situacao: str
    valor_estimado: float
    data_abertura: date
    data_publicacao: date
    municipio: str
    uf: str

    orgao_id: int = Field(foreign_key="orgao.id")
    orgao: "Orgao" = Relationship(back_populates="licitacoes")