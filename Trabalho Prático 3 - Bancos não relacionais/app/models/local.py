from typing import List
from odmantic import Model

class Local(Model):
    nome: str
    endereco: str
    cidade: str
    capacidade: int
    recursos: List[str]  # (ex: "Projetor", "Wi-Fi", "Estacionamento")