"""Servidor."""
# classe janela: 1 obj pra cada cliente
# vetor janelas (collections?)
#


import socket
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
        print('Incoming datagram from: ', addr[0], ':', str(addr[1]))
        print('Received %s bytes' % len(data))
        print("Data received: ", data, "\n")

        # if data:
        #     s.send("chegou carai", (udp_ip,port))

        # threading.start_new_thread(threaded_client, (addr,))

        thread = threading.Thread(target=threaded_client, args=[addr])
    s.close()


if __name__ == '__main__':
    main()