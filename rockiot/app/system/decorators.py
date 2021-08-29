from datetime import datetime
import logging

log = logging.getLogger(__name__)

def timeit(func):
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        log.info(f'Duration: {end - start}')
        return result
    return wrapper
