"""Constants"""

import logging

# Default port for network communication
DEFAULT_PORT = 7777
# Default IP address for client connection
DEFAULT_IP_ADDRESS = '127.0.0.1'
# Maximum connection queue
MAX_CONNECTIONS = 5
# Maximum message length in bytes
MAX_PACKAGE_LENGTH = 1024
# Project Encoding
ENCODING = 'utf-8'
# Current logging level
LOGGING_LEVEL = logging.DEBUG

# Protocol JIM main keys:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'

# Other keys used in the protocol
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
