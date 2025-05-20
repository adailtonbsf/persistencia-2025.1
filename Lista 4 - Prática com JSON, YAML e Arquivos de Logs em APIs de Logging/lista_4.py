import yaml
import logging
import json

def configurar_log(config):
    level = getattr(logging, config["level"], logging.INFO)
    logging.basicConfig(
        level=level,
        filename=config["file"],
        format=config["format"],
        filemode="a"
    )

def processar_dados(arquivo_json):
    try:
        with open(arquivo_json, "r") as file:
            data = json.load(file)
            logging.info(f"Arquivo JSON '{arquivo_json}' carregado com sucesso.")
    except FileNotFoundError:
        logging.error(f"Arquivo JSON '{arquivo_json}' não encontrado.")
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar o JSON: {e}")
        return []
    
    for record in data:
        try:
            if "name" not in record or record["age"] is None:
                raise ValueError(f"Dado inválido: {record}")
            logging.info(f"Processando registro: {record}")
        except ValueError as e:
            logging.warning(f"Erro no registro: {e}")

    return data

def main():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    configurar_log(config["logging"])
    processar_dados(config["data"]["file"])

if __name__ == "__main__":
    main()