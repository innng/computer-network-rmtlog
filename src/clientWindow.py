from hashlib import md5
import numpy as np
import threading
import struct
import socket
import time


class ClientWindow:
    log = None
    wtx = 0
    tout = 0
    perror = 0.0
    windowStart = 0
    windowEnd = 0
    acks = []
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

        confirmationStop = threading.Event()
        confirmation = threading.Thread(target=self.confirmationThread, args=[sock, confirmationStop])
        confirmation.start()


        while True:
            if num > len(self.log) - 1:
                break
            elif num >= self.windowStart and num <= self.windowEnd:
                msg = self.log[num]
                print(self.windowStart, self.windowEnd, num)
                print(msg)
                data = self.buildLog(num, msg)
                sock.send(data)
                num += 1
            else:
                if self.acks[self.windowStart] == 1:
                    print('andou')
                    self.windowStart += 1
                    self.windowEnd += 1

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
            data = bytes(str(no) + str(sec) + str(nanosec), 'utf-8')
        else:
            data = bytes(str(no) + str(sec) + str(nanosec) + str(len(msg)) +  msg, 'utf-8')

        hash = md5(data).hexdigest()
        return hash

    def buildLog(self, no, msg):
        (sec, nanosec) = self.getTimestamp()
        hash = self.getMd5(no, sec, nanosec, msg)

        seq = np.uint64(socket.htonl(no))
        seconds = np.uint64(socket.htonl(sec))
        nanoseconds = np.uint32(socket.htonl(nanosec))
        size = np.uint16(socket.htonl(len(msg)))
        msgLog = bytes(msg, 'utf-8')
        md5 = bytes(hash, 'utf-8')

        data = struct.pack('QQLH%ds%ds' % (len(msg), len(md5)), seq, seconds, nanoseconds, size, msgLog, md5)

        return data

    def confirmationThread(self, sock, stop):
        while not stop.is_set():
            msg = sock.get()
            print ('aeeee', msg.decode('ascii'))

            self.acks[int(msg)] = 1
