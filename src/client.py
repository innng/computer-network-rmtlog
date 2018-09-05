import numpy as np
import struct
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

    try:
        # takes port's parameter and transforms to network byte code
        port = socket.htons(np.uint32(ipPort[1]))

        # converts string to address
        socket.inet_pton(socket.AF_INET, IP)

        # creates Socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # sets a timeout
        s.settimeout(60)

        # connects to a socket on a server's side
        # s.connect(IP)

    except socket.error as error_msg:
        logExit(error_msg[1] + ', código ' + error_msg[0])

    file = open(filename, 'r')
    log = file.read().splitlines()

    # counts messages in sequence
    counter = 0

    for msg in log:

        try:
            # sends sequence number of the log
            nSequence = struct.pack('Q', counter)
            s.send(nSequence)

            # sends timestamp


            # sends log's size


            # sends the log


            # sends error verifier code


        except socket.error as error_msg:
            logExit(error_msg[1] + ', código ' + error_msg[0])

        counter += 1

def logExit(string):
    sys.exit(string)


if __name__ == '__main__':
    main()
