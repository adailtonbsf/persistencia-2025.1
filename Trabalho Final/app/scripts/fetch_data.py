import re
import httpx
import asyncio
import csv
import os
import datetime
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.portaldatransparencia.gov.br/api-de-dados"
HEADERS = {"chave-api-dados": API_KEY}

def get_sleep_time(endpoint: str) -> float:
    restritos = [
        "despesas/documentos-por-favorecido",
        "bolsa-familia-disponivel-por-cpf-ou-nis",
        "bolsa-familia-por-municipio",
        "bolsa-familia-sacado-por-nis",
        "auxilio-emergencial-beneficiario-por-municipio",
        "auxilio-emergencial-por-cpf-ou-nis",
        "auxilio-emergencial-por-municipio",
        "seguro-defeso-codigo"
    ]
    now = datetime.datetime.now()
    if any(endpoint.endswith(r) for r in restritos):
        return 60 / 180
    elif 0 <= now.hour < 6:
        return 60 / 700
    else:
        return 60 / 400

def get_orgao_siafi_codes(csv_path: str) -> List[str]:
    codes = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if "CODIGO INVALIDO" not in row["descricao"]:
                codes.append(row["codigo"])
    return codes

async def fetch_paginated_data(endpoint: str, params: Dict[str, Any]) -> List:
    all_data = []
    page = 1
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            params["pagina"] = page
            try:
                response = await client.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params)
                response.raise_for_status()
                data = response.json()
                if not data:
                    break
                all_data.extend(data)
                print(f"Página {page} do endpoint '{endpoint}' carregada com {len(data)} registros.")
                page += 1
                await asyncio.sleep(get_sleep_time(endpoint))
            except httpx.HTTPStatusError as e:
                print(f"Erro ao buscar dados para {endpoint} na página {page}: {e}")
                break
            except Exception as e:
                print(f"Ocorreu um erro inesperado: {e}")
                break
    return all_data

async def fetch_licitacoes(orgaos_siafi: list[str], start_date: str = "01/01/2024", end_date: str = "31/01/2024"):
    all_licitacoes = []
    for codigo in orgaos_siafi:
        params = {
            "dataInicial": start_date,
            "dataFinal": end_date,
            "codigoOrgao": codigo
        }
        licitacoes = await fetch_paginated_data("licitacoes", params)
        print(f"Órgão {codigo}: {len(licitacoes)} licitações encontradas.")
        all_licitacoes.extend(licitacoes)

    if all_licitacoes:
        def sanitize(date_str):
            return re.sub(r"\D", "", date_str)

        os.makedirs("data", exist_ok=True)
        filename = os.path.join("data", f"licitacoes_{sanitize(start_date)}_{sanitize(end_date)}.csv")
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_licitacoes[0].keys())
            writer.writeheader()
            writer.writerows(all_licitacoes)
        print(f"Arquivo {filename} salvo com sucesso com {len(all_licitacoes)} registros.")
    else:
        print("Nenhum dado para salvar.")

async def fetch_contratos(orgaos_siafi: list[str], start_date: str = "01/01/2024", end_date: str = "31/12/2024"):
    all_contratos = []
    for codigo in orgaos_siafi:
        params = {
            "dataInicial": start_date,
            "dataFinal": end_date,
            "codigoOrgao": codigo
        }
        contratos = await fetch_paginated_data("contratos", params)
        print(f"Órgão {codigo}: {len(contratos)} contratos encontrados.")
        all_contratos.extend(contratos)

    if all_contratos:
        def sanitize(date_str):
            return re.sub(r"\D", "", date_str)

        os.makedirs("data", exist_ok=True)
        filename = os.path.join("data", f"contratos_{sanitize(start_date)}_{sanitize(end_date)}.csv")
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=all_contratos[0].keys())
            writer.writeheader()
            writer.writerows(all_contratos)
        print(f"Arquivo {filename} salvo com sucesso com {len(all_contratos)} registros.")
    else:
        print("Nenhum dado para salvar.")

async def fetch_despesas_documentos(orgaos_siafi: list[str], start_date: str = "01/01/2024", end_date: str = "31/01/2024"):
    start = datetime.datetime.strptime(start_date, "%d/%m/%Y")
    end = datetime.datetime.strptime(end_date, "%d/%m/%Y")
    delta = datetime.timedelta(days=1)
    tipos_consulta = ["unidadeGestora", "gestao"]
    fases = [1, 2, 3]

    os.makedirs("data", exist_ok=True)
    filename = os.path.join("data", "despesas_documentos.csv")
    first_write = not os.path.exists(filename)

    while start <= end:
        data_emissao = start.strftime("%d/%m/%Y")
        all_docs_dia = []
        for codigo in orgaos_siafi:
            for tipo in tipos_consulta:
                for fase in fases:
                    params = {
                        "dataEmissao": data_emissao,
                        tipo: codigo,
                        "fase": fase
                    }
                    docs = await fetch_paginated_data("despesas/documentos", params)
                    print(f"{tipo} {codigo} em {data_emissao} fase {fase}: {len(docs)} documentos encontrados.")
                    all_docs_dia.extend(docs)
        if all_docs_dia:
            with open(filename, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=all_docs_dia[0].keys())
                if first_write:
                    writer.writeheader()
                    first_write = False
                writer.writerows(all_docs_dia)
            print(f"{len(all_docs_dia)} registros adicionados ao arquivo {filename}.")
        else:
            print(f"Nenhum dado para salvar em {data_emissao}.")
        start += delta


async def main():
    orgaos_siafi = get_orgao_siafi_codes("data/orgaos_siafi.csv")
    await fetch_despesas_documentos(orgaos_siafi, "28/01/2024", "31/12/2024")


if __name__ == "__main__":
    asyncio.run(main())