from datetime import date
from pydantic import BaseModel

class LicitacaoRead(BaseModel):
    id: int
    numero_processo: str
    objeto: str
    modalidade: str
    situacao: str
    valor_estimado: float
    data_abertura: date
    data_publicacao: date
    municipio: str
    uf: str
    orgao_id: int

class LicitacaoCreate(BaseModel):
    numero_processo: str
    objeto: str
    modalidade: str
    situacao: str
    valor_estimado: float
    data_abertura: date
    data_publicacao: date
    municipio: str
    uf: str
    orgao_id: int