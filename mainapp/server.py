"""Программа-сервер"""
import logging
import select
import socket
import sys

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, TIME,\
    PRESENCE, MESSAGE, EXIT, MESSAGE_TEXT, USER, ERROR, DEFAULT_PORT, SENDER, DESTINATION
from common.utils import get_message, send_message, get_message_dict
import logs.server_log_config
from common.decorators import Log

server_log = logging.getLogger('server')

clients_list = []  # Client sockets list
clients_names = dict()  # Client names with sockets {client_name: client_socket}
messages_list = []  # Messages from all clients


@Log
def process_client_message(message, client):
    """
    Client message processor. Add message to a messages list if it's ok.
    If it's not - add response dict or close connection with this client
    :param message: client message
    :param client: client socket object
    :return:
    """
    global messages_list, clients_names, clients_list

    server_log.debug(f'Client message processing : {message}')

    if ACTION in message and message[ACTION] in [PRESENCE, MESSAGE, EXIT] and TIME in message:
        if message[ACTION] in PRESENCE and USER in message and ACCOUNT_NAME in message[USER]:
            # Send OK status to a client
            if message[USER][ACCOUNT_NAME] not in clients_names.keys():
                # Add new client with unique name to clients names list
                clients_names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, {RESPONSE: 200})
                return True
            else:
                # Client with this account name is already exists
                send_message(client, {
                    RESPONSE: 400,
                    ERROR: f' Client with account name "{message[USER][ACCOUNT_NAME]}" is already exists'
                })
                clients_list.remove(client)
                client.close()
                return True
        elif DESTINATION in message and SENDER in message and MESSAGE_TEXT in message:
            # Add message to a messages list
            server_log.debug(f'Add message to a message list : {message[MESSAGE_TEXT]}')
            messages_list.append(message)
            return True
        elif message[ACTION] in EXIT and ACCOUNT_NAME in message:
            # Close client socket if client closed the chat
            clients_list.remove(clients_names[message[ACCOUNT_NAME]])
            clients_names[message[ACCOUNT_NAME]].close()
            del clients_names[message[ACCOUNT_NAME]]
            return True

    # Send Bad request status to a client
    send_message(client, {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    })

    return False


@Log
def process_message(message, listen_socks):
    global clients_names
    """
    Function try to send a message by destinations name 
    :param message:
    :param listen_socks:
    :return:
    """
    if message[DESTINATION] in clients_names and clients_names[message[DESTINATION]] in listen_socks:
        # Send message to the client with DESTINATION account name
        send_message(clients_names[message[DESTINATION]], message)
        server_log.info(f'Message send to user {message[DESTINATION]} from user {message[SENDER]}')
    elif message[DESTINATION] in clients_names and clients_names[message[DESTINATION]] not in listen_socks:
        # There's now socket for DESTINATION account name
        raise ConnectionError
    else:
        server_log.error(f'There\'s no usr with "{message[DESTINATION]}" account name')


def main():
    global messages_list, clients_names, clients_list

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

    # Set ip address to listen
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

        # Setting this option to disable "accept" function locking state
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

            # If client sends data, need to process it's messages or delete from a clients list
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        server_log.info(f'Creating server response message for client {client_with_message.getpeername()}')
                        process_client_message(get_message(client_with_message), client_with_message)
                    except ValueError as value_error:
                        server_log.error(f'Client response message error.')
                        server_log.info(f'Client "{client_with_message.getpeername()}" is disconnected')
                        clients_list.remove(client_with_message)
                    except Exception as error:
                        server_log.error(f'Client response message error: {error}.')
                        server_log.info(f'Client "{client_with_message.getpeername()}" is disconnected')
                        clients_list.remove(client_with_message)

            # Send messages to a clients if not empty
            if messages_list:
                for i in messages_list:
                    try:
                        process_message(i, send_data_lst)
                    except Exception:
                        server_log.info(f'Client "{i[DESTINATION]}" is disconnected')
                        clients_list.remove(clients_names[i[DESTINATION]])
                        del clients_names[i[DESTINATION]]
                messages_list.clear()


if __name__ == '__main__':
    main()
