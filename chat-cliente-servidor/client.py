import socket
import threading
import sys
from server import binary_message_to_string, message_to_binary

# definir aqui funções a serem utilizadas

# abrir o socket a ser utilizado

# conectar o socket ao servidor
# (se falhar imprimir mensagem de erro idêntica a que tá na especificação do trabalho)

# enviar o nome do cliente para o servidor
# (se o servidor rejeitar pq já existe, imprimir mensagem de erro como na especificação)

# AO MESMO TEMPO (threads)
# 1 - ler o comando que o usuário está digitando e enviar quando ele apertar enter
# 1.1 - CASO USUÁRIO APERTE CTRL+C, PRIMEIRO FECHA A CONEXÃO, IMPRIME "Conexão encerrada." E SAIR DO PROGRAMA. (usar try except, a exceção é KeyboardInterrupt)
# 2 - imprimir qualquer mensagem que o servidor enviar para esse cliente

# AF_INET == ipv4 ------- SOCK_STREAM == TCP

# conectando ao server

def client():
    if (len(sys.argv) == 4):
        USERNAME = sys.argv[1]
        HOST = sys.argv[2]
        PORT = int(sys.argv[3])

        try:
            socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dest = (HOST, PORT)
            socket_connection.connect(dest)
            print("Conectado com sucesso!")
            msg = input()
            socket_connection.sendall(message_to_binary(USERNAME))
            while msg != '\3': # \x18 = captura do control + x do terminal. \3 => control + c
                socket_connection.sendall(message_to_binary(msg))
                msg = input()
        except KeyboardInterrupt:  # captura o CTRL+C
            # TODO: fechar todas as conexões
            sys.exit()
        except Exception:
            print("Falha na conexão")
            socket_connection.close()

    else:
        print('Uso: client <CLIENT_NAME> <SERVER_ADDRESS> <SERVER_PORT>')


if __name__ == "__main__":
    try:
        client()
    except:
        pass
    sys.exit()
