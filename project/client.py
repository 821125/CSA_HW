"""Client"""

import sys
import json
import socket
import time
import argparse
import logging
import threading
import logs.config_client_log
from common.variables import *
from common.utils import get_message, send_message
from errors import IncorrectDataReceivedError, ReqFieldMissingError, ServerError
from decos import Log

# Initial clients logger
CLIENT_LOGGER = logging.getLogger('client_dist')


# Initial client logger class
class ClientSender(threading.Thread):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Dictionary creation function with output message
    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    # Data sender function.
    # The function receives as input sender and message and send data to server.
    def create_message(self):
        to = input('Input sender for message: ')
        message = input('Input message: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Messages dictionary has formed: {message_dict}')
        try:
            send_message(self.sock, message_dict)
            CLIENT_LOGGER.info(f'Message has send to: {to}')
        except:
            CLIENT_LOGGER.critical('Connection failed')
            exit(1)

    # User communicate function.
    # The function request commands and send messages.
    def run(self):
        self.print_help()
        while True:
            command = input('Input command: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                print('Connection close')
                CLIENT_LOGGER.info('Finished by user')
                # Necessary delay
                time.sleep(0.5)
                break
            else:
                print('Unknown command, please try again. Help - for help.')

    # Helper function
    def print_help(self):
        print('Supported commands: ')
        print('message: send message')
        print('help: to print hints')
        print('exit: to exit')


# The class for receive a message from the server.
# The class receive message and print to console.
class ClientReader(threading.Thread):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    # Main class loop, receive messages and print to console.
    # if connection is down, exit.
    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nReceive user message {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    CLIENT_LOGGER.info(
                        f'Receive user message {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Receive incorrect message from server: {message}')
            except IncorrectDataReceivedError:
                CLIENT_LOGGER.error(f'Decoding failed')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                CLIENT_LOGGER.critical(f'Connection is down')
                break


# The function generate a client presence request
@Log(CLIENT_LOGGER)
def create_presence(account_name):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    CLIENT_LOGGER.debug(f'Formed {PRESENCE} message for user {account_name}')
    return out


# The function parse server response, return 200 if OK or generate exception
@Log(CLIENT_LOGGER)
def process_response_ans(message):
    CLIENT_LOGGER.debug(f'Parse server greeting message: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


# Args command prompt parser
@Log(CLIENT_LOGGER)
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # check port number
    if not 1023 < server_port < 65536:
        CLIENT_LOGGER.critical(
            f'Bad client port: {server_port}. Valid address range from 1024 to 65535. Client exit.')
        exit(1)

    return server_address, server_port, client_name


def main():
    # Run alert
    print('Console messanger. Client module.')

    # download command prompt parameters
    server_address, server_port, client_name = arg_parser()

    # Request username if not set
    if not client_name:
        client_name = input('Input user name: ')
    else:
        print(f'Client module has started with name: {client_name}')

    CLIENT_LOGGER.info(
        f'Client has started with ports: server address: {server_address} , '
        f'port: {server_port}, user name: {client_name}')

    # Sock initial
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_response_ans(get_message(transport))
        CLIENT_LOGGER.info(f'Connection up. Server response: {answer}')
        print(f'Server connection up.')
    except json.JSONDecodeError:
        CLIENT_LOGGER.error('JSON string parse failed')
        exit(1)
    except ServerError as error:
        CLIENT_LOGGER.error(f'Connection server error: {error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        CLIENT_LOGGER.error(f'Miss field {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        CLIENT_LOGGER.critical(
            f'Server connection failed {server_address}:{server_port}')
        exit(1)
    else:
        # If connection is correct, start client receive message process
        module_receiver = ClientReader(client_name, transport)
        module_receiver.daemon = True
        module_receiver.start()

        # start client interaction
        module_sender = ClientSender(client_name, transport)
        module_sender.daemon = True
        module_sender.start()
        CLIENT_LOGGER.debug('Process started')

        # Watchdog - main loop, if thread down break loop
        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
