"""Servidor."""

import socket
import sys
from threading import Thread
import hashlib
import numpy
import socketserver

# print (hashlib.md5(b'teste').hexdigest())
# arquivo port Wrx Perror

print_stuff = 1

UDP_IP = '127.0.0.1'   # Ip local
arquivo = sys.argv[1]  # Arquivo onde salvar as msgs
port = sys.argv[2]     # Port
Wrx = sys.argv[3]      # Window size
Perror = sys.argv[4]   # Porcentagem de erros a serem gerados

# Criação do socketstruct sockaddr_in
s = socket.socket(socket.AF_INET,        # INTERNET
                  socket.SOCK_DGRAM, 0)  # UDP
if print_stuff == 1:
    print("Socket created!")

# Bind
try:
    s.bind((UDP_IP, port))
except socket.error as error_msg:
    print("Bind failed. Error: "+str(error_msg[0]) + " - " + error_msg[1])
    sys.exit()
if print_stuff == 1:
    print("Socket bind done!")


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
    data, addr = s.recvfrom(4096)
    print ('Connected to: ' + addr[0] + ':' + str(addr[1]))

    Thread.start_new_thread(threaded_client, (data,))

s.close()
