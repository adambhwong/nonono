import logging, os

# logger configuration
DEBUG = int(os.getenv('DEBUG', 0))
if DEBUG == 0:
    dbg_lvl = logging.INFO
else:
    dbg_lvl = logging.DEBUG
LOG_CFG = {
    "level": dbg_lvl,
    "datefmt": '%Y-%m-%d %H:%M:%S',
    "format": '%(asctime)s [%(levelname)s] %(module)s.%(funcName)s: %(message)s'
}

# Dynamodb table 
DYNDB_TBL = {
    "name": "ShortenUrl",
    "sUrlKey": "ShortenUrl",
    "oUrlKey": "OriginalUrl",
    "oUrlIdx": "OriginalUrlIndex"
}
