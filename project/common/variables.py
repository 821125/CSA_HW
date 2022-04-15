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
# Database (server)
SERVER_CONFIG = 'server_dist.ini'

# Protocol JIM main keys:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Other keys used in the protocol
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'mess_text'
EXIT = 'exit'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'

# Dictionaries - response:
# 200
RESPONSE_200 = {RESPONSE: 200}
# 202
RESPONSE_202 = {RESPONSE: 202,
                LIST_INFO:None
                }
# 400
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
