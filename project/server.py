"""Server"""

import socket
import sys
import argparse
import logging
import select
import time
import logs.config_server_log
from errors import IncorrectDataReceivedError
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, SENDER, MAX_CONNECTIONS, MESSAGE, MESSAGE_TEXT, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message
from decos import Log

# Server logging initialization.
SERVER_LOGGER = logging.getLogger('server')


@Log(SERVER_LOGGER)
def process_client_message(message, messages_list, client):
    """
    Message handler from clients, takes a dictionary -
    a message from the clint, checks the correctness,
    returns a response dictionary for the client
    :param message:
    :param messages_list:
    :param client:
    :return:
    """
    SERVER_LOGGER.debug(f'Parsing clients message: {message}')
    # If success, receive and response
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    # If message add to line messages. No response.
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    # Else Bad Request
    else:
        send_message(client, {RESPONSE: 400, ERROR: 'Bad Request'})
        return


@Log(SERVER_LOGGER)
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
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(f'Try start with port: {listen_port}. Port range must be from 1024 to 65535.')
        sys.exit(1)
    SERVER_LOGGER.info(f'Listen port: {listen_port}, Listen address: {listen_address}.')

    # Preparing socket
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # Clients list, message line
    clients = []
    messages = []

    # Port listening
    transport.listen(MAX_CONNECTIONS)
    # Main loop
    while True:
        # Waiting connection, if timeout raise exception
        try:
            client, client_address = transport.accept()
        except OSError as err:
            print(err.errno)  # The error number returns None because it's just a timeout
            pass
        else:
            SERVER_LOGGER.info(f'Connection with PC {client_address}')
            clients.append(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []
        # Check awaiting clients
        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # Receive message if message append to dict else exception
        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message), messages, client_with_message)
                except IncorrectDataReceivedError:
                    SERVER_LOGGER.info(f'Client {client_with_message.getpeername()} disconnect from server')
                    clients.remove(client_with_message)

        # If messages to send and awaiting clients, send message
        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except IncorrectDataReceivedError:
                    SERVER_LOGGER.info(f'Client {waiting_client.getpeername()} disconnected from server.')
                    waiting_client.close()
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
