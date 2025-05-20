import logging
import os

LOG_DIR = "app/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(entidade: str) -> logging.Logger:
    entidade = entidade.lower()
    logger = logging.getLogger(entidade)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

        file_handler = logging.FileHandler(os.path.join(LOG_DIR, f"{entidade}.log"), encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger