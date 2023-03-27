"""Project logger."""

from loguru import logger


LOGURU_FORMAT = (
    '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | '
    '<level>{level: <8}</level> | '
    '<green>{name: <25}</green> | '
    '<cyan>{module}:{function}:{line}</cyan> - <level>{message}</level>'
)

LOGGING_FORMAT = (
    '%(asctime)s | '
    '%(levelname)-8s | '
    '%(name)-25s | '
    '%(module)s:%(funcName)s:%(lineno)d - %(message)s'
)

logger.debug('loaded logger')
