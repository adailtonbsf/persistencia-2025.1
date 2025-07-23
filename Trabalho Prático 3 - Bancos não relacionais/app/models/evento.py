from datetime import datetime
from typing import List
from bson import ObjectId
from odmantic import Model, Reference
from app.models.local import Local

class Evento(Model):
    titulo: str
    descricao: str
    data_inicio: datetime
    data_fim: datetime
    local: Local = Reference()
    palestrantes: List[ObjectId]
    participantes: List[ObjectId]