"""Программа-клиент"""
import logging
import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
from common.utils import get_message, send_message
from common.decorators import Log

import logs.client_log_config
from errors import ReqFieldMissingError

client_log = logging.getLogger('client')


@Log
def create_presence(account_name='Guest'):
    """
    Функция генерирует запрос о присутствии клиента
    :param account_name:
    :return:
    """

    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    client_log.debug(f'Presence message from a user {account_name}: {out}')

    return out


@Log
def process_ans(message):
    """
    Функция разбирает ответ сервера
    :param message:
    :return:
    """
    client_log.debug(f'Server response message: {message}')
    if RESPONSE in message:
        if int(message[RESPONSE]) == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ReqFieldMissingError(RESPONSE)


def main():
    """Загружаем параметы коммандной строки"""
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
        client_log.info(f'Setting up a default port and address values')
    except ValueError:
        client_log.critical(f'Wrong port number: {server_port}. Value must be between 1024 and 65535')
        sys.exit(1)

    # Инициализация сокета и обмен

    client_log.info(f'Starting client app')
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((server_address, server_port))
    message_to_server = create_presence()

    client_log.info(f'Sending hello message to the server')
    send_message(transport, message_to_server)
    try:
        answer = process_ans(get_message(transport))
        client_log.info(f'Getting answer from a server: {answer}')
    except ReqFieldMissingError as error:
        client_log.error(error)

    client_log.info(f'End of transmission!')
    transport.close()


if __name__ == '__main__':
    main()
