
import os
import logging
from safe_logger import TimedRotatingFileHandlerSafe

LOG_FILE = 'debug.log'
FORMAT = '[%(asctime)s] [%(levelname)s] [PID: '+str(os.getpid())+'] [%(name)s]:  %(message)s'
FORMATTER = logging.Formatter(FORMAT)

handler = TimedRotatingFileHandlerSafe(LOG_FILE, when='MIDNIGHT')
handler.setLevel(logging.DEBUG)
handler.setFormatter(FORMATTER)

logging.getLogger().addHandler(handler)
