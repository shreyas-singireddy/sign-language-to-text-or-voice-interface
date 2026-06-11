import logging
import sys


def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with standard formatting.
    """
    logger = logging.getLogger(name)

    # If the logger is already configured, return it
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # Define a clean formatting pattern
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
