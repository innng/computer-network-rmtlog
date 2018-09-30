import clientWindow
import socket
import time
import sys


def main():
    # checa número de parâmetros
    if len(sys.argv) < 6:
        sys.exit('Incorrect number of parameters')

    # começa a contar o tempo de execução
    start = time.time()

    # recebe nome do arquivo de log
    fn = sys.argv[1]
    # recebe o IP e o porto
    hostPort = sys.argv[2]
    # recebe o tamanho da janela
    wtx = int(sys.argv[3])
    # recebe o tamanho do temporizador
    tout = int(sys.argv[4])
    # recebe a porcentagem de erro
    perror = float(sys.argv[5])

    # cria o objeto socket
    sock = ClientSocket(hostPort)
    # cria o objeto janela
    window = clientWindow.Window(fn, wtx, tout, perror, sock)
    # inicia a janela deslizante
    window.slidingWindow()
    sock.closeSocket()

    # termina de contar o tempo de execução
    end = time.time()
    elapsed = end - start
    # pega estatísticas da janela
    distMsg, sentMsg, incMd5 = window.getStats()
    print(distMsg, sentMsg, incMd5, format(elapsed, '.3f'))


# classe que instancia o socket com tratamento de erros
class ClientSocket:
    sock = None
    addr = None

    # inicia socket
    def __init__(self, hp):
        # separa IP e porto
        aux = hp.split(':')
        host = aux[0]
        port = int(aux[1])
        # salva informações em tupla
        self.addr = (host, port)

        try:
            # abre socket para comunicação via UDP
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as error_msg:
            self.logExit(error_msg)

    # envia mensagem em bytes para addr
    def send(self, data):
        try:
            self.sock.sendto(data, self.addr)
        except socket.error as error_msg:
            self.logExit(error_msg)

    # recebe um tamanho fixo de bytes
    def get(self, bytes):
        try:
            msg, address = self.sock.recvfrom(bytes)
        except socket.error as error_msg:
            self.logExit(error_msg)

        return msg

        # fecha socket
    def closeSocket(self):
        self.sock.close()

    # tratamento de erros
    def logExit(self, msg):
        self.sock.close()
        sys.exit(msg)


if __name__ == '__main__':
    main()
