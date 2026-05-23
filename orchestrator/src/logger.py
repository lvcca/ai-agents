import logging
import sys
import traceback  

def get_logger(filename):
    logger = logging.getLogger(f"{__name__}.{filename}")
    
    logging.basicConfig(
        stream=sys.stdout, 
        format="%(asctime)s [%(levelname)s] %(message)s", 
        datefmt="%Y-%m-%d %H:%M:%S%z",
        level=logging.DEBUG
        )

    return logger

def error_details():
    error_details = traceback.format_exc()
    return error_details