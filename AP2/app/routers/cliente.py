from ..models import Cliente
from fastapi import APIRouter, Depends, HTTPException
from ..database import get_session

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)

@router.post("/", response_model=Cliente)
async def criar_cliente(cliente: Cliente, session: Depends(get_session)) -> Cliente:
    session.add(cliente)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    session.refresh(cliente)
    return cliente