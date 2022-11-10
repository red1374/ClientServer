"""Программа-сервер"""
import logging
import select
import socket
import sys

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, MESSAGE, MESSAGE_TEXT, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message, get_message_dict
import logs.server_log_config
from common.decorators import Log

server_log = logging.getLogger('server')


@Log
def process_client_message(message, messages_list, client):
    """
    Client message processor. Add message to a messages list if it's ok.
    If it's not - add response dict
    :param message: client message
    :param messages_list: messages from all clients
    :param client: client socket object
    :return:
    """
    server_log.debug(f'Client message processing : {message}')

    if ACTION in message and message[ACTION] in [PRESENCE, MESSAGE] and TIME in message and USER in message:
        # and message[USER][ACCOUNT_NAME] == 'Guest'
        if message[ACTION] in PRESENCE:
            # Send OK status to a client
            send_message(client, {RESPONSE: 200})
            return True
        else:
            # Add message to a messages list
            server_log.debug(f'Add message to a message list : {message[MESSAGE_TEXT]}')
            messages_list.append((message[USER][ACCOUNT_NAME], message[MESSAGE_TEXT]))
            return True

    # Send Bad request status to a client
    send_message(client, {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    })

    return False


def main():
    clients_list = []
    messages_list = []

    """
    Load command line parameters to start server. Set default values if parameters are empty or wrong 
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

    # Prepare server socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((listen_address, listen_port))
        server_sock.settimeout(1)

        server_sock.listen(MAX_CONNECTIONS)

        while True:
            server_log.info(f'Waiting for new client ...')
            try:
                client, client_address = server_sock.accept()
            except OSError as err:
                print(err.errno)  # The error number returns None because it's just a timeout
                pass
            else:
                server_log.info(f'New client connected from \'{client_address}\'')
                clients_list.append(client)

            recv_data_lst = []
            send_data_lst = []

            # Checking for clients activity
            try:
                if clients_list:
                    recv_data_lst, send_data_lst, _ = select.select(clients_list, clients_list, [], 0)
            except OSError:
                pass

            # If client sends data, need to process it's message or delete from a clients list
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        server_log.info(f'Creating server response message for client {client_with_message.getpeername()}')
                        process_client_message(get_message(client_with_message), messages_list, client_with_message)
                    except ValueError as value_error:
                        server_log.error(f'Client response message error.')
                        server_log.info(f'Client "{client_with_message.getpeername()}" is disconnected')
                        clients_list.remove(client_with_message)
                    except Exception as error:
                        server_log.error(f'Client response message error: {error}.')
                        server_log.info(f'Client "{client_with_message.getpeername()}" is disconnected')
                        clients_list.remove(client_with_message)

            # Sending messages, if there are messages to send and waiting clients for receiving
            if messages_list and send_data_lst:
                message = get_message_dict(messages_list[0][1], messages_list[0][0])
                del messages_list[0]
                for waiting_client in send_data_lst:
                    try:
                        send_message(waiting_client, message)
                    except:
                        server_log.info(f'Client "{client_with_message.getpeername()}" is disconnected')
                        waiting_client.close()
                        clients_list.remove(waiting_client)


if __name__ == '__main__':
    main()
