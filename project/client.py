"""Client"""

import sys
import json
import socket
import time
import argparse
import logging
import logs.config_client_log
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT
from common.utils import get_message, send_message
from errors import ReqFieldMissingError, ServerError
from decos import Log

# Initial client logger
CLIENT_LOGGER = logging.getLogger('client')


@Log(CLIENT_LOGGER)
def message_from_server(message):
    """
    The function generates message from server
    :param message:
    """
    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
        print(f'Received message from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        CLIENT_LOGGER.info(f'Received message from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        CLIENT_LOGGER.error(f'Received bad message from server: {message}')


@Log(CLIENT_LOGGER)
def create_message(sock, account_name='Guest'):
    """
    The function ask message text and return it
    :param sock:
    :param account_name:
    :return message_dict:
    """
    message = input(f'Please input message for send or !!! for exit: ')
    if message == '!!!':
        sock.close()
        CLIENT_LOGGER.info('Finished by user')
        print('Service closed')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Message dict was formed: {message_dict}')
    return message_dict


@Log(CLIENT_LOGGER)
def create_presence(account_name='Guest'):
    """
    The function generates a client presence request
    :param account_name:
    :return out:
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
def process_response_ans(message):
    """
    The function parses the server response
    :param message:
    """
    CLIENT_LOGGER.debug(f'Parse greeting message from server: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400: {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@Log(CLIENT_LOGGER)
def arg_parser():
    """
    Create a command line argument parser
    :return server_address, server_port, client_mode:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # Check port number
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Wrong port: {server_port}. Range must be from 1024 to 65535.')
        sys.exit(1)

    CLIENT_LOGGER.info(f'Client started with server address: {server_address}, port: {server_port}')

    # Check selected mode
    if client_mode not in ('listen', 'send'):
        CLIENT_LOGGER.critical(f'Invalid mode {client_mode}, valid modes is listen, send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    """
    Loading command line options
    """
    server_address, server_port, client_mode = arg_parser()
    CLIENT_LOGGER.info(f'Started client with params: adr: {server_address} | prt: {server_port} | mod: {client_mode}')
    # Initial socket
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message_to_server = create_presence()
        send_message(transport, message_to_server)
        answer = process_response_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Connection done. Server response {answer}')
        print('Connection done')
        print(answer)
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Bad JSON data')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'Miss field {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Server out {server_address}:{server_port}')
        sys.exit(1)
    else:
        # If connection is correct
        if client_mode == 'send':
            print('Send messages mode')
        else:
            print('Receive messages mode')
        while True:
            # Send message mode
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionError, ConnectionResetError, ConnectionRefusedError):
                    CLIENT_LOGGER.error(f'Server connection {server_address} has lost')
                    sys.exit(1)
            # Receive message mode
            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionError, ConnectionResetError, ConnectionRefusedError):
                    CLIENT_LOGGER.error(f'Server connection {server_address} has lost')
                    sys.exit(1)


if __name__ == '__main__':
    main()
