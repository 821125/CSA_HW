"""Utils"""

import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING


def get_message(client):
    """
    Utility for receiving and decoding messages
    accepts bytes returns a dictionary if something else is received returns a value error
    :param client:
    :return:
    """

    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise ValueError
    raise ValueError


def send_message(sock, message):
    """
    Message encoding and sending utility
    takes a dictionary and sends it
    :param sock:
    :param message:
    :return:
    """
    if not isinstance(message, dict):
        raise TypeError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
