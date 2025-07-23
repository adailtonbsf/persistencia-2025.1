from typing import Optional
from odmantic import Model

class Palestrante(Model):
    nome: str
    bio: str
    email: str
    empresa: str
    linkedin_url: Optional[str] = None