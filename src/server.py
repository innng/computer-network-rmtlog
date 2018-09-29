"""Servidor."""

# Escrever na Doc
# GG

import socket
import struct
import sys
import hashlib
import random
import operator
import time

print_stuff = 1

window = {
    # 'id: [pacote1, pacote2, ...]
}


class Package:
    seqNum = None
    msg = None

    def __init__(self, seqnum, msg) -> None:
        self.seqNum = seqnum
        self.msg = msg


def dump_window_to_file(clientID, output_file):
    # Escreve as mensagens da janela no arquivo de saída
    for i in range(0, len(window[clientID])):
        output_file.write(window[clientID][i].msg + '\n')
        output_file.flush()

    # Esvazia a janela
    window[clientID].clear()


def add_to_window(clientID, package):
    # Testa se o cliente ja tem uma janela
    if clientID in [x for x in window]:
        # Adiciona o pacote na janela do cliente
        window[clientID].append(package)

    # Cliente não existe, da um update no dicionario e adiciona o cliente
    # depois, adiciona a mensagem
    else:
        window.update({clientID: []})
        window[clientID].append(package)

    # Ordena os pacotes dentro da janela do cliente
    window[clientID].sort(key=operator.attrgetter('seqNum'))
    # print(window[clientID][0].msg)


# Função que testa o pacote
def check_package(s, data, addr, Wrx, Perror, output_file):
    if print_stuff is 1: print('Incoming datagram from: ', addr[0], ':', str(addr[1]))
    if print_stuff is 1: print('Received %s bytes' % len(data))
    # if print_stuff is 1: print("Data received: ", data)

    # Lê o cabeçalho da mensagem
    msg_header = struct.unpack('!QQL', data[:20])

    # Lê o tamanho da mensagem
    msg_size = struct.unpack_from("!H", data[:22], 20)

    # Guardo o tamanho da mensagem (lido do formato H)
    msg_size = int(msg_size[0])

    # Leio a mensagem dando unpack de um offset igual ao tamanho do cabeçalho (22)
    msg = struct.unpack_from("!"+str(msg_size)+"s", data[:22+msg_size], 22)

    # Lẽ o hash md5 da mensagem
    msg_hash = struct.unpack_from("!16s", data[:22+msg_size+16], 22+msg_size)

    test_hash = hashlib.md5(data[0:22+msg_size]).digest()

    clientID = addr[1]
    messageSeqnum = msg_header[0]
    clientMessage = msg[0].decode('ascii')

    # Testa se o cliente ja tem uma janela
    if clientID not in [x for x in window]:
        # Cliente não existe, da um update no dicionario e adiciona o cliente
        window.update({clientID: []})

    # Testa se a janela está cheia, se sim, imprima seu conteúdo no arquivo e esvazia a janela
    if len(window[clientID]) == Wrx:
        dump_window_to_file(clientID, output_file)

    # Testa se o hash enviado e o testado com o cabeçalho+msg são iguais
    if (msg_hash[0] == test_hash):
        # Test passed! Both Hashes are the same!

        # Seqnum do pacote é menor que o primeiro seqnum na janela + o tamanho
        # da janela ou a janela está vazia, ou seja, ele cabe na janela
        if len(window[clientID]) == 0 or messageSeqnum < (window[clientID][0].seqNum + Wrx):
            # Monto o pacote
            package = Package(messageSeqnum, clientMessage)
            # Armazena na janela deslizante
            add_to_window(clientID, package)

            # Monta o ACK para confirmar o recebimento
            ack = struct.pack("!QQL", *msg_header)
            ack_hash = hashlib.md5(ack).digest()

            # Gera um número aleatório entre 0 e 1 para simular erros no md5
            error_chance = random.uniform(0, 1)

            # Se precisar gerar um erro, faça um hash com o hash (erro)
            if error_chance < Perror:
                ack_hash = hashlib.md5(ack_hash).digest()

            # Concatena o cabeçalho com o novo hash
            ack += ack_hash

            # Envia o ack confirmando o recebimento da mensagem
            s.sendto(ack, addr)

        # Pacote recebido tem seqnum menor que o primeiro da janela
        # então é só confirmar
        elif messageSeqnum < window[clientID][0].seqNum:
            # Envia o ack confirmand: o o recebimento da mensagem
            ack = struct.pack("!QQL", *msg_header)
            ack_hash = hashlib.md5(ack).digest()

            # Gera um número aleatório entre 0 e 1 para simular erros no md5
            error_chance = random.uniform(0, 1)

            # Gera erro no hash se necessário
            if error_chance < Perror:
                ack_hash = hashlib.md5(ack_hash).digest()

            # Concatena o cabeçalho com o novo hash
            ack += ack_hash

            # Envia o ACK para o cliente
            s.sendto(ack, addr)
    else:
        # Descartar mensagem
        if print_stuff is 1: print("Hashes are not the same, message DISCARDED!\n")


# Função principal do programa
def main():
    udp_ip = '127.0.0.1'         # Ip local
    arquivo = sys.argv[1]        # Arquivo onde salvar as msgs
    port = int(sys.argv[2])      # Porto
    Wrx = int(sys.argv[3])       # Tamanho da janela deslizante
    Perror = float(sys.argv[4])  # Porcentagem de erros a serem gerados

    print("Server writing to", arquivo)
    print("Wrx =", Wrx, "probError =", Perror)

    # Abre o arquivo de saída
    output_file = open(arquivo, "w")

    # Criação do socketstruct sockaddr_in
    s = socket.socket(socket.AF_INET,        # INTERNET
                      socket.SOCK_DGRAM, 0)  # UDP

    # Bind
    s.bind((udp_ip, port))

    while True:
        # Esperando receber datagrama
        print("Esperando datagrama...")
        (data, addr) = s.recvfrom(16422)


        check_package(s, data, addr, Wrx, Perror, output_file)
        #threading.Thread(target=check_package, args=(s, data, addr, Wrx, Perror, output_file)).start()


if __name__ == '__main__':
    main()