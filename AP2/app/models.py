from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float

Base = declarative_base()

class Cliente(Base):
    __tablename__ = 'clientes'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    cpf = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=False)
    data_cadastro = Column(DateTime, nullable=False)

    pedidos = relationship("Pedido", back_populates="cliente")

class Pedido(Base):
    __tablename__ = 'pedidos'

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    funcionario_id = Column(Integer, ForeignKey('funcionarios.id'), nullable=False)
    status = Column(String, nullable=False)
    observacao = Column(String, nullable=True)
    forma_pagamento = Column(String, nullable=True)
    data_pedido = Column(DateTime, nullable=False)

    cliente = relationship("Cliente", back_populates="pedidos")
    funcionario = relationship("Funcionario", back_populates="pedidos")
    pedido_pratos = relationship("PedidoPrato", back_populates="pedido")

class Funcionario(Base):
    __tablename__ = 'funcionarios'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    cargo = Column(String, nullable=False)
    data_admissao = Column(DateTime, nullable=False)

    pedidos = relationship("Pedido", back_populates="funcionario")

class Prato(Base):
    __tablename__ = 'pratos'

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    preco = Column(Integer, nullable=False)
    categoria = Column(String, nullable=False)
    disponibilidade = Column(Boolean, nullable=False)

    pedidos = relationship("PedidoPrato", back_populates="prato")

class PedidoPrato(Base):
    __tablename__ = 'pedido_pratos'

    id = Column(Integer, primary_key=True)
    pedido_id = Column(Integer, ForeignKey('pedidos.id'), nullable=False)
    prato_id = Column(Integer, ForeignKey('pratos.id'), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="pedido_pratos")
    prato = relationship("Prato", back_populates="pedidos")