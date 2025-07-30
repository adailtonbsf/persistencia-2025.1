from pydantic import BaseModel
from typing import Optional

class FornecedorRead(BaseModel):
    id: int
    cpf_cnpj: str
    nome: str
    razao_social: Optional[str]
    tipo_pessoa: str

class FornecedorCreate(BaseModel):
    cpf_cnpj: str
    nome: str
    razao_social: Optional[str]
    tipo_pessoa: str