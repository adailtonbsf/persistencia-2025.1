from fastapi import FastAPI, HTTPException
from http import HTTPStatus
from pydantic import BaseModel
import xml.etree.ElementTree as ET
import os

XML_FILE = "livros.xml"

app = FastAPI()

class Livro(BaseModel):
    id: int
    titulo: str
    autor: str
    ano: int
    genero: str

def carregar_livros():
    livros = []
    if os.path.exists(XML_FILE):
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        for elem in root.findall("livro"):
            livro = Livro(
                id = int(elem.find("id").text),
                titulo = elem.find("titulo").text,
                autor = elem.find("autor").text,
                ano = int(elem.find("ano").text),
                genero = elem.find("genero").text
            )
            livros.append(livro)
    return livros

def salvar_livros(livros):
    root = ET.Element("livros")
    for livro in livros:
        livro_elem = ET.SubElement(root, "livro")
        ET.SubElement(livro_elem, "id").text = str(livro.id)
        ET.SubElement(livro_elem, "titulo").text = livro.titulo
        ET.SubElement(livro_elem, "autor").text = livro.autor
        ET.SubElement(livro_elem, "ano").text = str(livro.ano)
        ET.SubElement(livro_elem, "genero").text = livro.genero
    tree = ET.ElementTree(root)
    tree.write(XML_FILE)

db_livros = carregar_livros()

@app.get("/")
async def read_root():
    return {"msg": "Hello World"}

@app.get("/livros", response_model=list[Livro])
async def get_livros():
    return db_livros

@app.get("/livros/{livro_id}", response_model=Livro)
async def get_livro(livro_id: int):
    for livro in db_livros:
        if livro.id == livro_id:
            return livro
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Livro não encontrado")

@app.post("/livros", response_model=Livro)
async def criar_livro(livro: Livro):
    if any(l.id == livro.id for l in db_livros):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="ID já existente")
    db_livros.append(livro)
    salvar_livros(db_livros)
    return livro

@app.put("/livros/{livro_id}", response_model=Livro)
async def atualizar_livro(livro_id: int, livro_atualizado: Livro):
    for i, livro in enumerate(db_livros):
        if livro.id == livro_id:
            db_livros[i] = livro_atualizado
            salvar_livros(db_livros)
            return livro_atualizado
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Livro não encontrado")

@app.delete("/livros/{livro_id}", response_model=dict)
async def deletar_livro(livro_id: int):
    global db_livros
    livros_filtrados = [livro for livro in db_livros if livro.id != livro_id]
    if len(livros_filtrados) == len(db_livros):
        raise HTTPException(HTTPStatus.NOT_FOUND, detail="Livro não encontrado")
    db_livros = livros_filtrados
    salvar_livros(db_livros)
    return {"msg": "Livro deletado com sucesso"}
    