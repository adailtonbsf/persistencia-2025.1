from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

class StatusPedido(str, Enum):
    EM_ABERTO = "Em aberto"
    FECHADO = "Fechado"

class FormaPagamento(str, Enum):
    PIX = "Pix"
    DINHEIRO = "Dinheiro"
    CARTAO = "Cartão"

class ClienteBase(SQLModel):
    nome: str
    email: str = Field(unique=True, index=True)
    cpf: str = Field(unique=True, index=True)
    telefone: str
    data_cadastro: date = Field(default_factory=date.today)

class Cliente(ClienteBase, table=True):
    __tablename__ = 'clientes'

    id: Optional[int] = Field(default=None, primary_key=True)

    pedidos: List["Pedido"] = Relationship(back_populates="cliente")

class ClienteRead(ClienteBase):
    id: int

class ClienteCreate(ClienteBase):
    pass

class PedidoBase(SQLModel):
    status: StatusPedido = Field(default=StatusPedido.EM_ABERTO)
    observacao: Optional[str] = None
    forma_pagamento: Optional[FormaPagamento] = None
    data_pedido: datetime = Field(default_factory=datetime.now)
    cliente_id: int = Field(foreign_key="clientes.id")
    funcionario_id: int = Field(foreign_key="funcionarios.id")

class Pedido(PedidoBase, table=True):
    __tablename__ = 'pedidos'

    id: Optional[int] = Field(default=None, primary_key=True)

    cliente: Optional[Cliente] = Relationship(back_populates="pedidos")
    funcionario: Optional["Funcionario"] = Relationship(back_populates="pedidos")
    pedido_pratos: List["PedidoPrato"] = Relationship(back_populates="pedido")

class PedidoRead(PedidoBase):
    id: int

class PedidoCreate(PedidoBase):
    pass

class FuncionarioBase(SQLModel):
    nome: str
    email: str = Field(unique=True, index=True)
    cargo: str
    telefone: Optional[str] = Field(default=None, index=True)
    data_admissao: date = Field(default_factory=date.today)

class Funcionario(FuncionarioBase, table=True):
    __tablename__ = 'funcionarios'

    id: Optional[int] = Field(default=None, primary_key=True)

    pedidos: List[Pedido] = Relationship(back_populates="funcionario")

class FuncionarioRead(FuncionarioBase):
    id: int

class FuncionarioCreate(FuncionarioBase):
    pass

class PratoBase(SQLModel):
    nome: str
    descricao: Optional[str] = None
    preco: float
    categoria: str
    disponibilidade: bool = Field(default=True)

class Prato(PratoBase, table=True):
    __tablename__ = 'pratos'

    id: Optional[int] = Field(default=None, primary_key=True)

    pedidos_prato: List["PedidoPrato"] = Relationship(back_populates="prato")

class PratoRead(PratoBase):
    id: int

class PratoCreate(PratoBase):
    pass

class PedidoPratoBase(SQLModel):
    quantidade: int
    preco_unitario: float
    subtotal: float

    pedido_id: int = Field(foreign_key="pedidos.id")
    prato_id: int = Field(foreign_key="pratos.id")

class PedidoPrato(PedidoPratoBase, table=True):
    __tablename__ = 'pedido_pratos'

    id: Optional[int] = Field(default=None, primary_key=True)

    pedido: Optional[Pedido] = Relationship(back_populates="pedido_pratos")
    prato: Optional[Prato] = Relationship(back_populates="pedidos_prato")

class PedidoPratoRead(PedidoPratoBase):
    id: int

class PedidoPratoCreate(PedidoPratoBase):
    pass

class ClienteWithPedidosRead(SQLModel):
    id: int
    nome: str
    pedidos: List[PedidoRead] = []

    class Config:
        orm_mode = True

Cliente.model_rebuild()
Funcionario.model_rebuild()
Prato.model_rebuild()
Pedido.model_rebuild()
PedidoPrato.model_rebuild()