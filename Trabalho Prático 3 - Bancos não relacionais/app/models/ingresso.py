from datetime import datetime
from odmantic import Model, Reference, ObjectId
from pydantic import BaseModel

from app.models.evento import Evento
from app.models.participante import Participante

class IngressoCreate(BaseModel):
    tipo: str
    preco: float
    evento: ObjectId
    participante: ObjectId

class Ingresso(Model):
    tipo: str  # Ex: "Padrão", "VIP", "Estudante"
    preco: float
    data_compra: datetime
    evento: Evento = Reference()
    participante: Participante = Reference()