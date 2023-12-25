import logging
from logging.config import fileConfig
from src.common.constants import DEBUG_MODE

if DEBUG_MODE:
    fileConfig("logs/logging.ini")
    logger = logging.getLogger("root")
    logger.debug("Debug mode is on.")
else:
    logging.basicConfig(level=logging.WARNING)
