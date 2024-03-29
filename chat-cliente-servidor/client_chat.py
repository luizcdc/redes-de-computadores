import socket
import threading
import sys
from server_chat import binary_message_to_string, message_to_binary, NUM_BYTES, ENCODING

# AF_INET == ipv4 ------- SOCK_STREAM == TCP
try:
    socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as erro:
    print ("ERRO: Não foi possível criar o socket.")
    sys.exit()

def send_msg():
    global socket_connection
    try:
        msg = input()
        while True:
            if msg:
                if len(bytes(msg,ENCODING)) > NUM_BYTES:
                    print("ERRO: mensagem é muito grande e será encurtada "
                          "para " + str(NUM_BYTES) + " bytes antes de ser " +
                          "enviada.")
                socket_connection.sendall(message_to_binary(msg))
            msg = input()
    except (KeyboardInterrupt,OSError,EOFError):
        # a outra thread já fecha as conexões
        exit()
    finally:
        # esse bloco que encerra a conexão sempre é executado
        # independentemente do que está no "try" ou em qualquer "except",
        # até mesmo caso a função dê "return"
        try:
            socket_connection.shutdown(socket.SHUT_RDWR)
            socket_connection.close()
        except OSError:
            # caso a conexão já esteja fechada/inválida
            pass

def client():
    global socket_connection
    if (len(sys.argv) == 4):
        USERNAME = sys.argv[1]
        HOST = sys.argv[2]
        PORT = int(sys.argv[3])
            # conectando ao server
        dest = (HOST, PORT)
        try:
            socket_connection.connect(dest)
        except ConnectionError:
            print("ERRO: não foi possível conectar ao servidor.")
            return
        try:
            socket_connection.sendall(message_to_binary(USERNAME))
            thread_send = threading.Thread(target=send_msg, args=())
            thread_send.daemon = True
            thread_send.start()
            while True:
                # loop que executa na thread principal cuja função é receber e
                # imprimir as mensagens transmitidas pelo servidor.
                msg_recebida = binary_message_to_string(socket_connection.recv(NUM_BYTES))
                if(msg_recebida):
                    print(msg_recebida)
                else:
                    raise ConnectionError('O servidor desconectou.')

        except KeyboardInterrupt:
            print('Desconectando.')
            return
        except (ConnectionError, OSError) as erro:
            print('ERRO: O servidor desconectou.')
            return
        except Exception as erro:
            print(f'ERRO: Erro não identificado {type(erro).__name__} -> {erro}.')
            return
        finally:
            # esse bloco que encerra a conexão sempre é executado
            # independentemente do que está no "try" ou em qualquer "except",
            # até mesmo caso a função dê "return"
            try:
                socket_connection.shutdown(socket.SHUT_RDWR)
                socket_connection.close()
            except OSError:
                # caso a conexão já esteja fechada/inválida
                pass

    else:
        print('Uso: python3 client_chat.py <CLIENT_NAME> <SERVER_ADDRESS> <SERVER_PORT>')


if __name__ == "__main__":
    if sys.version_info < (3,8):
        print("Esse programa exige o python 3.8 ou mais recente para ser executado.")
    else:
        client()
    sys.exit()
