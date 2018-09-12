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
    sent = []       # salvar o pacote já enviado para reenviar sem dar pack de novo
    timeouts = []

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
                num += 1
            else:
                while self.acks[self.windowStart] != 1:
                    pass

        confirmationStop.set()
        confirmation.join()
        return

    def getTimestamp(self):
        seconds = time.time()
        current = time.time()
        nanoseconds = (current - seconds)*1000000000

        return (int(seconds), int(nanoseconds))

    def getMd5(self, no, sec, nanosec, msg=None):
        if msg == None:
            data = struct.pack('!QQL', no, sec, nanosec)
        else:
            msgLog = bytes(msg, 'utf-8')
            data = struct.pack('!QQLH%ds' % (len(msgLog)), no, sec, nanosec, len(msgLog), msgLog)

        hash = md5(data).digest()
        return hash
    
    def buildLog(self, no, msg):
        (sec, nanosec) = self.getTimestamp()
        md5 = self.getMd5(no, sec, nanosec, msg)

        msgLog = bytes(msg, 'utf-8')

        data = struct.pack('!QQLH%ds' % (len(msgLog)), no, sec, nanosec, len(msgLog), msgLog)
        print(data)
        print(md5)
        data = data + md5

        return data

    def confirmationThread(self, sock, stop, lock):
        while not stop.is_set():
            msg = sock.get(36)

            if self.checkConfirmation(msg) == True:
                with lock:
                    self.acks[int(msg)] = 1

    def splitConfirmation(self, confirmation):
        data = struct.unpack('!QQL', confirmation[0:20])

        return (data, confirmation[20:])

    def checkConfirmation(self, confirmation):
        print('ha')
        # splita confirmação
        # recalcula md5
        # confere com o que foi recebido

    def errorMd5(self):
        print('hey')

    def printStatistics(self):
        print('ha!')
