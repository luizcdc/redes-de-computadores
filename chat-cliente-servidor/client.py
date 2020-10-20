import socket
import threading
import sys

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

def client():
	if(len(sys.argv) < 4):
		print ('Uso: client_chat <CLIENT_NAME> <SERVER_ADDRESS> <SERVER_PORT>')
		sys.exit()

username = sys.argv[1]  
host = sys.argv[2]
port = int(sys.argv[3])

if __name__ == "__main__":
	sys.exit(client())
