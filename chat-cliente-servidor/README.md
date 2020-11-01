# Chat Cliente Servidor

## Equipe **Diamante G3**

### Professor: **Paul Denis Etienne Regnier**

### Disciplina: **MATA59 - Redes de Computadores**

<br>

| Componentes                       | E-mail                   |
| --------------------------------- | ------------------------ |
| Alberto Lucas da Trindade Neto    | alberto.trindade@ufba.br |
| Andre Luiz dos Santos Gomes Filho | andreluizsgf@gmail.com   |
| Artur Oscar Silva Santos Junior   | artur.junior@ufba.br     |
| Cainan Lima Alves                 | cainan.lima@ufba.br      |
| Luiz Cláudio Dantas Cavalcanti    | luizcdc@ufba.br          |

<br>

## Manual de Instruções

### Informações Gerais

- Projeto em python, para executar é necessário a versão do python 3.8 ou mais recente.

### Servidor

1. python3 server.py <**PORT**>

- Onde o parâmetro **PORT** é a porta na qual será conectado
- Opcional: para testar o servidor localmente com o endereço de IP de loopback 
(127.0.0.1), basta invocar o programa com mais que um argumento, desde que o 
primeiro argumento seja ainda a porta de rede a ser utilizada.

### Cliente

1. python3 client.py <**CLIENT_NAME**> <**SERVER_ADRESS**> <**SERVER_PORT**>

- Onde os parâmetros **CLIENT_NAME**, serve para indicar o nome do cliente que está se conectando, **SERVER_ADRESS** para indicar o endereço do servidor, **SERVER_PORT** para indicar a porta de conexão.
