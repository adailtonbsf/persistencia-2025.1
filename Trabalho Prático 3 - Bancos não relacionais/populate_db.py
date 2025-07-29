import asyncio
from datetime import datetime, timedelta
from odmantic import ObjectId

from app.config.database import engine
from app.models.local import Local
from app.models.palestrante import Palestrante
from app.models.participante import Participante
from app.models.evento import Evento
from app.models.ingresso import Ingresso

async def main():
    # Popula Locais
    locais = [
        Local(
            nome=f"Local {i}",
            endereco=f"Rua {i}, Bairro {i}",
            cidade="Cidade X",
            capacidade=100 + i * 10,
            recursos=["Wi-Fi", "Projetor"]
        ) for i in range(10)
    ]
    await engine.save_all(locais)

    # Popula Palestrantes
    palestrantes = [
        Palestrante(
            nome=f"Palestrante {i}",
            bio=f"Bio do palestrante {i}",
            email=f"palestrante{i}@exemplo.com",
            empresa=f"Empresa {i}",
            linkedin_url=f"https://linkedin.com/in/palestrante{i}"
        ) for i in range(10)
    ]
    await engine.save_all(palestrantes)

    # Popula Participantes
    participantes = [
        Participante(
            nome=f"Participante {i}",
            email=f"participante{i}@exemplo.com",
            cpf=f"000.000.000-0{i}",
            data_nascimento=datetime(1990, 1, i+1),
            data_cadastro=datetime.now() - timedelta(days=i)
        ) for i in range(10)
    ]
    await engine.save_all(participantes)

    # Popula Eventos
    eventos = []
    for i in range(10):
        evento = Evento(
            titulo=f"Evento {i}",
            descricao=f"Descrição do evento {i}",
            data_inicio=datetime.now() + timedelta(days=i),
            data_fim=datetime.now() + timedelta(days=i, hours=4),
            local=locais[i],
            palestrantes=[ObjectId(str(p.id)) for p in palestrantes[:3]],
            participantes=[ObjectId(str(p.id)) for p in participantes[:5]]
        )
        eventos.append(evento)
    await engine.save_all(eventos)

    # Popula Ingressos
    ingressos = []
    for i in range(10):
        ingresso = Ingresso(
            tipo="Padrão" if i % 2 == 0 else "VIP",
            preco=100.0 + i * 10,
            data_compra=datetime.now() - timedelta(days=i),
            evento=eventos[i],
            participante=participantes[i]
        )
        ingressos.append(ingresso)
    await engine.save_all(ingressos)

    print("Banco populado com sucesso!")

if __name__ == "__main__":
    asyncio.run(main())