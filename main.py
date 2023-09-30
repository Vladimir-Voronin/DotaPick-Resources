import logging

import settings
from console import console_handler


def logging_configuration():
    logging.getLogger('geventwebsocket.handler').setLevel(logging.WARNING)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    if settings.DEBUG:
        logging.basicConfig(level=logging.DEBUG,
                            format="%(name)s | %(levelname)s | %(asctime)s | %(message)s",
                            datefmt='%I:%M:%S %p')
    else:
        logging.basicConfig(filename='logging.log',
                            level=logging.WARNING,
                            format="%(color)s %(name)s | %(levelname)s | %(asctime)s | %(message)s",
                            datefmt='%m/%d/%Y %I:%M:%S %p')


if __name__ == '__main__':
    logging_configuration()

    console_handler()
