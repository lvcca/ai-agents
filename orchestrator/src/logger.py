import logging
import sys

def get_logger(filename):
    logger = logging.getLogger(f"{__name__}.{filename}")
    
    logging.basicConfig(
        stream=sys.stdout, 
        format="%(asctime)s [%(levelname)s] %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S%z",
        level=logging.DEBUG
        )

    return logger