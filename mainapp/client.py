"""Программа-клиент"""
import logging
import sys
import socket
import time
from common.variables import PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, ACTION, MESSAGE_TEXT
from common.utils import get_message, send_message, get_params, get_message_dict
from common.decorators import Log

import logs.client_log_config
from errors import ReqFieldMissingError, ServerError, NonDictInputError

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
def process_presence_answer(message):
    """
    Processing server answer
    :param message:
    :return:
    """
    client_log.debug(f'Server response message: {message}')
    if RESPONSE in message:
        if int(message[RESPONSE]) == 200:
            return '200 : OK'
        raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


def message_from_server(message):
    """
    Processing other clients messages from server
    :param message:
    :return:
    """
    if ACTION in message and message[ACTION] == MESSAGE and \
            USER in message and MESSAGE_TEXT in message:
        print(f'Message from "{message[USER][ACCOUNT_NAME]}":\n{message[MESSAGE_TEXT]}')
        client_log.info(f'Message from "{message[USER][ACCOUNT_NAME]}":\n{message[MESSAGE_TEXT]}')
    else:
        client_log.error(f'Incorrect server message format: {message}')


def main():
    # Get command line params and set default socket params
    params = get_params()

    if not params:
        client_log.critical(f'Empty required params: server_address and server_post!')
        sys.exit(1)
    else:
        try:
            server_address = params['ip']
            server_port = int(params['p'])
            if server_port < 1024 or server_port > 65535:
                raise ValueError
        except IndexError:
            server_address = DEFAULT_IP_ADDRESS
            server_port = DEFAULT_PORT
            client_log.info(f'Setting up a default port and address values')
        except ValueError:
            client_log.critical(f'Wrong port number: {server_port}. Value must be between 1024 and 65535')
            sys.exit(1)

    # Initiate client socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        client_log.info(f'Starting client app')
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_sock.connect((server_address, server_port))

        client_name = 'Guest-' + str(client_sock.getsockname()[1])

        message_to_server = create_presence(account_name=client_name)

        client_log.info(f'Sending hello message to the server')
        send_message(client_sock, message_to_server)
        try:
            answer = process_presence_answer(get_message(client_sock))
            client_log.info(f'Getting answer from a server: {answer}')
        except ServerError as error:
            client_log.error(f'Server returned an error: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as error:
            client_log.error(error)
            sys.exit(1)
        except ConnectionRefusedError:
            client_log.critical(f'Connection refused error to server {server_address}:{server_port}')
            sys.exit(1)
        else:
            client_log.info(f'Starting client communications')

            # Start communication with server
            if params['m'] == 'send':
                print(f'--- {client_name}: I can sand a message ---\n')
            else:
                print(f'--- {client_name}: I can read a message ---\n')
            while True:
                # Send message mode
                if params['m'] == 'send':
                    client_log.info(f'Entering Client send mode')
                    try:
                        message = input('Enter a message or "q" to quit: ')
                        client_log.info(f'Sending a message: {message}')
                        dict_message = get_message_dict(message, account_name=client_name)
                        client_log.info(f'Sending a dict: {dict_message}')
                        send_message(client_sock, dict_message)
                        if message == 'q':
                            client_sock.close()
                            client_log.info(f'User "{client_sock.getpeername()}" quit a chat')
                            print('End of chat!')
                            sys.exit(0)
                    except NonDictInputError as error:
                        client_log.error(error)
                        sys.exit(1)
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        client_log.error(f'Server connection error: {server_address}')
                        sys.exit(1)

                # Read message mode
                if params['m'] == 'listen':
                    client_log.info(f'Entering Client listen mode')
                    try:
                        message_from_server(get_message(client_sock))
                    except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                        client_log.error(f'Server connection error: {server_address}')
                        sys.exit(1)


if __name__ == '__main__':
    main()
