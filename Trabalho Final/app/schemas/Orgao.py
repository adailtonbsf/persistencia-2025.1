from pydantic import BaseModel
from app.schemas.Contrato import ContratoRead


class OrgaoRead(BaseModel):
    id: int
    codigo_siafi: str
    descricao: str

class OrgaoCreate(BaseModel):
    codigo_siafi: str
    descricao: str

class OrgaoComContratosRead(OrgaoRead):
    contratos: list[ContratoRead]