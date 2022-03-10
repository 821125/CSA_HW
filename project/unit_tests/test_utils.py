"""Utilities unit-tests"""

import json
import unittest
import os
import sys

sys.path.append(os.path.join(os.getcwd(), '..'))
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from common.variables import *
from common.utils import get_message, send_message


class TestUtils(unittest.TestCase):
    test_message = {
        'action': 'presence',
        'time': 1,
        'type': 'status',
        'user': {
            'account_name': 'User',
            'password': ''
        }
    }
    test_correct_response = {
        'response': 200,
        'time': 1,
        'alert': 'Соединение прошло успешно'
    }
    test_error_response = {
        'response': 400,
        'time': 1,
        'error': 'Ошибка соединения'
    }

    # initialize test sockets for client and server
    server_socket = None
    client_socket = None

    def setUp(self) -> None:
        # Create a test socket for the server
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((DEFAULT_IP_ADDRESS, DEFAULT_PORT))
        self.server_socket.listen(MAX_CONNECTIONS)
        # Create a test socket for the client
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((DEFAULT_IP_ADDRESS, DEFAULT_PORT))
        self.client, self.client_address = self.server_socket.accept()

    def tearDown(self) -> None:
        # Close created sockets
        self.client.close()
        self.client_socket.close()
        self.server_socket.close()

    def test_send_wrong_message_from_client(self):
        """
        Checking for an exception if the input is not a dictionary
        """
        self.assertRaises(TypeError, send_message, self.client_socket, 'not dict')

    def test_send_message_client_server(self):
        """
        Check if the correct message was sent
        """

        # Sending a message
        send_message(self.client_socket, self.test_message)
        # We receive and decode the message
        test_response = self.client.recv(MAX_PACKAGE_LENGTH)
        test_response = json.loads(test_response.decode(ENCODING))
        self.client.close()
        # Checking the correspondence between the original message and the one that was sent
        self.assertEqual(self.test_message, test_response)

    def test_get_message_200(self):
        """
        Correct decoding of the correct dictionary
        """
        # We send a test response to the client about the correct sending of data
        message = json.dumps(self.test_correct_response)
        self.client.send(message.encode(ENCODING))
        self.client.close()
        # we get an answer
        response = get_message(self.client_socket)
        # compare sent and received response
        self.assertEqual(self.test_correct_response, response)

    def test_get_message_400(self):
        """
        Correct interpretation of the erroneous dictionary
        """
        # Sending a test error response to the client
        message = json.dumps(self.test_error_response)
        self.client.send(message.encode(ENCODING))
        self.client.close()
        # get an answer
        response = get_message(self.client_socket)
        # compare sent and received response
        self.assertEqual(self.test_error_response, response)

    def test_get_message_not_dict(self):
        """
        Check for an error if the incoming object is not a dictionary
        """
        # Sending a string to the client instead of a dictionary
        message = json.dumps('not dict')
        self.client.send(message.encode(ENCODING))
        self.client.close()

        self.assertRaises(ValueError, get_message, self.client_socket)

    def test_get_message_dict(self):
        """
        Checks if the returned object is a dictionary
        """
        message = json.dumps(self.test_correct_response)
        self.client.send(message.encode(ENCODING))
        self.client.close()

        self.assertIsInstance(get_message(self.client_socket), dict)


if __name__ == '__main__':
    unittest.main()
