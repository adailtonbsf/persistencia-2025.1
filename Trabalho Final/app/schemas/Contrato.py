from pydantic import BaseModel
from typing import Optional
from datetime import date

class ContratoDetalheRead(BaseModel):
    id: int
    modalidade_licitacao_origem: str
    numero_licitacao_origem: str
    contrato_id: int

class ContratoDetalheCreate(BaseModel):
    modalidade_licitacao_origem: str
    numero_licitacao_origem: str
    contrato_id: int

class ContratoRead(BaseModel):
    id: int
    numero: str
    objeto: str
    fundamento_legal: str
    valor_inicial: float
    data_assinatura: Optional[date]
    data_inicio_vigencia: Optional[date]
    data_fim_vigencia: Optional[date]
    orgao_id: int
    fornecedor_id: int
    detalhes: Optional[ContratoDetalheRead]

class ContratoCreate(BaseModel):
    numero: str
    objeto: str
    fundamento_legal: str
    valor_inicial: float
    data_assinatura: Optional[date]
    data_inicio_vigencia: Optional[date]
    data_fim_vigencia: Optional[date]
    orgao_id: int
    fornecedor_id: int