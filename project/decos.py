"""
Logger-decorator
"""

import inspect
import logging
import sys

sys.path.append('../')
import logs.config_client_log
import logs.config_server_log
from functools import wraps


class LogFilter(logging.Filter):
    """
    Filter allow writing only logs with additional condition.
    """

    def filter(self, record):
        return "fUnction" in record.getMessage()


class Log:
    def __init__(self, logger=None):
        """
        LOGGER = logging.getLogger('client')

        """

        self.logger = logger

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            parent_func_name = inspect.currentframe().f_back.f_code.co_name
            module_name = inspect.currentframe().f_back.f_code.co_filename.split("/")[-1]
            if self.logger is None:
                """
                if decorator called from utils.py
                then associate logger with module_name
                """
                logger_name = module_name.replace('.py', '')
                self.logger = logging.getLogger(logger_name)

            # create Class instance for new filter and add it to current logger
            new_filter = LogFilter()
            self.logger.addFilter(new_filter)
            print('List of filters after adding new_filter: ', self.logger.filters)

            # Message where <function> write as "fUnction" will be filtered
            self.logger.debug(f'fUnction {func.__name__} called from function {parent_func_name} '
                              f'in module {module_name} with arguments: {args}; {kwargs}')

            # Message where <function> write as "Function" won't be filtered
            self.logger.debug(f'Function {func.__name__} called from function {parent_func_name} '
                              f'in module {module_name} with arguments: {args}; {kwargs}')

            # Delete filter
            self.logger.filters.remove(new_filter)
            print('List of filters after removing new_filter: ', self.logger.filters)

            result = func(*args, **kwargs)
            return result

        return wrapper
