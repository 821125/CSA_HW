"""Server"""

import socket
import sys
import argparse
import json
import logging
import logs.config_server_log
from errors import IncorrectDataRecivedError
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, RESPONDEFAULT_IP_ADDRESSSE
from common.utils import get_message, send_message

SERVER_LOGGER = logging.getLogger('server')


def process_client_message(message):
    """
    Message handler from clients, takes a dictionary -
    a message from the clint, checks the correctness,
    returns a response dictionary for the client
    :param message:
    :return:
    """
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONDEFAULT_IP_ADDRESSSE: 400,
        ERROR: 'Bad Request'
    }


def create_arg_parser():
    """
    Command Line Argument Parser
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    return parser


def main():
    """
    Loading command line parameters, if there are no parameters, then set the default values.
    First we process the port:
    server.py -p 8888 -a 127.0.0.1
    :return:
    """
    parser = create_arg_parser()
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # Port checking

    if not 1024 < listen_port < 65536:
        SERVER_LOGGER.critical(f'{listen_port}. Port range must be from 1024 to 65535.')
        sys.exit(1)
    SERVER_LOGGER.info(f'Listen port: {listen_port}, Listen address: {listen_address}.')

    # Preparing socket

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))

    # Port listening

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            SERVER_LOGGER.debug(f'Got message {message_from_client}')
            response = process_client_message(message_from_client)
            SERVER_LOGGER.info(f'Report to client: {response}')
            send_message(client, response)
            SERVER_LOGGER.debug(f'Connection to {client_address}')
            client.close()
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.error(f'Bad JSON client data: {client_address}.')
            client.close()
        except IncorrectDataRecivedError:
            SERVER_LOGGER.error(f'Bad data from client {client_address}.')
            client.close()


if __name__ == '__main__':
    main()
