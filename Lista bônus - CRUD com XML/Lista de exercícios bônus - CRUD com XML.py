from typing import Union
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from http import HTTPStatus
import xml.etree.ElementTree as ET
import os

app = FastAPI()
XML_FILE = "database.xml"

class Produto(BaseModel):
    id: int
    nome: str
    preco: float
    qtd: int
    
def ler_dados_xml():
    produtos = []
    if os.path.exists(XML_FILE):
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        for elem in root.findall("produto"):
            id = int(elem.find("id").text)
            nome = elem.find("nome").text
            preco = float(elem.find("preco").text)
            qtd = int(elem.find("qtd").text)
            produtos.append(Produto(id=id, nome=nome, preco=preco, qtd=qtd))
    return produtos

def escrever_dados_xml(produtos):
    root = ET.Element("produtos")
    for produto in produtos:
        produto_elem = ET.SubElement(root, "produto")
        ET.SubElement(produto_elem, "id").text = str(produto.id)
        ET.SubElement(produto_elem, "nome").text = produto.nome
        ET.SubElement(produto_elem, "preco").text = str(produto.preco)
        ET.SubElement(produto_elem, "qtd").text = str(produto.qtd)
    tree = ET.ElementTree(root)
    tree.write(XML_FILE)
            
@app.get("/produtos", response_model=List[Produto])
def listar_produtos():
    return ler_dados_xml()

@app.get("/produtos/{produto_id}", response_model=Produto)
def obter_produto(produto_id: int):
    produtos = listar_produtos()
    for produto in produtos:
        if produto.id == produto_id:
            return produto
    raise HTTPException(status_code=404, 
                        detail="Produto não encontrado")
    
@app.post("/produtos", response_model=Produto)
def criar_produto(produto: Produto):
    produtos = listar_produtos()
    if any(p.id == produto.id for p in produtos):
        raise HTTPException(status_code=400, detail="Id já existe")
    produtos.append(produto)
    escrever_dados_xml(produtos)
    return produto

@app.put("/produtos/{produto_id}", response_model=Produto)
def atualizar_produto(produto_id: int, produto_atualizado: Produto):
    produtos = listar_produtos()
    for i, produto in enumerate(produtos):
        if produto.id == produto_id:
            produtos[i] = produto_atualizado
            escrever_dados_xml(produtos)
            return produto_atualizado
    raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.delete("/produtos/{produto_id}", response_model=dict)
def deletar_produto(produto_id: int):
    produtos = listar_produtos()
    produtos_filtrados = [produto for produto in produtos 
                          if produto.id != produto_id]
    if len(produtos) == len(produtos_filtrados):
        raise HTTPException(status_code=404, 
                            detail="Produto não encontrado")
    escrever_dados_xml(produtos_filtrados)
    return {"mensagem": "Produto deletado com sucesso"}
    
