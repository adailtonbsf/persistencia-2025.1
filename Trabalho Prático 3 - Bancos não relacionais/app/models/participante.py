from datetime import datetime
from odmantic import Model

class Participante(Model):
    nome: str
    email: str
    cpf: str
    data_nascimento: datetime
    data_cadastro: datetime