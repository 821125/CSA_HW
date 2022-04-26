import logging
import sys

if sys.argv[0].find("client_dist") == -1:
    logger = logging.getLogger("server_dist")
else:
    logger = logging.getLogger("client_dist")


class Port:

    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f"Bad port {value}. Valid address from 1024 to 65535."
            )
            raise TypeError("Bad port number")
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
