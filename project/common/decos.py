import sys
import logs.config_server_log
import logs.config_client_log
import logging

if sys.argv[0].find('client_dist') == -1:
    logger = logging.getLogger('server_dist')
else:
    logger = logging.getLogger('client_dist')


def log(func_to_log):
    def log_saver(*args, **kwargs):
        logger.debug(
            f'Function called {func_to_log.__name__} with params {args} , {kwargs}. Called from module {func_to_log.__module__}')
        ret = func_to_log(*args, **kwargs)
        return ret

    return log_saver
