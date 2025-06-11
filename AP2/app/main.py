from contextlib import asynccontextmanager
from datetime import date
from typing import List
from fastapi import FastAPI, Depends, Query
from sqlmodel import SQLModel, desc, func
from app.database import engine, get_session
from app.models import Cliente, Prato, PedidoPrato, Pedido, ClienteWithPedidosRead, Funcionario
from app.api import (
    cliente as cliente_router,
    pedido as pedido_router,
    funcionario as funcionario_router,
    pedido_prato as pedido_prato_router,
    prato as prato_router
)

@asynccontextmanager
async def lifespan(_):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/top-clientes", response_model=List[ClienteWithPedidosRead])
async def top_clientes(
    session=Depends(get_session),
    limit: int = Query(10, ge=1, le=100)
):
    results = (
        session.query(Cliente)
        .join(Cliente.pedidos)
        .group_by(Cliente.id)
        .order_by(func.count().desc())
        .limit(limit)
        .all()
    )

    return results

@app.get("/faturamento", response_model=dict)
async def faturamento(
    data_inicio: date,
    data_fim: date,
    session=Depends(get_session)
):
    total = (
        session.query(func.sum(PedidoPrato.subtotal))
        .join(Pedido)
        .filter(Pedido.data_pedido >= data_inicio)
        .filter(Pedido.data_pedido <= data_fim)
        .scalar()
    )
    return {"faturamento": total or 0}

@app.get("/pratos-mais-vendidos", response_model=List[dict])
async def pratos_mais_vendidos(
    session=Depends(get_session),
    limit: int = Query(5, ge=1, le=100)
):
    results = (
        session.query(Prato.nome, func.sum(PedidoPrato.quantidade).label("total_vendido"))
        .join(PedidoPrato)
        .group_by(Prato.id)
        .order_by(func.sum(PedidoPrato.quantidade).desc())
        .limit(limit)
        .all()
    )
    return [{"prato": nome, "total_vendido": total} for nome, total in results]

@app.get("/pedidos-detalhados", response_model=List[dict])
async def pedidos_detalhados(
    data_inicio: date,
    data_fim: date,
    session=Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    id: int = Query(None)
):
    query = (
        session.query(
            Pedido.id,
            Pedido.data_pedido,
            Cliente.nome,
            Funcionario.nome
        )
        .join(Cliente, Pedido.cliente_id == Cliente.id)
        .join(Funcionario, Pedido.funcionario_id == Funcionario.id)
        .filter(Pedido.data_pedido >= data_inicio)
        .filter(Pedido.data_pedido <= data_fim)
    )
    if id is not None:
        query = query.filter(Pedido.id == id)
    results = (
        query
        .order_by(desc(Pedido.data_pedido))
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "pedido_id": pid,
            "data_pedido": data,
            "cliente": cliente,
            "funcionario": funcionario
        }
        for pid, data, cliente, funcionario in results
    ]

app.include_router(cliente_router.router)
app.include_router(pedido_router.router)
app.include_router(funcionario_router.router)
app.include_router(pedido_prato_router.router)
app.include_router(prato_router.router)