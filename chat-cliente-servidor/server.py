import threading
from socket import AF_INET, SOCK_STREAM, socket, gethostbyname, gethostname
from threading import Thread
from select import select
from sys import argv
from datetime import datetime

ENCODING = 'utf-8'
NUM_BYTES = 2000
users_connected = []

# definir as funções que executam cada comando suportado pelo servidor

def socket_available():
    """Retorna se o socket do servidor tem nova(s) conexões pendentes."""
    global server_socket

    available = select([server_socket],[],[],0.25)[0]
    return True if available else False

def remove_connection(connection):
    """Remove uma conexão da lista users_connected e a encerra."""
    global users_connected

    users_connected = [x for x in users_connected if x[0] != connection]
    connection.shutdown()
    connection.close()
    return

def binary_message_to_string(message):
    """Reconverte a mensagem recebida de binário para string."""
    message = str(message, ENCODING)
    return message.split('\0',maxsplit=1)[0]

def message_to_binary(message):
    """Converte a mensagem para binário.
    Caso a mensagem seja muito grande, trunca a mensagem para NUM_BYTES bytes.
    caso seja muito pequena, insere '\0' no fim da mensagem até seu tamanho
    ser igual a NUM_BYTES.
    """
    size_message = len(bytes(message,ENCODING))
    if size_message > NUM_BYTES:
        # TODO : CHAMAR erro() para sinalizar que a mensagem é muito grande
        message = message[:NUM_BYTES]
        size_message = len(bytes(message,ENCODING))
        while (size_message > 2000):
            # necessário pois alguns caracteres utf-8 têm mais que 1 byte.
            message = message[:-1]
            size_message = len(bytes(message,ENCODING))

    message += "\0" * (NUM_BYTES - size_message)

    return bytes(message,ENCODING)

def send(connection, nickname, message):
    global users_connected
    executed = "Não"
    for user in users_connected:
        if user[0] != connection:
            executed = "Sim"
            try:
                connection.sendall(message_to_binary(f"{nickname}: {message}"))
            except Exception:
                executed = "Não"
    messageserver = (datetime.now().strftime("%H:%M ") + nickname +  " SEND Executado: " + executed)
    print(messageserver)

def send_to(connection, sender_nickname, message):
    global users_connected
    message = message.split(' ',maxplit=1)
    if len(message != 2):
        erro()
        # TODO: chamar erro() para sinalizar que o comando não recebeu os
        # argumentos corretos
    else:
        # filter retorna uma lista com a entrada [socket,nickname] do usuário
        # destino em users_connected, ou uma lista vazia se não existir esse
        # usuário. Nesse último caso, envia mensagem de erro de volta para
        # o cliente.
        dest_nick = message[0]
        # TODO: adicionar horário e nome do remetente à mensagem
        dest_socket = list(filter(lambda u: u[1] == dest_nick, users_connected))
        if dest_socket:
            dest_socket[0][0].sendall(message_to_binary(message[1]))
        else:
            pass
            # TODO: chamar erro() para sinalizar que o usuário especificado
            # não está conectado ao servidor


def help_(connection):
    help_message =  ("COMANDOS SUPORTADOS:\n"
                    "HELP -> listar os comandos suportados\n"
                    "WHO -> exibir uma lista dos usuários conectados.\n"
                    "SEND <MESSAGE>-> enviar uma mensagem para todos os usuários.\n"
                    "SENDTO <CLIENT_NAME> <MESSAGE>\n\n"
                    "Pressione CTRL+C a qualquer momento para encerrar a "
                    "conexão com o servidor e fechar o cliente de chat.\n")
    help_message = message_to_binary(help_message)
    connection.sendall(help_message)


def who(connection):
    global users_connected
    connection.send("USUÁRIOS CONECTADOS:")
    for c in users_connected:
        c.send(c[1])

def erro(connection='',message='',tipo="undisclosed"):
    pass


def thread_client(connection, address):
    """Handler para cada cliente que é executado em uma thread própria para cada um."""
    global users_connected
    nickname = binary_message_to_string(connection.recv(NUM_BYTES))
    if (nickname in (c[1] for c in users_connected)) or (' ' in nickname):
        # caso o nome de usuario estiver em uso, desconecta, exclui a conexão
        # da lista users_connected e retorna
        print("ERRO: falha na conexão com o cliente, o nome de usuário "
              "já está em uso.")
        remove_connection(connection)
        return
    else:
        # senão, registra o nome de usuário com a conexão na lista users_connected
        for x in users_connected:
            if x[0] == connection:
                x[1] = nickname
                break
        # print(datetime.now().strftime("%H:%M\tAndré Conectado"))
    while True:
        try:
            received = str(connection.recv(NUM_BYTES),ENCODING)
            command, message = received.split(maxsplit=1)
            if command == "SEND":
                send(connection, nickname, message)
            elif command == "SENDTO":
                send_to(connection,nickname, message)
            elif command == "HELP":
                help_(connection)
            elif command == "WHO":
                who(connection)
            else:
                erro(connection,message)

        except (IndexError, AttributeError, ValueError):
            # um socket só retorna com 0 bytes se a conexão está quebrada.
            erro(connection,message,tipo="mensagem vazia")
            print(f"TODO: HORÁRIO{nickname} desconectado.")
            return

if __name__ == "__main__":
    try:
        # cria um socket servidor na porta passada como argumento do programa
        # com o máximo de 127 conexões pendentes
        PORT_NUM = argv[1]
        server_socket = socket(AF_INET,SOCK_STREAM)
        server_socket.bind((gethostbyname(gethostname()),int(PORT_NUM)))
        server_socket.listen(127)
        while True:
            if socket_available():
                connection, address = server_socket.accept()
                users_connected.append([connection,''])
                thread_user = threading.Thread(target=thread_client, args=(connection, address))
                thread_user.daemon = True
                thread_user.start()
                # TODO: cria e inicia thread desse cliente que acabou de conectar
                # thread_client.daemon = True

    except KeyboardInterrupt: # captura o CTRL+C
        # TODO: fechar todas as conexões
        quit()
