import socket
import sys


class ClientSocket:
    sock = None

    def __init__(self, ipPort):
        aux = ipPort.split(':')
        host = aux[0]
        port = int(aux[1])

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.sock.connect((host, port))

        except socket.error as error_msg:
            self.logExit(error_msg)

    def send(self, data):
        try:
            self.sock.send(data)

        except socket.error as error_msg:
            self.logExit(error_msg)

    def get(self, bytes):
        try:
            msg = self.sock.recv(bytes)
        except socket.error as error_msg:
            self.logExit(error_msg)

        return msg

    def closeSocket(self):
        self.sock.close()

    def logExit(self, msg):
        self.sock.close()
        sys.exit(msg)
