from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class Fornecedor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cpf_cnpj: str = Field(index=True, unique=True)
    nome: str = Field(index=True)
    razao_social: Optional[str] = None
    tipo_pessoa: str # 'F' para Física, 'J' para Jurídica

    contratos: List["Contrato"] = Relationship(back_populates="fornecedor")