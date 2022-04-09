"""Server"""

import socket
import argparse
import select
import logs.config_server_log
from errors import IncorrectDataReceivedError
from common.variables import *
from common.utils import *
from decos import Log

# Server logging initialization.
SERVER_LOGGER = logging.getLogger('server_dist')


@Log(SERVER_LOGGER)
# Args command prompt parser
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


# Main server class
class Server:
    def __init__(self, listen_address, listen_port):
        # connection param
        self.addr = listen_address
        self.port = listen_port

        # connection client list
        self.clients = []

        # sending messages list
        self.messages = []

        # name-sock dictionary
        self.names = dict()

    def init_socket(self):
        SERVER_LOGGER.info(
            f'Server up, port: {self.port}, '
            f'connection address: {self.addr}. ')

        # Prepare socket
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        # Socket listening
        self.sock = transport
        self.sock.listen()

    def main_loop(self):

        # Socket initialization
        self.init_socket()

        # Server main loop
        while True:
            # Awaiting connection, it timeout - exception.
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'PC connection is up {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []

            # Check awaiting clients
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            # Receive message. Exception if error.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        SERVER_LOGGER.info(f'Client {client_with_message.getpeername()} has disconnected.')
                        self.clients.remove(client_with_message)

            # If message then process
            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except Exception as e:
                    SERVER_LOGGER.info(f'Connection with '
                                       f'{message[DESTINATION]} has lost, '
                                       f' error {e}')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    # The function send message to client
    # Receive dictionary
    # Return nothing
    def process_message(self, message, listen_socks):
        if message[DESTINATION] in self.names and \
                self.names[message[DESTINATION]] in listen_socks:
            send_message(self.names[message[DESTINATION]], message)
            SERVER_LOGGER.info(f'Message to user has sent {message[DESTINATION]} '
                               f'from user {message[SENDER]}.')
        elif message[DESTINATION] in self.names \
                and self.names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOGGER.error(
                f'User {message[DESTINATION]} not registered.')

    # Client messages parser, receive dictionary - message from client,
    # check, send dictionary-answer.
    def process_client_message(self, message, client):
        SERVER_LOGGER.debug(f'Client message parser : {message}')
        # If this is a presence message, accept and respond
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            # If not registered -> register else send response
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Username already taken '
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # If message then add to queue. No answer required.
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and DESTINATION in message \
                and TIME in message \
                and SENDER in message \
                and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        # If client exit
        elif ACTION in message \
                and message[ACTION] == EXIT \
                and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        # otherwise, Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'bad response'
            send_message(client, response)
            return


def main():
    # Loading params of command prompt if not then set default.
    listen_address, listen_port = arg_parser()

    # Create an instance of a class.
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
