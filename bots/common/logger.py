import logging
import os

from bots.common.settings import settings


def setup_logger(module_name: str) -> logging.Logger:
    log_dir = settings.log_dir
    log_file = os.path.join(log_dir, f"{module_name}.log")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(module_name)
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
