import logging
import sys


def get_structured_logger(module_name: str) -> logging.Logger:
    """
    Creates and returns a structured logger for modular cv components.
    """
    logger = logging.getLogger(f"signbridge.{module_name}")

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger
