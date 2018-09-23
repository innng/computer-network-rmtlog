"""Servidor."""
# classe janela: 1 obj pra cada cliente
# vetor janelas (collections?)
#


import socket
import struct
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
    print("Thread created:", threading.currentThread())

    print('Incoming datagram from: ', addr[0], ':', str(addr[1]))
    print('Received %s bytes' % len(data))
    print("Data received: ", data)

    # Fazendo o unpacking da mensagem enviada
    # O  formato "!QQLH" é o especificado na spec do TP
    # Q = unsigned long long (64bits) - Numero de seq. e secs do timestamp
    # L = unsigned long (32bits)      - Nanosecs do timestamp
    # H = unsigned short (16 bits)    - Tamanho da msg

    msg_header = struct.unpack('!QQLH', data[:22])

    # Guardo o tamanho da mensagem (lido do formato H)

    msg_size = int(msg_header[3])

    # Leio a mensagem dando unpack de um offset igual ao tamanho do cabeçalho (22)

    msg = struct.unpack_from("!"+str(msg_size)+"s", data[:22+msg_size], 22)
    print("Message: ", msg[0])

    msg_hash = struct.unpack_from("!16s", data[:22+msg_size+16], 22+msg_size)
    print("Hash:     ", msg_hash[0])

    test_hash = hashlib.md5(data[0:22+msg_size]).digest()
    print("Test Hash:", test_hash)

    # Testa se o hash enviado e o testado com o cabeçalho e msg são iguais
    if (msg_hash[0] == test_hash):
        print("Test passed! Both Hashes are the same!")
    else:
        # Descartar mensagem
        print("Hashes are not the same, message DISCARDED!")


    # s.sendto(data, (addr,))
    print("\n")


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

        threading.Thread(target=threaded_client, args=(s, data, addr)).start()

    # ThreadedServer(udp_ip, port).WaitDatagram()


if __name__ == '__main__':
    main()