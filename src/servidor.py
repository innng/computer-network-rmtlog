"""Servidor."""

import socket
import sys
from thread import *
import hashlib
import numpy
# print (hashlib.md5(b'teste').hexdigest())
# arquivo port Wrx Perror

print_stuff = 1

host = ''              # Nome simbólico significando todas as interfaces disp.
arquivo = sys.argv[1]  # Arquivo onde salvar as msgs
port = sys.argv[2]     # Port
Wrx = sys.argv[3]      # Window size
Perror = sys.argv[4]   # Porcentagem de erros a serem gerados

# Criação do socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if print_stuff == 1:
    print("Socket created!")

# Bind
try:
    s.bind((host, port))
except socket.error as error_msg:
    print("Bind failed. Error: "+str(error_msg[0]) + " - " + error_msg[1])
    sys.exit()
if print_stuff == 1:
    print("Socket bind done!")

# Início da escuta
s.listen(10)
if print_stuff == 1:
    print("Socket listening...")


# Função que irá  ligar com as conexões e será usada para a criação de threads
def threaded_client(conn):
    u"""Função Thread dos clientes."""
    # Envia uma mensagem de boas vindas (temporário)
    conn.send(str.encode("You are connected to our server, welcome!\n"))

    while True:
        # Recebendo dados do cliente

        # Configurar o resto que tem que receber
        # !!!!

        data = conn.recv(2048)
        reply = 'Server: ' + data.decode('utf-8')
        if not data:
            break
        conn.sendall(str.encode(reply))

    conn.close()


while True:
    # Esperando receber alguma conexão
    conn, addr = s.accept()
    print ('Connected to: ' + addr[0] + ':' + str(addr[1]))

    start_new_thread(threaded_client, (conn,))

s.close()
