from hashlib import md5
import numpy as np
import threading
import struct
import socket
import time
import sys


class ClientWindow:
    log = None
    wtx = 0
    tout = 0
    perror = 0.0
    windowStart = 0
    windowEnd = 0
    acks = []
    sent = []       # salvar o pacote já enviado para reenviar

    def __init__(self, filename, wtx, tout, perror):
        with open(filename, 'r') as fp:
            self.log = fp.read().splitlines()

        self.wtx = wtx
        self.tout = tout
        self.perror = perror

    def slidingWindow(self, sock):
        num = 0
        self.windowStart = 0
        self.windowEnd = self.wtx - 1
        self.acks = [None] * len(self.log)
        self.sent = []

        lock = threading.Lock()
        confirmationStop = threading.Event()
        confirmation = threading.Thread(target=self.confirmationThread, args=[sock, confirmationStop, lock])
        confirmation.start()

        while True:
            if num > len(self.log) - 1:
                break

            while self.acks[self.windowStart] == 1:
                self.windowStart += 1
                self.windowEnd += 1

            if num >= self.windowStart and num <= self.windowEnd:
                msg = self.log[num]
                data = self.buildLog(num, msg)
                sock.send(data)
                self.sent.append(threading.Timer(self.tout, sock.send, args=data))
                num += 1
            else:
                while self.acks[self.windowStart] != 1:
                    pass

        confirmationStop.set()
        confirmation.join()
        return

    def getTimestamp(self):
        ts = time.time()
        seconds = int(ts)
        sub = ts - seconds
        nanoseconds = int(sub*(10**9))

        return (seconds, nanoseconds)

    def getMd5(self, package):
        hash = md5(package).digest()
        return hash

    def buildPack(self, no, sec, nanosec, msg=None):
        if msg is None:
            data = struct.pack('!QQL', no, sec, nanosec)
        else:
            msg1 = bytes(msg, 'ascii')
            data = struct.pack('!QQLH', no, sec, nanosec, len(msg1))
            data += msg1

        return data

    def buildLog(self, no, msg):
        (sec, nanosec) = self.getTimestamp()
        data = self.buildPack(no, sec, nanosec, msg)
        md5 = self.getMd5(data)

        log = data + md5
        return log

    def confirmationThread(self, sock, stop, lock):
        while not stop.is_set():
            msg = sock.get(36)

            if self.checkConfirmation(msg) == True:
                with lock:
                    self.acks[int(msg)] = 1

    def checkConfirmation(self, confirmation):
        data = struct.unpack('!QQL', confirmation[0:20])
        md5 = confirmation[20:]

        package = self.buildPack(*data)
        md5Tester = self.getMd5(package)
        if md5 == md5Tester:
            return True
        else:
            return False

    def errorMd5(self, package):
        aux = int.from_bytes(package, 'big') + 1
        pack = bytes(aux.to_bytes(len(package), 'big'))

        return pack

    def printStatistics(self):
        print('ha!')
