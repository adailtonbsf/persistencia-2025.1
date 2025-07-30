from fastapi import FastAPI
from app.api.despesas import router as despesa_router
from app.api.contratos import router as contrato_router
from app.api.contratos_detalhes import router as contrato_detalhe_router
from app.api.orgaos import router as orgao_router
from app.api.fornecedores import router as fornecedor_router
from app.api.licitacoes import router as licitacao_router

app = FastAPI()
app.include_router(despesa_router)
app.include_router(contrato_router)
app.include_router(contrato_detalhe_router)
app.include_router(orgao_router)
app.include_router(fornecedor_router)
app.include_router(licitacao_router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Gestão de Contratos e Despesas Públicas!"}