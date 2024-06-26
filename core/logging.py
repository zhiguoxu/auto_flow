import logging
import os
import sys


def get_logger(name: str) -> logging.Logger:
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s", datefmt="%m/%d/%Y %H:%M:%S"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(os.getenv("LOG_LEVEL", "DEBUG"))
    logger.addHandler(handler)
    return logger
