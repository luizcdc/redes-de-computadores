from socket import AF_INET, SOCK_STREAM, socket, gethostbyname, gethostname
from threading import Thread
from select import select
from sys import argv
from datetime import datetime

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

def send(connection,message):
    for(user in users_connected):
        if(user[0] != connection ):
            connection.send(message)

def send_to(connection,message):
    pass

def help_(connection):
    pass

def who(connection):
    global users_connected
    c.send("USUÁRIOS CONECTADOS:")
    for c in users_connected:
        connection.send(c[1])

def erro(connection='',message='',tipo="undisclosed"):
    pass


def thread_client(connection, address):
    """Handler para cada cliente que é executado em uma thread própria para cada um."""
    global users_connected
    nickname = connection.recv(NUM_BYTES)
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
        received = str(connection.recv(NUM_BYTES),'utf-8')
        try:
            command = received.split(maxsplit=1)[0]
            if command == "SEND":
                send(connection,received)
            elif command == "SENDTO":
                send_to(connection,received)
            elif commend == "HELP":
                help_(connection)
            elif command == "WHO":
                who(connection)
            else:
                erro(connection,message)

        except (IndexError, AttributeError):
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
                users_connected.append([connection,None])

                # TODO: cria e inicia thread desse cliente que acabou de conectar
                # thread_client.daemon = True

    except KeyboardInterrupt: # captura o CTRL+C
        # TODO: fechar todas as conexões
        quit()
