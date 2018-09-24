from hashlib import md5
import collections
import threading
import struct
import time

import binascii


class Window:
    socket = None
    log = None
    Wtx = 0
    Tout = 0
    Perror = 0
    acks = []
    sent = []
    window = None
    statistic = {'msgDistinct': 0, 'msgTransmitted': 0, 'md5Incorrect': 0}

    def __init__(self, filename, wtx, tout, perror, s):
        self.Wtx = wtx
        self.Tout = tout
        self.Perror = perror
        self.socket = s

        with open(filename, 'r') as fp:
            self.log = fp.read().splitlines()

        self.acks = [None] * len(self.log)
        self.window = collections.deque(maxlen=self.Wtx)

    def slidingWindow(self):
        lock = threading.Lock()
        thread = threading.Thread(target=self.confirmationThread)
        thread.start()

        seqNum = 0

        while True:
            if seqNum > len(self.log) - 1:
                break

            while len(self.window) > 0 and self.acks[self.window[0].num] == 1:
                teste = self.window.popleft()

            if len(self.window) < self.Wtx:
                print('enviando', seqNum)
                msg = Package(no=seqNum, msg=self.log[seqNum])
                with lock:
                    self.window.append(msg)
                    self.sent.append(msg)

                pack = msg.getLog()
                self.socket.send(pack)
                msg.setTimer(self.Tout, self.resend)

                seqNum += 1
            else:
                while self.acks[self.window[0].num] != 1:
                    pass

        thread.join()

        print('sent', self.sent)
        print('acks', self.acks)
        return

    def resend(self):
        pack = self.sent[0].getLog()
        self.socket.send(pack)
        self.sent[0].cancelTimer()
        self.sent[0].resetTimer(self.Tout, self.resend)
        print('reenviando', self.sent[0].num)

    def confirmationThread(self):
        lock = threading.Lock()

        while None in self.acks:
            msg = self.socket.get(36)

            if self.checkAck(msg) == True:
                num,_,_ = struct.unpack('!QQL', msg[:20])
                print('confirmado', num)
                with lock:
                    if self.acks[num] == None:
                        self.acks[num] = 1
                        self.sent[0].cancelTimer()
                        teste = self.sent.pop(0)
                        print('excluindo do sent', teste.num)

    def checkAck(self, pkg):
        num, sc, nanosc = struct.unpack('!QQL', pkg[:20])
        md5 = pkg[20:]

        data = Package(no=num, sec=sc, nanosec=nanosc)
        data.getPack()
        md5Tester = data.getMd5()

        if md5 == md5Tester:
            return True
        else:
            return False


class Package:
    num = 0
    seconds = 0
    nanoseconds = 0
    message = None
    md5 = None
    timer = None

    def __init__(self, no, msg=None, sec=None, nanosec=None, md5=None):
        self.num = no
        self.seconds = sec
        self.nanoseconds = nanosec
        self.message = msg
        self.md5 = md5

    def getTimestamp(self):
        ts = time.time()
        self.seconds = int(ts)
        nano = ts - self.seconds
        self.nanoseconds = int(nano * (10**9))

    def getPack(self):
        if self.message is None:
            data = struct.pack('!QQL', self.num, self.seconds, self.nanoseconds)
        else:
            msg = bytes(self.message, 'ascii')
            data = struct.pack('!QQLH', self.num, self.seconds, self.nanoseconds, len(msg))
            data += msg
        return data

    def getMd5(self):
        pkg = self.getPack();
        hash = md5(pkg).digest()
        return hash

    def getLog(self):
        self.getTimestamp()
        pkg = self.getPack()
        md5 = self.getMd5()

        data = pkg + md5
        return data

    def changeMd5(self):
        pkg = self.getLog()
        aux = int.from_bytes(pkg, 'big') + 1
        pack = bytes(aux.to_bytes(len(pkg), 'big'))
        return pack

    def setTimer(self, tout, func, a=None):
        self.timer = threading.Timer(tout, func, args=a)
        self.timer.start()

    def cancelTimer(self):
        self.timer.cancel()

    def resetTimer(self, tout, func, a=None):
        self.setTimer(tout, func, a)
