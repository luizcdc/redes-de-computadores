import threading
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
from socket import socket, gethostbyname, gethostname
from threading import Thread
from select import select
from sys import argv, exit
from datetime import datetime

ENCODING = 'utf-8'
quitting_program = False
NUM_BYTES = 2000
users_connected = []
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# definir as funções que executam cada comando suportado pelo servidor

def time_string():
    return datetime.now().strftime("%H:%M")

def socket_available(socket_):
    """Retorna se um socket específico tem dados pendentes para leitura
    ou conexões pendentes para serem aceitas.
    """
    available = select([socket_], [], [], 0.5)[0]
    return True if available else False

def close_all_connections():
    global users_connected, server_socket
    for c in users_connected:
        try:
            c[0].shutdown(SHUT_RDWR)
        except OSError:
            pass
        c[0].close()
    users_connected = []
    try:
        server_socket.shutdown(SHUT_RDWR)
        server_socket.close()
    except OSError:
        pass

def remove_connection(connection):
    """Remove uma conexão da lista users_connected e a encerra."""
    global users_connected

    users_connected = [x for x in users_connected if x[0] != connection]
    try:
        connection.shutdown(SHUT_RDWR)
        connection.close()
    except Exception:
        # caso a conexão já esteja inválida/fechada
        pass

def binary_message_to_string(message):
    """Reconverte a mensagem recebida de binário para string."""
    message = str(message, ENCODING)
    return message.split('\0', maxsplit=1)[0]

def message_to_binary(message):
    """Converte a mensagem para binário.
    
    Caso a mensagem seja muito grande, encurta a mensagem para NUM_BYTES bytes.
    caso seja muito pequena, insere '\0' no fim da mensagem até seu tamanho
    ser igual a NUM_BYTES.
    """
    size_message = len(bytes(message, ENCODING))
    if size_message > NUM_BYTES:
        message = message[:NUM_BYTES]
        size_message = len(bytes(message, ENCODING))
        while (size_message > 2000):
            # necessário pois alguns caracteres utf-8 têm mais que 1 byte.
            message = message[:-1]
            size_message = len(bytes(message, ENCODING))

    message += "\0" * (NUM_BYTES - size_message)

    return bytes(message, ENCODING)


def send(connection, nickname, message):
    global users_connected

    message = message.split(maxsplit=1)
    if len(message) == 2:
        executed = "Sim"
        message = message[1]
        for user in users_connected:
            if user[0] != connection:
                try:
                    user[0].sendall(message_to_binary(
                        f"{nickname}: {message}"))
                except Exception:
                    executed = "Não"
    else:
        erro(connection)
        executed = "Não"
        # TODO: CHAMAR erro() PARA SINALIZAR QUE SEND NÃO RECEBEU COMO
        # ARGUMENTO A MENSAGEM

    messageserver = (time_string() + '\t' +
                     nickname + "\tSEND\tExecutado:\t" + executed)
    print(messageserver)


def send_to(connection, sender_nickname, message):
    global users_connected
    message = message.split(maxsplit=2)
    if len(message) != 3:
        erro(connection)
        executed = "Não"
        # TODO: chamar erro() para sinalizar que o comando não recebeu os
        # argumentos corretos
    else:
        # filter retorna uma lista com a entrada [socket, nickname] do usuário
        # destino em users_connected, ou uma lista vazia se não existir esse
        # usuário. Nesse último caso, envia mensagem de erro de volta para
        # o cliente.
        dest_nick = message[1]
        executed = "Sim"
        dest_socket = list(
            filter(lambda u: u[1] == dest_nick, users_connected))
        if dest_socket:
            try:
                dest_socket[0][0].sendall(message_to_binary(
                    f"{sender_nickname}:" + message[2]))
            except Exception:
                executed = "Não"
        else:
            executed = "Não"
            erro(connection, f"Usuário {dest_nick} não está conectado ao servidor.")
            # TODO: chamar erro() para sinalizar para o usuario que sendto falhou
    messageserver = (time_string() + '\t' +
    sender_nickname + "\tSENDTO\tExecutado:\t" + executed)
    print(messageserver)

