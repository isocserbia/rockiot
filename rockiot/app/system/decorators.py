from datetime import datetime
import logging

log = logging.getLogger(__name__)


def timeit(func):
    def wrapper(*args, **kwargs):
        start = datetime.utcnow()
        result = func(*args, **kwargs)
        end = datetime.utcnow()
        log.info(f'Duration: {end - start}')
        return result

    return wrapper
