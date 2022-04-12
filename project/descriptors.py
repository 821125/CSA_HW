import logging

logger = logging.getLogger('server_dist')


# Port descriptor
class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f'Run server with wrong port {value}. Address must be from 1024 to 65535.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
