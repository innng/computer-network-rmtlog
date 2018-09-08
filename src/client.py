import numpy as np
import threading
import hashlib
import struct
import socket
import time
import sys


# takes input in argv
filename = sys.argv[1]
ipPort = tuple(sys.argv[2].split(':'))
Wtx = int(sys.argv[3])
Tout = int(sys.argv[4])
Perror = float(sys.argv[5])


def main():
    # tests number of arguments
    if len(sys.argv) < 6:
        logExit('Incorrect number of parameters')

    host = ipPort[0]
    port = int(ipPort[1])

    # extracts logs from file and get the timestamp in seconds and nanoseconds
    with open(filename, 'r') as fp:
        log = fp.read().splitlines()

    try:
        # creates socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # tries to stablish connection to the server
        sock.connect((host, port))

        # Receive no more than 1024 bytes
        msg = sock.recv(1024)
        print (msg.decode('ascii'))

    except socket.error as error:
        logExit(sock, error)

    slidingWindow(log, sock)

    sock.close()


def slidingWindow(log, sock):
    noLog = 0
    ws = 0
    we = Wtx - 1
    acks = [None] * len(log)
    timeout = [None] * len(log)

    for msg in log:
        if we > len(log) - 1:
            break

        if noLog >= ws and noLog <= we:
            data = buildLog(noLog, msg)
            sendLog(data, sock)
            noLog += 1
            timeout[noLog] = threading.Timer(Tout, sendLog, args=[data, sock])

        while acks[ws] != 1:
            pass

        if acks[ws] == 1:
            ws += 1
            we += 1


def sendLog(log, sock):
    try:
        sock.send(log)
    except socket.error as error:
        logExit(sock, error)


def receiveConfirmation(sock, acks, no):
    try:
        data = sock.recv(36)
    except socket.error as error:
        logExit(sock, error)

def buildLog(no, msg):
    (sec, nanosec) = getTimestamp()
    sz = len(msg)
    hash = getMd5(no, sec, nanosec, sz, msg)

    noLog = np.uint64(socket.htonl(no))
    seconds = np.uint64(socket.htonl(sec))
    nanoseconds = np.uint32(socket.htonl(nanosec))
    size = np.uint16(socket.htonl(sz))
    logMsg = bytes(msg, 'utf-8')
    md5 = bytes(hash, 'utf-8')

    data = struct.pack('QQLH%ds%ds' % (len(msg), len(md5),), noLog, seconds, nanoseconds, size, logMsg, md5)

    return data


def getTimestamp():
    seconds = int(time.time())
    ts = time.time()
    nanoseconds = int((ts - seconds)*1000000000)
    return (seconds, nanoseconds)


def getMd5(noLog, seconds, nanoseconds, sizeMsg, msg):
    data = bytes(str(noLog) + str(seconds) + str(nanoseconds) + str(sizeMsg) + msg, 'utf-8')
    hash = hashlib.md5(data).hexdigest()
    return hash


def logExit(sock, msg):
    sock.close()
    sys.exit(msg)


if __name__ == '__main__':
    main()
