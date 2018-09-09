import socket
import struct
import sys
from time import sleep

# create a socket object
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
# host = socket.gethostname()
host = ''

port = int(sys.argv[1])

# bind to the port
serversocket.bind((host, port))

# queue up to 5 requests
serversocket.listen(5)

while True:
	# establish a connection
	clientsocket,addr = serversocket.accept()

	print("Got a connection from %s" % str(addr))

	msg = 'Thank you for connecting'+ "\r\n"
	clientsocket.send(msg.encode('ascii'))

	for i in range(0, 200):
		# msg1 = clientsocket.recv(1024)
		# print (msg1)

		msg2 = str(i)
		clientsocket.send(msg2.encode('ascii'))
		sleep(5)

	clientsocket.close()
