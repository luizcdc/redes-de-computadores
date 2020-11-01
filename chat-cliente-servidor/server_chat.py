import threading
from socket import AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR
from socket import socket, gethostbyname, gethostname
from threading import Thread
from select import select
from sys import argv, exit, version_info
from datetime import datetime

ENCODING = "utf-8"
quitting_program = False
NUM_BYTES = 1999
users_connected = []
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# definir as funções que executam cada comando suportado pelo servidor

def time_string():
    """Retorna uma string com o horário atual."""

    return datetime.now().strftime("%H:%M")

def socket_available(socket_):
    """Retorna se um socket específico tem dados pendentes para leitura
    ou conexões pendentes para serem aceitas.
    """

    available = select([socket_], [], [], 0.5)[0]
    return True if available else False

def close_all_connections():
    """Encerra todas as conexões, inclusive o socket servidor."""
    
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
    except OSError:
        # caso a conexão já esteja inválida/fechada
        pass

def binary_message_to_string(message):
    """Reconverte a mensagem recebida de binário para string."""

    message = str(message, ENCODING)
    return message.split("\0", maxsplit=1)[0]

def message_to_binary(message):
    """Converte a mensagem para binário.
    
    Caso a mensagem seja muito grande, encurta a mensagem para NUM_BYTES bytes.
    caso seja muito pequena, insere "\0" no fim da mensagem até seu tamanho
    ser igual a NUM_BYTES.
    """

    size_message = len(bytes(message, ENCODING))
    if size_message > NUM_BYTES:
        message = message[:NUM_BYTES]
        size_message = len(bytes(message, ENCODING))
        while (size_message > NUM_BYTES):
            # necessário pois alguns caracteres utf-8 têm mais que 1 byte.
            message = message[:-1]
            size_message = len(bytes(message, ENCODING))

    message += "\0" * (NUM_BYTES - size_message)

    return bytes(message, ENCODING)


def send(connection, username, message):
    """Envia a mensagem para todos os usuários conectados, menos o remetente.
    
    Caso um dos usuários conectados não receba a mensagem, é marcado que a ope-
    ração não teve sucesso, porém tenta enviar para todos os outros mesmo assim.

    Caso a mensagem a enviar esteja vazia, também registra que a operação não
    teve sucesso e envia uma mensagem de erro para o cliente.
    """

    global users_connected

    message = message.split(maxsplit=1)
    if len(message) == 2:
        executed = "Sim"
        message = message[1]
        count_sent = 0
        for user in users_connected:
            if user[0] != connection:
                try:
                    user[0].sendall(message_to_binary(
                        f"{username}: {message}"))
                    count_sent += 1
                except OSError:
                    pass
        if count_sent == 0 and len(users_connected) > 1:
            executed = "Não"
            erro(connection=connection, tipo="SEND_FAILURE")
            # chama erro() para sinalizar que não conseguiu enviar a mensagem
            # para nenhum usuário conectado (quando o remetente não é o único)
    else:
        executed = "Não"
        erro(connection=connection, tipo="EMPTY_SEND")
        # chama erro() para sinalizar que o comando foi invocado sem uma
        # mensagem a enviar

    messageserver = (time_string() + "\t" +
                     username + "\tSEND\tExecutado: " + executed)
    print(messageserver)


def send_to(connection, sender_username, message):
    """Envia a mensagem para o usuário especificado.
    
    Duas possibilidades de falha: argumentos incorretos ou destinatário inexis-
    tente.
    """

    global users_connected
    message = message.split(maxsplit=2)
    if len(message) != 3:
        executed = "Não"
        erro(connection=connection,tipo="SENDTO_INVALID_ARGS")
        # chama erro() para sinalizar que o comando não recebeu os
        # argumentos corretos
    else:
        # filter retorna uma lista com a entrada [socket, username] do usuário
        # destino em users_connected, ou uma lista vazia se não existir esse
        # usuário. Nesse último caso, envia mensagem de erro de volta para
        # o cliente.
        dest_user = message[1]
        executed = "Sim"
        dest_socket = list(
            filter(lambda u: u[1] == dest_user, users_connected))
        if dest_socket:
            try:
                dest_socket[0][0].sendall(message_to_binary(
                    f"{sender_username}: " + message[2]))
            except OSError:
                executed = "Não"
                erro(connection=connection,tipo="SENDTO_BROKEN_CONNECTION",dest_user=sender_username)
        else:
            executed = "Não"
            erro(connection=connection,tipo="SENDTO_INVALID_DEST",dest_user=sender_username)
    messageserver = (time_string() + "\t" +
                     sender_username + "\tSENDTO\tExecutado: " + executed)
    print(messageserver)

def commands_help(connection, sender_username):
    """Envia a mensagem de ajuda para o usuário que a solicitou."""

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
    except OSError:
        executed = "Não"
        erro(connection=connection,tipo="RESPONSE_INTERRUPTED")
    messageserver = (time_string() + "\t" +
                        sender_username + "\tHELP\tExecutado: " + executed)
    print(messageserver)

def who(connection, sender_username):
    """Gera uma lista de todos os usuários conectados e a envia para o usuário que a solicitou."""

    global users_connected
    who_message = "USUARIOS CONECTADOS:"
    for c in users_connected:
        who_message += "\n" + c[1]
    who_message += "\n"
    try:
        connection.sendall(message_to_binary(who_message))
        executed = "Sim"
    except OSError:
        executed = "Não"
        erro(connection=connection, tipo="RESPONSE_INTERRUPTED")

    messageserver = (time_string() + "\t" +
                     sender_username + "\tWHO\tExecutado: " + executed)
    print(messageserver)


