from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel
from datetime import date

class Contrato(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str = Field(index=True)
    objeto: str
    fundamento_legal: str
    valor_inicial: float
    data_assinatura: Optional[date] = Field(default=None)
    data_inicio_vigencia: Optional[date] = Field(default=None)
    data_fim_vigencia: Optional[date] = Field(default=None)

    orgao_id: int = Field(foreign_key="orgao.id")
    orgao: "Orgao" = Relationship(back_populates="contratos")

    fornecedor_id: int = Field(foreign_key="fornecedor.id")
    fornecedor: "Fornecedor" = Relationship(back_populates="contratos")

    detalhes: Optional["ContratoDetalhe"] = Relationship(back_populates="contrato")


class ContratoDetalhe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    modalidade_licitacao_origem: str
    numero_licitacao_origem: str

    contrato_id: int = Field(foreign_key="contrato.id", unique=True)
    contrato: "Contrato" = Relationship(back_populates="detalhes")