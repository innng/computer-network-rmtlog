import clientWindow
import socket
import time
import sys

def main():
    if len(sys.argv) < 6:
        sys.exit('Incorrect number of parameters')

    fn = sys.argv[1]
    hostPort = sys.argv[2]
    wtx = int(sys.argv[3])
    tout = int(sys.argv[4])
    perror = float(sys.argv[5])

    start = time.time()

    s = ClientSocket(hostPort)
    window = clientWindow.Window(fn, wtx, tout, perror)
    window.slidingWindow(s)

    end = time.time()
    elapsed = end - start
    print(elapsed)


class ClientSocket:
    sock = None
    addr = None

    def __init__(self, hp):
        aux = hp.split(':')
        host = aux[0]
        port = int(aux[1])
        self.addr = (host, port)

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as error_msg:
            self.logExit(error_msg)

    def send(self, data):
        try:
            self.sock.sendto(data, self.addr)
        except socket.error as error_msg:
            self.logExit(error_msg)

    def get(self, bytes):
        try:
            msg, address = self.sock.recvfrom(bytes)
        except socket.error as error_msg:
            self.logExit(error_msg)

        return msg

    def closeSocket(self):
        self.sock.close()

    def logExit(self, msg):
        self.sock.close()
        sys.exit(msg)


if __name__ == '__main__':
    main()
