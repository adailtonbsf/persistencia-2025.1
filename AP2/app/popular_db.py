# app/scripts/popular_banco.py
# python -m app.popular_db

from sqlmodel import Session
from app.models import Cliente, Funcionario, Prato, Pedido, PedidoPrato, StatusPedido, FormaPagamento
from app.database import engine
from datetime import date, datetime
import random
from app.utils.logger import get_logger

logger_cliente = get_logger("cliente")
logger_funcionario = get_logger("funcionario")
logger_prato = get_logger("prato")
logger_pedido = get_logger("pedido")
logger_pedido_prato = get_logger("pedido_prato")

def popular_banco():
    with Session(engine) as session:
        # Clientes
        clientes = [
            Cliente(nome=f"Cliente {i}", email=f"cliente{i}@exemplo.com", cpf=f"0000000000{i}", telefone=f"1199999000{i}")
            for i in range(1, 11)
        ]
        session.add_all(clientes)
        session.commit()
        for c in clientes:
            logger_cliente.info(f"Cliente inserido: {c.nome} ({c.email})")

        # Funcionários
        funcionarios = [
            Funcionario(nome=f"Funcionario {i}", email=f"func{i}@empresa.com", cargo="Atendente", data_admissao=date(2023, 1, i))
            for i in range(1, 11)
        ]
        session.add_all(funcionarios)
        session.commit()
        for f in funcionarios:
            logger_funcionario.info(f"Funcionário inserido: {f.nome} ({f.email})")

        # Pratos
        pratos = [
            Prato(nome=f"Prato {i}", descricao=f"Descrição do prato {i}", preco=10.0 + i, categoria="Categoria A", disponibilidade=True)
            for i in range(1, 11)
        ]
        session.add_all(pratos)
        session.commit()
        for p in pratos:
            logger_prato.info(f"Prato inserido: {p.nome} (R$ {p.preco})")

        # Pedidos
        pedidos = [
            Pedido(
                status=random.choice(list(StatusPedido)),
                observacao=f"Observação {i}",
                forma_pagamento=random.choice(list(FormaPagamento)),
                data_pedido=datetime.now(),
                cliente_id=clientes[i % 10].id,
                funcionario_id=funcionarios[i % 10].id
            )
            for i in range(10)
        ]
        session.add_all(pedidos)
        session.commit()
        for p in pedidos:
            logger_pedido.info(f"Pedido inserido: ID {p.id} (Cliente ID: {p.cliente_id}, Funcionário ID: {p.funcionario_id})")

        # PedidoPrato
        pedido_pratos = [
            PedidoPrato(
                quantidade=random.randint(1, 5),
                preco_unitario=pratos[i % 10].preco,
                subtotal=pratos[i % 10].preco * random.randint(1, 5),
                pedido_id=pedidos[i % 10].id,
                prato_id=pratos[i % 10].id
            )
            for i in range(10)
        ]
        session.add_all(pedido_pratos)
        session.commit()
        for pp in pedido_pratos:
            logger_pedido_prato.info(f"PedidoPrato inserido: ID {pp.id} (Pedido ID: {pp.pedido_id}, Prato ID: {pp.prato_id})")

        print("Banco populado com sucesso!")

if __name__ == "__main__":
    popular_banco()