def erro(connection=None, username = "", message="", tipo="undisclosed", **kwargs):
    """Função responsável pelo tratamento de erros."""

    if tipo == "INVALID_COMMAND":
        try:
            connection.sendall(message_to_binary(
                f"ERRO: {kwargs['command']} não é um comando válido."))
        except OSError:
            pass
    elif tipo == "EMPTY_SEND":
        try:
            connection.sendall(message_to_binary(
                f"ERRO: SEND requer uma mensagem como argumento."))
        except OSError:
            pass
    elif tipo == "SEND_FAILURE":
        err_msg = "ERRO: SEND não conseguiu enviar a mensagem para nenhum outro usuário conectado."
        print(err_msg)
        try:
            connection.sendall(message_to_binary(err_msg))
        except OSError:
            pass
    elif tipo == "SENDTO_INVALID_ARGS":
        try:
            connection.sendall(message_to_binary(
                f"ERRO: SENDTO requer um usuário destino e uma mensagem como argumentos"))
        except OSError:
            pass
    elif tipo == "SENDTO_INVALID_DEST":
        try:
            connection.sendall(message_to_binary(
                f"ERRO: usuário {kwargs['dest_user']} não está conectado ao servidor."))
        except OSError:
            pass
    elif tipo == "SENDTO_BROKEN_CONNECTION":
        # TODO: eliminar a conexão quebrada
        try:
            connection.sendall(message_to_binary(
                f"ERRO: a conexão com {kwargs['dest_user']} foi encerrada e a mensagem não foi entregue."))
        except OSError:
            pass
    elif tipo == "RESPONSE_INTERRUPTED":
        print("ERRO: ao tentar enviar a resposta do comando do usuário, a conexão foi perdida.")
        remove_connection(connection)
    elif tipo == "USERNAME_ALREADY_USED":
        print(f"ERRO: falha no registro do cliente {kwargs['address']}, o " +
              f"nome de usuário {username} já está em uso.")
        try:
            connection.sendall(message_to_binary(f"ERRO: O usuário {username} já " +
                                                 "está registrado no servidor."))
        except OSError:
            pass
        remove_connection(connection)
    elif tipo == "NO_ARGS":
        print("Uso: python3 server_chat.py <PORT>")
    else:
        print("ERRO: um erro não especificado ocorreu.")
        
def thread_client(connection, address):
    """Handler para cada cliente, que é executado em uma thread própria para cada um."""

    global users_connected
    try:
        username = binary_message_to_string(connection.recv(NUM_BYTES))
        if (username in (c[1] for c in users_connected)) or (" " in username):
            # caso o nome de usuario estiver em uso, desconecta, exclui a conexão
            # da lista users_connected e retorna
            print(f"ERRO: falha na conexão com o cliente em {address}, o nome " +
                f"de usuário {username} já está em uso.")
            erro(connection=connection,tipo="USERNAME_ALREADY_USED",username=username,address=address)
            return
        else:
            # senão, registra o nome de usuário com a conexão na lista users_connected
            for x in users_connected:
                if x[0] == connection:
                    x[1] = username
                    break
            connection.sendall(message_to_binary(f"Conectado com Sucesso"))
            print(time_string() + "\t" +username+"\tConectado")
        while True:
            while not socket_available(connection):
                # evita que a thread bloqueie tentando receber do socket,
                # o que permite que se feche a conexão sem causar uma exceção 
                pass
            received = binary_message_to_string(connection.recv(NUM_BYTES))
            command = received.split(maxsplit=1)[0]
            if command == "SEND":
                send(connection, username, received)
            elif command == "SENDTO":
                send_to(connection, username, received)
            elif received == "HELP":
                commands_help(connection, username)
            elif command == "WHO":
                who(connection, username)
            else:
                erro(connection=connection,tipo="INVALID_COMMAND",username=username,command=command)

    except (IndexError, AttributeError, ValueError, OSError, ConnectionError):
        # um socket só retorna com 0 bytes se a conexão está quebrada.
        remove_connection(connection)
        if not quitting_program:
            print(f"{time_string()}\t{username}\tDesconectado.")
        return

if __name__ == "__main__":
    if len(argv) < 2:
        erro(tipo="NO_ARGS")
    elif version_info < (3, 8):
        print("Esse programa exige o python 3.8 ou mais recente para ser executado.")
    else:
        try:
            # cria um socket servidor na porta passada como argumento do programa
            # com o máximo de 127 conexões pendentes
            PORT_NUM = int(argv[1])
            HOST_IP = (gethostbyname(gethostname()) if len(argv) == 2 else "127.0.0.1")
            server_socket.bind((HOST_IP, PORT_NUM))
            server_socket.listen(127)
            print(f"Servidor inicializado e disponível em {HOST_IP}:{PORT_NUM}\n" +
                "Aguardando novas conexões.")
            while True:
                if socket_available(server_socket):
                    connection, address = server_socket.accept()
                    users_connected.append([connection, ""]) 

                    thread_user = threading.Thread(
                        target=thread_client, args=(connection, address))
                    thread_user.daemon = True
                    thread_user.start()

        except KeyboardInterrupt:  # captura o CTRL+C
            print("Encerrando o servidor e desconectando todos os usuários.")
            quitting_program = True
            close_all_connections()
            exit()
