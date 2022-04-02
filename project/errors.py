"""Errors"""


class IncorrectDataReceivedError(Exception):
    """Exception - bad data from socket"""
    def __str__(self):
        return 'Bad massages from remote PC.'


class ServerError(Exception):
    """Exception -  server error"""
    def __init__(self, text):
        self.text = text

class NonDictInputError(Exception):
    """Exception - argument not a dictionary"""
    def __str__(self):
        return 'Bad arg, must be a dictionary.'


class ReqFieldMissingError(Exception):
    """Error - miss field in dictionary"""
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Miss field {self.missing_field}.'
