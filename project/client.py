"""Client"""

import sys
import json
import socket
import time
import argparse
import logging
import threading
import logs.config_client_log
from common.variables import DEFAULT_PORT, DEFAULT_IP_ADDRESS, \
    ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, \
    ERROR, MESSAGE, MESSAGE_TEXT, DESTINATION, EXIT
from common.utils import get_message, send_message
from errors import IncorrectDataReceivedError, ReqFieldMissingError, ServerError
from decos import Log

# Initial client logger
CLIENT_LOGGER = logging.getLogger('client')


@Log(CLIENT_LOGGER)
def create_exit_message(account_name):
    """
    The function create dictionary with entry message
    :param account_name:
    :return:
    """
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@Log(CLIENT_LOGGER)
def message_from_server(sock, my_username):
    """
    The handlers function for messages from server
    :param sock:
    :param my_username:
    """
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and \
                    SENDER in message and DESTINATION in message \
                    and MESSAGE_TEXT in message and MESSAGE[DESTINATION] == my_username:
                print(f'\nReceived message from user {message[SENDER]}:'
                      f'\n{message[MESSAGE_TEXT]}')
                CLIENT_LOGGER.info(f'Received message from user {message[SENDER]}:'
                                   f'\n{message[MESSAGE_TEXT]}')
            else:
                CLIENT_LOGGER.error(f'Received incorrect server from server: {message}')
        except IncorrectDataReceivedError:
            CLIENT_LOGGER.error(f'Decoding message failed')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            CLIENT_LOGGER.critical(f'Server connection lost')
            break


@Log(CLIENT_LOGGER)
def create_message(sock, account_name='Guest'):
    """
    The function ask message text and return it
    :param sock:
    :param account_name:
    """
    to_user = input('Input the recipient of the message: ')
    message = input('Input the message for send')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    CLIENT_LOGGER.debug(f'Messages dictionary has formed: {message_dict}')
    try:
        send_message(sock, message_dict)
        CLIENT_LOGGER.info(f'Message to user {to_user} has sent')
    except Exception as e:
        print(e)
        CLIENT_LOGGER.critical('Server connection has lost')
        sys.exit(1)


@Log(CLIENT_LOGGER)
def user_interactive(sock, username):
    """
    The function for communication with user
    :param sock:
    :param username:
    """
    while True:
        command = input('Input the command: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Connection is closing...')
            CLIENT_LOGGER.info('Connection is closing by user...')
            # Delay need to send message about exit
            time.sleep(0.5)
            break
        else:
            print('Unknown command, please try again')


@Log(CLIENT_LOGGER)
def create_presence(account_name):
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


def print_help():
    """
    The function print help
    """
    print('Supported commands: ')
    print('message - send message')
    print('help - print hints for commands')
    print('exit - exit from program')


@Log(CLIENT_LOGGER)
def process_response_ans(message):
    """
    The function parses the server response
    return 200 if all is OK or generated exception
    :param message:
    :return:
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
    The main function
    """
    # Loading command line options
    server_address, server_port, client_name = arg_parser()

    # Starting alert
    print(f'Messanger. Client module. Client name: {client_name}')

    # if not client name, ask for client name
    if not client_name:
        client_name = input('Input the client name: ')

    CLIENT_LOGGER.info(f'Started client with params: adr: {server_address} | port: {server_port} | name: {client_name}')
    # Initial socket
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_message(client_name))
        answer = process_response_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Connection done. Server response {answer}')
        print('Connection done')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('Decoding JSON string has failed')
        sys.exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'Error connection to server: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'Miss field {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        CLIENT_LOGGER.critical(f'Server out {server_address}:{server_port}')
        sys.exit(1)
    else:
        # Start client process if connection is OK
        receiver = threading.Thread(target=message_from_server, args=(transport, client_name), daemon=True)
        receiver.start()

        # Start sending messages
        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name), daemon=True)
        user_interface.start()
        CLIENT_LOGGER.debug('Processes has started')

        # Watchdog is main loop, if one of threads has finished connection closed/lost
        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
