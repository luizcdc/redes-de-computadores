from socket import AF_INET, SOCK_STREAM, socket, gethostbyname, gethostname
from threading import Thread
from select import select
from sys import argv

NUM_BYTES = 4096 # ???????

def socket_available():
    available = select([server_socket],[],[],0.25)[0]
    return available[0][0] if available else None

def thread_client(connection, address):
    # recebe primeiro comando (o nome de usuario)
    # caso o nome de usuario estiver em uso, desconecta e exclui da lista users_connected e retorna
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

        users_connected = []

        while True:
            if socket_available():
                connection, address = server_socket.accept()
                users_connected.append(connection)
                # cria e inicia thread desse cliente que acabou de conectar
                # thread_client.daemon = True
    except KeyboardInterrupt:
        # fecha todas as conexões
        quit()
