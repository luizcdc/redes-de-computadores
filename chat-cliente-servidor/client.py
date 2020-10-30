import socket
import threading
import sys
from server import binary_message_to_string, message_to_binary, NUM_BYTES, ENCODING

# AF_INET == ipv4 ------- SOCK_STREAM == TCP
socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def send_msg():
    global socket_connection
    try:
        msg = input()
        while True:
            socket_connection.sendall(message_to_binary(msg))
            msg = input()
            if(msg == 'fim'): break
    except KeyboardInterrupt:
        # TODO: fechar todas as conexões
        sys.exit()
def client():
    if (len(sys.argv) == 4):
        USERNAME = sys.argv[1]
        HOST = sys.argv[2]
        PORT = int(sys.argv[3])
        try:
            # conectando ao server
            dest = (HOST, PORT)
            socket_connection.connect(dest)
            socket_connection.sendall(message_to_binary(USERNAME))
            print("Conectado com sucesso!")
            thread_send = threading.Thread(target=send_msg, args=())
            thread_send.daemon = True
            thread_send.start()
            while True:
                msg_recebida = binary_message_to_string(socket_connection.recv(NUM_BYTES))
                if(msg_recebida):
                    print(msg_recebida)
                else:
                    raise ConnectionError('O servidor desconectou.')

        except KeyboardInterrupt:
            # TODO: fechar todas as conexões
            print('Desconectando')
            sys.exit()    
        except (ConnectionError, socket.error) as erro:
            print('ERRO:', erro)
            socket_connection.close()
        except Exception as erro:
            print('ERROR: Erro não identificado', erro)
            sys.exit()
    else:
        print('Uso: client <CLIENT_NAME> <SERVER_ADDRESS> <SERVER_PORT>')


if __name__ == "__main__":
    client()
    sys.exit()
