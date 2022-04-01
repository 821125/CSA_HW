"""Client"""

import sys
import json
import socket
import time
import argparse
import logging
import logs.config_client_log
from common.variables import ACTION, TIME, USER, ACCOUNT_NAME, RESPONSE, \
    DEFAULT_IP_ADDRESS, DEFAULT_PORT, ERROR, PRESENCE
from common.utils import get_message, send_message
from errors import ReqFieldMissingError
from decos import Log

# Initial client logger
CLIENT_LOGGER = logging.getLogger('client')


@Log(CLIENT_LOGGER)
def create_presence(account_name='Guest'):
    """
    The function generates a client presence request
    :param account_name:
    :return:
    """
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'{PRESENCE} message for user {account_name}')
    return out


@Log(CLIENT_LOGGER)
def process_ans(message):
    """
    The function parses the server response
    :param message:
    :return:
    """
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


@Log(CLIENT_LOGGER)
def create_arg_parser():
    """
    Create a command line argument parser
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    return parser


def main():
    """Loading command line options"""
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port

    # Check port number
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Wrong port: {server_port}. Range must be from 1024 to 65535.')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Client started with server address: {server_address}, port: {server_port}')

    # Initial socket
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(transport, message_to_server)
        answer = process_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Server response {answer}')
        print(answer)
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Bad JSON data')
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'Miss field {missing_error.missing_field}')
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Server out {server_address}:{server_port}')


if __name__ == '__main__':
    main()
