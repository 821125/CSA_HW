"""Server logger config"""

import sys
import os
import logging
import logging.handlers

sys.path.append('../')
from common.variables import LOGGING_LEVEL

sys.path.append('../')

# create logs formatter
SERVER_FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

# prepare file name for logging
PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

# create stream loggers handlers
STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding='utf8', interval=1, when='D')
LOG_FILE.setFormatter(SERVER_FORMATTER)

# create and set logger
LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

# debug
if __name__ == '__main__':
    LOGGER.critical('Critical error')
    LOGGER.error('Error')
    LOGGER.debug('Debug message')
    LOGGER.info('Info message')
