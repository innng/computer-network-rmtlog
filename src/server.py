"""Servidor."""
# classe janela: 1 obj pra cada cliente
# vetor janelas (collections?)
#


import socket
import socketserver
import sys
import threading
import hashlib
import numpy
import socketserver

# print (hashlib.md5(b'teste').hexdigest())
# arquivo port Wrx Perror

print_stuff = 1

clients = []

#d = {'5': []}

#d['5'].append(6)
#print(d['5'])


# class ThreadedServer(object):
#     def __init__(self, host, port):
#         self.host = host
#         self.port = port
#         self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#         # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         self.sock.bind((self.host, self.port))
#
#     def WaitDatagram(self):
#
#         while True:
#             # Esperando receber datagrama
#             if print_stuff == 1:
#                 print("Waiting for datagram...")
#
#             (data, addr) = self.sock.recvfrom(16384)
#             print("Data received: ", data, "\n")
#             print('Incoming datagram from: ', addr[0], ':', str(addr[1]))
#             print('Received %s bytes' % len(data))
#
#             threading.Thread(target=self.threaded_client, args=(data, addr)).start()

# Função de thread
def threaded_client(s, data, addr):
    # while True:
        # Recebendo dados do cliente

        # Configurar o resto que tem que receber
        # !!!!
        # s.sendto(data, (addr,))
        print(threading.currentThread())


# Função principal do programa
def main():
    udp_ip = '127.0.0.1'   # Ip local
    arquivo = sys.argv[1]  # Arquivo onde salvar as msgs
    port = sys.argv[2]     # Porto
    Wrx = sys.argv[3]      # Tamanho da janela deslizante
    Perror = sys.argv[4]   # Porcentagem de erros a serem gerados

    # Criação do socketstruct sockaddr_in
    s = socket.socket(socket.AF_INET,        # INTERNET
                      socket.SOCK_DGRAM, 0)  # UDP
    if print_stuff == 1:
        print("Socket created!")

    # Bind
    s.bind((udp_ip, int(port)))
    if print_stuff == 1:
        print("Socket bind done!")

    while True:
        # Esperando receber datagrama
        if print_stuff == 1:
            print("Waiting for datagram...")

        (data, addr) = s.recvfrom(16384)
        print("Data received: ", data, "\n")
        print('Incoming datagram from: ', addr[0], ':', str(addr[1]))
        print('Received %s bytes' % len(data))

        threading.Thread(target=threaded_client, args=(s, data, addr)).start()

    # ThreadedServer(udp_ip, port).WaitDatagram()


if __name__ == '__main__':
    main()