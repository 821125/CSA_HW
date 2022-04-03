"""Server"""

import socket
import sys
import argparse
import logging
import select
import logs.config_server_log
from errors import IncorrectDataReceivedError
from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, \
    USER, ACCOUNT_NAME, SENDER, PRESENCE, ERROR, MESSAGE, \
    MESSAGE_TEXT, RESPONSE_400, DESTINATION, RESPONSE_200, EXIT
from common.utils import get_message, send_message
from decos import Log

# Server logging initialization.
SERVER_LOGGER = logging.getLogger('server')


@Log(SERVER_LOGGER)
def process_client_message(message, messages_list, client, clients, names):
    """
    Message handler from clients, takes a dictionary -
    a message from the clint, checks the correctness,
    returns a response dictionary for the client
    :param message:
    :param messages_list:
    :param client:
    :param clients:
    :param names:
    :return:
    """
    SERVER_LOGGER.debug(f'Parsing clients message: {message}')
    # If message
    if ACTION in message and message[ACTION] == PRESENCE and \
            TIME in message and USER in message:
        # If user not registered -> register or send response and close connection
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'User name is taken'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # If message -> add to queue
    elif ACTION in message and message[ACTION] == MESSAGE and \
            DESTINATION in message and TIME in message \
            and SENDER in message and MESSAGE_TEXT in message:
        messages_list.append(message)
        return
    # If client exit
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    # Else -> Bad request
    else:
        response = RESPONSE_400
        response[ERROR] = 'Bad response'
        send_message(client, response)
        return


@Log(SERVER_LOGGER)
def process_message(message, names, listen_socks):
    """
    The function send message to client. Received dictionary message, return nothing
    :param message:
    :param names:
    :param listen_socks:
    :return:
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        SERVER_LOGGER.info(f'Message has sent to {message[DESTINATION]} '
                           f'from user {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        SERVER_LOGGER.error(
            f'User {message[DESTINATION]} not registered.')


@Log(SERVER_LOGGER)
def arg_parser():
    """
    Command Line Argument Parser
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    # Port checking
    if not 1023 < listen_port < 65536:
        SERVER_LOGGER.critical(f'Try start with port: {listen_port}. Port range must be from 1024 to 65535.')
        sys.exit(1)

    return listen_address, listen_port


def main():
    """
    Loading command line parameters, if there are no parameters, then set the default values.
    First we process the port:
    server.py -p 8888 -a 127.0.0.1
    :return:
    """
    listen_address, listen_port = arg_parser()
    SERVER_LOGGER.info(f'Listen port: {listen_port}, Listen address: {listen_address}.')

    # Preparing socket
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.5)

    # Clients list, message line
    clients = []
    messages = []

    # Dictionary with users names and sockets
    names = dict()  # {client_name: client_socket}

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
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message, clients, names)
                except IncorrectDataReceivedError:
                    SERVER_LOGGER.info(f'Client {client_with_message.getpeername()} disconnect from server')
                    clients.remove(client_with_message)

        # If messages -> process every message
        for i in messages:
            try:
                process_message(i, names, send_data_lst)
            except Exception:
                SERVER_LOGGER.info(f'Connect with client {i[DESTINATION]} has lost')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
