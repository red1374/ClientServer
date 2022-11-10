"""Программа-сервер"""
import logging
import socket
import sys
import json

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message
import logs.server_log_config

server_log = logging.getLogger('server')


def process_client_message(message):
    """
    Обработчик сообщений от клиентов, принимает словарь -
    сообщение от клинта, проверяет корректность,
    возвращает словарь-ответ для клиента

    :param message:
    :return:
    """
    server_log.debug(f'Client message processing : {message}')

    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def main():
    """
    Загрузка параметров командной строки, если нет параметров, то задаём значения по умолчанию.
    Сначала обрабатываем порт:
    server.py -p 8888 -a 127.0.0.1
    """

    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        server_log.critical(f'Insert port number after -\'p\' parameter')
        sys.exit(1)
    except ValueError:
        server_log.critical(f'Wrong port number: {listen_port}. Value must be between 1024 and 65535')
        sys.exit(1)

    # Затем загружаем какой адрес слушать

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        server_log.critical(f'Insert listen address after -\'a\' parameter')
        sys.exit(1)

    server_log.info(f'Server started at {listen_address}:{listen_port}')

    # Готовим сокет

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    transport.bind((listen_address, listen_port))

    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)

    while True:
        server_log.info(f'Waiting for new client ...')
        client, client_address = transport.accept()
        try:
            server_log.info(f'New client connected from \'{client_address}\'')
            message_from_client = get_message(client)

            response = process_client_message(message_from_client)
            server_log.info(f'Creating server response message')
            send_message(client, response)

            server_log.info(f'Closing client connection')
            client.close()
        except (ValueError, json.JSONDecodeError):
            server_log.error(f'Got incorrect message from a client')
            client.close()


if __name__ == '__main__':
    main()
