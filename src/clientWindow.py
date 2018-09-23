from hashlib import md5
import collections
import threading
import struct
import time

import binascii


class Window:
    log = None
    Wtx = 0
    Tout = 0
    Perror = 0
    acks = []
    sent = []
    statistic = {'msgDistinct': 0, 'msgTransmitted': 0, 'md5Incorrect': 0}

    def __init__(self, filename, wtx, tout, perror):
        self.Wtx = wtx
        self.Tout = tout
        self.Perror = perror

        with open(filename, 'r') as fp:
            self.log = fp.read().splitlines()

    def slidingWindow(self, sock):
        self.acks = [None] * len(self.log)
        window = collections.deque(maxlen=self.Wtx)

        stopEvt = threading.Event()
        thread = threading.Thread(target=self.confirmationThread, args=[sock, stopEvt])
        thread.start()

        seqNum = 0

        while True:

            if seqNum > len(self.log) - 1:
                break

            while len(window) > 0 and self.acks[window[0].num] == 1:
                teste = window.popleft()
                print('eba', teste.num)

            if len(window) < self.Wtx:
                print('num', seqNum)
                msg = Package(no=seqNum, msg=self.log[seqNum])
                window.append(msg)
                pack = msg.getLog()
                sock.send(pack)
                seqNum += 1
            else:
                while self.acks[window[0].num] != 1:
                    pass

        stopEvt.set()
        thread.join()
        return

    def confirmationThread(self, sock, stopEvt):
        lock = threading.Lock()

        while not stopEvt.is_set():
            msg = sock.get(36)

            if self.checkAck(msg) == True:
                print('aaaaaaa')
                num,_,_ = struct.unpack('!QQL', msg[:20])
                with lock:
                    self.acks[num] = 1

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
