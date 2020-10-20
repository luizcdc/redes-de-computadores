from socket import AF_INET, SOCK_STREAM, socket, gethostbyname, gethostname
from threading import Thread
import sys

NUM_BYTES = 4096 # ???????

def thread_client(connection, address):
    # recebe primeiro comando (o nome de usuario)
    # caso o nome de usuario estiver em uso, desconecta e exclui da lista users_connected e retorna
    while True:
        command = connection.recv(NUM_BYTES)
        # chama a função que executa o comando
        pass



if name == "__main__":

    try:
        server_socket = socket(AF_INET,SOCK_STREAM)
        server_socket.bind(gethostbyname(gethostname()),sys.argv[2]) # tomara que funcione
        server_socket.listen() # descobrir melhor numero para esse argumento
        users_connected = []
        while True:
            connection, address = server_socket.accept()
            # coloca a conexão na lista de conexões
            # cria e inicia thread desse cliente que acabou de conectar    # .daemon = True
    except KeyboardInterrupt:
        # fecha todas as conexões
        exit()
