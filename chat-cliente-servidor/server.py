from socket import AF_INET, SOCK_STREAM, socket, gethostbyname, gethostname
from threading import Thread
from select import select
from sys import argv

NUM_BYTES = 2000
users_connected = []

def socket_available():
    available = select([server_socket],[],[],0.25)[0]
    return available[0][0] if available else None

def remove_connection(connection):
    global users_connected

    users_connected = [x for x in users_connected if x[0] != connection]
    connection.shutdown()
    connection.close()
    return


def thread_client(connection, address):
    global users_connected

    # caso o nome de usuario estiver em uso, desconecta, exclui a conexão
    # da lista users_connected e retorna
    # senão, registra o nome de usuário com a conexão na lista users_connected
    nickname = connection.recv(NUM_BYTES)
    if (nickname in (c[1] for c in users_connected)) or (' ' in nickname):
        print("ERRO: falha na conexão com o cliente, o nome de usuário "
              "já está em uso.")
        remove_connection(connection)
        return
    else:
        for x in users_connected:
            if x[0] == connection:
                x[1] = nickname
                break

    while True:
        command = connection.recv(NUM_BYTES)
        # chama a função que executa o comando
        pass



if __name__ == "__main__":
    try:
        PORT_NUM = argv[1]
        server_socket = socket(AF_INET,SOCK_STREAM)
        server_socket.bind((gethostbyname(gethostname()),int(PORT_NUM)))
        server_socket.listen(127)


        while True:
            if socket_available():
                connection, address = server_socket.accept()
                users_connected.append([connection,None])
                # cria e inicia thread desse cliente que acabou de conectar
                # thread_client.daemon = True
    except KeyboardInterrupt:
        # fecha todas as conexões
        quit()
