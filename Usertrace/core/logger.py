import logging
from logging import Logger

from core.constants import LOG_DIR, LOG_FILE


def setup_logger(name: str = "usertrace") -> Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        logger.addHandler(file_handler)

    return logger


logger = setup_logger()
