import logging


def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)-9s %(filename)-15s[:%(lineno)d]\t%(message)s"))
    logger.addHandler(handler)
    return logger


LOG = init_logger()
