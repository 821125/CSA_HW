"""Errors"""


class IncorrectDataRecivedError(Exception):
    def __str__(self):
        return 'Bad massages from remote PC.'


class NonDictInputError(Exception):
    def __str__(self):
        return 'Bad arg, must be a dictionary.'


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Miss field {self.missing_field}.'