def commands_help(connection, sender_nickname):
    help_message = ("COMANDOS SUPORTADOS:\n"
                    "HELP -> listar os comandos suportados\n"
                    "WHO -> exibir uma lista dos usuários conectados.\n"
                    "SEND <MESSAGE> -> enviar uma mensagem para todos os usuários.\n"
                    "SENDTO <CLIENT_NAME> <MESSAGE> -> enviar uma mensagem para somente um usuário.\n\n"
                    "Mensagens com mais de " + str(NUM_BYTES) + " bytes serão encurtadas para esse comprimento máximo.\n"
                    "Pressione CTRL+C a qualquer momento para encerrar a "
                    "conexão com o servidor e fechar o cliente de chat.\n")
    try:
       connection.sendall(message_to_binary(help_message))
       executed = "Sim"
    except Exception:
        executed = "Não"
    messageserver = (time_string() + '\t' +
                        sender_nickname + "\tHELP\tExecutado:\t" + executed)
    print(messageserver)

def who(connection, sender_nickname):
    global users_connected
    who_message = "USUARIOS CONECTADOS:"
    for c in users_connected:
        who_message += '\n' + c[1]
    who_message += '\n'
    try:
        connection.sendall(message_to_binary(who_message))
        executed = "Sim"
    except Exception:
        executed = "Não"
    messageserver = (time_string() + '\t' +
                     sender_nickname + "\tWHO\tExecutado:\t" + executed)
    print(messageserver)


def erro(connection='', message='Um erro desconhecido ocorreu.', tipo="undisclosed"):
    try:
        connection.sendall(message_to_binary(message))
    except Exception:
        pass

def thread_client(connection, address):
    """Handler para cada cliente que é executado em uma thread própria para cada um."""
    global users_connected
    nickname = binary_message_to_string(connection.recv(NUM_BYTES))
    if (nickname in (c[1] for c in users_connected)) or (' ' in nickname):
        # caso o nome de usuario estiver em uso, desconecta, exclui a conexão
        # da lista users_connected e retorna
        print(f"ERRO: falha na conexão com o cliente em {address}, o nome " +
              f"de usuário {nickname} já está em uso.")
        connection.sendall(message_to_binary(f"ERRO: O usuário {nickname} já " +
                                             "está registrado no servidor."))
        remove_connection(connection)
        return
    else:
        # senão, registra o nome de usuário com a conexão na lista users_connected
        for x in users_connected:
            if x[0] == connection:
                x[1] = nickname
                break
        print(time_string() + '\t' +nickname+"\tConectado")
    while True:
        try:
            while not socket_available(connection):
                # evita que a thread bloqueie tentando receber do socket,
                # o que permite que se feche a conexão sem causar uma exceção 
                pass
            received = binary_message_to_string(connection.recv(NUM_BYTES))
            command = str(received.split(maxsplit=1)[0])
            if command == "SEND":
                send(connection, nickname, received)
            elif command == "SENDTO":
                send_to(connection, nickname, received)
            elif received == "HELP":
                commands_help(connection, nickname)
            elif command == "WHO":
                who(connection, nickname)
            else:
                erro(connection, received+" não é um comando válido.")

        except (IndexError, AttributeError, ValueError, OSError, ConnectionError):
            # um socket só retorna com 0 bytes se a conexão está quebrada.
            remove_connection(connection)
            if not quitting_program:
                print(f"{time_string()}\t{nickname}\tDesconectado.")
            return

if __name__ == "__main__":
    if len(argv) < 2:
        print("Uso: python3 server_chat.py <PORT>")
    else:
        try:
            # cria um socket servidor na porta passada como argumento do programa
            # com o máximo de 127 conexões pendentes
            PORT_NUM = int(argv[1])
            HOST_IP = gethostbyname(gethostname())
            server_socket.bind((HOST_IP, PORT_NUM))
            server_socket.listen(127)
            print(f"Servidor inicializado e disponível em {HOST_IP}:{PORT_NUM}\n" +
                "Aguardando novas conexões.")
            while True:
                if socket_available(server_socket):
                    connection, address = server_socket.accept()
                    users_connected.append([connection, '']) 

                    thread_user = threading.Thread(
                        target=thread_client, args=(connection, address))
                    thread_user.daemon = True
                    thread_user.start()

        except KeyboardInterrupt:  # captura o CTRL+C
            print("Encerrando o servidor e desconectando todos os usuários.")
            quitting_program = True
            close_all_connections()
            exit()
