from clientSocket import ClientSocket
from clientWindow import ClientWindow
import sys


def main():
    if len(sys.argv) < 6:
        sys.exit('Incorrect number of parameters')

    filename = sys.argv[1]
    ipPort = sys.argv[2]
    wtx = int(sys.argv[3])
    tout = int(sys.argv[4])
    perror = float(sys.argv[5])

    client = ClientSocket(ipPort)
    window = ClientWindow(filename, wtx, tout, perror)

    client.get(1024)
    window.slidingWindow(client)


if __name__ == '__main__':
    main()
