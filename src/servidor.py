import hashlib
import random
import socket
import struct
import random
import time

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 5000))

for i in range(0, 200):
    message, address = server_socket.recvfrom(1024)
    data = struct.unpack('!QQL', message[:20])

    data2 = struct.pack("!QQL", *data)
    hash = hashlib.md5(data2).digest()
    data2 += hash
    print(data[0])

    if message is not None:
        rnd = random.random()

        if rnd < 0.5:
            time.sleep(6)
        server_socket.sendto(data2, address)
        print('confirmando', data[0])

# message, address = server_socket.recvfrom(1024)
# print(message.decode('ascii'))
# server_socket.sendto(message, address)
