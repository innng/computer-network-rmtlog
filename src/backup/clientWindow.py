import collections
import threading
import binascii
import hashlib
import random
import struct
import time


class Window:
    statistic = None
    window = None
    perror = None
    sock = None
    acks = None
    tout = None
    log = None
    wtx = None

    def __init__(self, f, w, t, p, s):
        self.wtx = w
        self.tout = t
        self.perror = p
        self.sock = s

        with open(f, 'r') as fp:
            self.log = fp.read().splitlines()

        self.acks = [None] * len(self.log)
        self.window = collections.deque(maxlen=self.wtx)
        self.statistic = [0] * 3

    def slidingWindow(self):
        waitAck = threading.Thread(target=self.confirmationThread)
        waitAck.start()

        seqNum = 0

        while True:
            if seqNum > len(self.log) - 1:
                print('acabou')
                break

            while len(self.window) > 0 and self.acks[self.window[0].seqNum] == 1:
                teste = self.window.popleft()
                print('andou', teste.seqNum)

            if len(self.window) < self.wtx:
                print('enviou', seqNum)
                self.send(seqNum)
                seqNum += 1
            else:
                while self.acks[self.window[0].seqNum] != 1:
                    pass

        waitAck.join()

    def send(self, no):
        msg = Package(no, self.log[no])
        self.window.append(msg)

        rnd = random.random()
        if rnd < self.perror:
            print('enviando com erro', no)
            pkg = msg.changeMd5()
        else:
            pkg = msg.getLog()

        self.sock.send(pkg)
        msg.setTimer(self.tout, self.resend, [msg])

    def resend(self, msg):
        if self.acks[msg.seqNum] == 1:
            return
        print('reenviando', msg.seqNum)
        rnd = random.random()
        if rnd < self.perror:
            pkg = msg.changeMd5()
        else:
            pkg = msg.getLog()

        self.sock.send(pkg)
        msg.resetTimer(self.tout, self.resend, [msg])

    def confirmationThread(self):
        while None in self.acks:
            pkg = self.sock.get(36)

            if self.checkAck(pkg):
                num,_,_ = struct.unpack('!QQL', pkg[:20])
                print('confirmou', num)
                if self.acks[num] is None:
                    self.acks[num] = 1

    def checkAck(self, pkg):
        n, s, ns = struct.unpack('!QQL', pkg[:20])
        md5 = pkg[20:]

        data = Package(no=n, s=s, n=ns)
        data.getPack()
        md5Tester = data.getMd5()

        if md5 == md5Tester:
            return True
        else:
            return False

class Package:
    seqNum = 0
    seconds = 0
    nanoseconds = 0
    message = None
    md5 = None
    timer = None

    def __init__(self, no, msg=None, s=None, n=None, m=None):
        self.seqNum = no
        self.seconds = s
        self.nanoseconds = n
        self.message = msg
        self.md5 = m

    def getTimestamp(self):
        ts = time.time()
        self.seconds = int(ts)
        nano = ts - self.seconds
        self.nanoseconds = int(nano * (10**9))

    def getPack(self):
        if self.message is None:
            data = struct.pack('!QQL', self.seqNum, self.seconds, self.nanoseconds)
        else:
            msg = bytes(self.message, 'ascii')
            data = struct.pack('!QQLH', self.seqNum, self.seconds, self.nanoseconds, len(msg))
            data += msg
        return data

    def getMd5(self):
        pkg = self.getPack();
        hash = hashlib.md5(pkg).digest()
        return hash

    def getLog(self):
        self.getTimestamp()
        pkg = self.getPack()
        md5 = self.getMd5()

        data = pkg + md5
        return data

    def changeMd5(self):
        pkg = self.getLog()

        try:
            aux = int.from_bytes(pkg, 'big') + 1
            pack = bytes(aux.to_bytes(len(pkg), 'big'))
        except OverflowError:
            pack = pkg

        return pack

    def setTimer(self, tout, func, a=None):
        self.timer = threading.Timer(tout, func, args=a)
        self.timer.start()

    def resetTimer(self, tout, func, a=None):
        self.setTimer(tout, func, a)