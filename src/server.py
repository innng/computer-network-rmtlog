"""Servidor."""
# classe janela: 1 obj pra cada cliente
# vetor janelas (collections?)
# GRAVAR ARQUIVO
# Fazer janela
# Escrever na Doc
# GG

import socket
import struct
import sys
import threading
import hashlib
import random
import numpy

print_stuff = 1

clients = []

#d = {'5': []}

#d['5'].append(6)
#print(d['5'])


# Função de thread
def threaded_client(s, data, addr, Wrx, Perror):
    if print_stuff is 1: print("Thread created:", threading.currentThread())

    if print_stuff is 1: print('Incoming datagram from: ', addr[0], ':', str(addr[1]))
    if print_stuff is 1: print('Received %s bytes' % len(data))
    if print_stuff is 1: print("Data received: ", data)

    # Fazendo o unpacking da mensagem enviada
    # O  formato "!QQLH" é o especificado na spec do TP
    # ! = network byte order
    # Q = unsigned long long (64bits) - Numero de seq. e secs do timestamp
    # L = unsigned long (32bits)      - Nanosecs do timestamp
    # H = unsigned short (16 bits)    - Tamanho da msg

    # Lê o cabeçalho da mensagem
    msg_header = struct.unpack('!QQL', data[:20])

    # Lê o tamanho da mensagem
    msg_size = struct.unpack_from("!H", data[:22], 20)

    # Guardo o tamanho da mensagem (lido do formato H)
    msg_size = int(msg_size[0])

    # Leio a mensagem dando unpack de um offset igual ao tamanho do cabeçalho (22)
    msg = struct.unpack_from("!"+str(msg_size)+"s", data[:22+msg_size], 22)
    if print_stuff is 1: print("Message: ", msg[0].decode('ascii'))

    # Lẽ o hash md5 da mensagem
    msg_hash = struct.unpack_from("!16s", data[:22+msg_size+16], 22+msg_size)
    if print_stuff is 1: print("Hash:     ", msg_hash[0])

    test_hash = hashlib.md5(data[0:22+msg_size]).digest()
    if print_stuff is 1: print("Test Hash:", test_hash)

    # Testa se o hash enviado e o testado com o cabeçalho+msg são iguais
    if (msg_hash[0] == test_hash):
        if print_stuff is 1: print("Test passed! Both Hashes are the same!")

        # Envia o ack confirmando o recebimento da mensagem
        ack = struct.pack("!QQL", *msg_header)
        ack_hash = hashlib.md5(ack).digest()
        if print_stuff is 1: print(ack_hash)

        #Armazenas na janela deslizante


        # Gera um número aleatório entre 0 e 1 para simular erros no md5
        error_chance = random.uniform(0, 1)
        if print_stuff is 1: print("============== ERROR_CHANCE ==============", error_chance)
        if (error_chance < Perror):
            ack_hash = hashlib.md5(ack_hash).digest()
            print(ack_hash)

        # Concatena o cabeçalho com o novo hash
        ack += ack_hash
        if print_stuff is 1: print("ACK w/ hash:", ack)

        # Envia o ACK para o cliente
        s.sendto(ack, addr)

        if print_stuff is 1: print("Ack sent to client", addr[1], "\n")
    else:
        # Descartar mensagem
        if print_stuff is 1: print("Hashes are not the same, message DISCARDED!\n")


# Função principal do programa
def main():
    udp_ip = '127.0.0.1'   # Ip local
    arquivo = sys.argv[1]  # Arquivo onde salvar as msgs
    port = int(sys.argv[2])     # Porto
    Wrx = int(sys.argv[3])   # Tamanho da janela deslizante
    Perror = float(sys.argv[4])   # Porcentagem de erros a serem gerados

    # Criação do socketstruct sockaddr_in
    s = socket.socket(socket.AF_INET,        # INTERNET
                      socket.SOCK_DGRAM, 0)  # UDP
    if print_stuff is 1: print("Socket created!")

    # Bind
    s.bind((udp_ip, port))
    if print_stuff is 1: print("Socket bind done!")

    while True:
        # Esperando receber datagrama
        if print_stuff is 1: print("Waiting for datagram...")

        (data, addr) = s.recvfrom(16384)

        threading.Thread(target=threaded_client, args=(s, data, addr, Wrx, Perror)).start()


if __name__ == '__main__':
    main()