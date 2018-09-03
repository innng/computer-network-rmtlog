import numpy as np
import socket
import sys

def main():
    if len(sys.argv) < 6:
        logExit('Incorrect number of parameters!')

    # parameters passed by arguments
    filename = sys.argv[1]
    ipPort = tuple(sys.argv[2].split(':'))
    Wtx = int(sys.argv[3])
    Tout = int(sys.argv[4])
    Perror = float(sys.argv[5])
    IP = ipPort[0]
    port = socket.htons(np.uint32(ipPort[1]))

    # counts messages in sequence
    counter = 0

    try:
        # converts string to address
        socket.inet_pton(socket.AF_INET, IP)

        # sets a timeout
        socket.settimeout(60)

        # creates Socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connects to a socket on a server's side
        socket.connect(IP)

        # 

    except socket.error as error_msg:
        logExit(error_msg[1] + ", código " + error_msg[0])



def logExit(string):
    sys.exit(string)


if __name__ == '__main__':
    main()
