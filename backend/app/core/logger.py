import logging
import os

from backend.app.core.settings import settings


def setup_logger() -> logging.Logger:
    log_dir = settings.log_dir
    log_file = os.path.join(log_dir, "backend.log")

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("backend")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger