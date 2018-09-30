import collections
import threading
import binascii
import hashlib
import random
import struct
import time


# classe que instancia um objeto janela
class Window:
    # guarda as estatísticas
    stats = None
    # janela deslizante
    window = None
    # porcentagem de erro
    perror = None
    # socket do cliente para comunicação UDP
    sock = None
    # vetor de confirmação das mensagens de log
    acks = None
    # tamanho do temporizador
    tout = None
    # vetor com as mensagens de log extraídas do arquivo
    log = None
    # tamanho da janela deslizante
    wtx = None

    # preparações para a janela
    def __init__(self, f, w, t, p, s):
        self.wtx = w
        self.tout = t
        self.perror = p
        self.sock = s

        # extraí as mensagens de log do arquivo
        with open(f, 'r') as fp:
            self.log = fp.read().splitlines()

        # inicializa o vetor de confirmações com o número de mensagens de log
        self.acks = [None] * len(self.log)
        # inicializa a janela com seu tamanho máximo fixo
        self.window = collections.deque(maxlen=self.wtx)
        # inicializa o dicionário com estatísticas a serem coletadas
        # distMsg: no mensagens distintas
        # sentMsg: no mensagens enviadas
        # incMd5: no mensagens com md5 incorreto
        self.stats = {'distMsg': len(self.log), 'sentMsg': 0, 'incMd5': 0}

    # executa o processo de envio de mensagens através da janela
    def slidingWindow(self):
        # cria thread que ficará responsável por receber acks de confirmação e
        # marcar seu recebimento no vetor de confirmação
        waitAck = threading.Thread(target=self.confirmationThread)
        waitAck.start()

        # número da mensagem de log
        seqNum = 0

        while True:
            # checa se todas as mensagens foram enviadas
            if seqNum > len(self.log) - 1:
                print('acabou')
                break

            # envia as mensagens de log enquanto:
            # 1. ainda houver mensagens,
            # 2. a janela tiver espaço disponível,
            # 3. o pacote no início da janela já foi confirmado
            while seqNum < len(self.log) and (len(self.window) < self.wtx or self.acks[self.window[0].seqNum] == 1):

                self.send(seqNum)
                seqNum += 1

        # termina execução da janela e de sua thread
        waitAck.join()

    # envia a mensagem de log pela primeira vez
    def send(self, no):
        # cria o objeto mensagem
        msg = Package(no, self.log[no])
        # adiciona o objeto à janela deslizante
        self.window.append(msg)
        self.stats['sentMsg'] += 1

        # cálcula número aleatório
        rnd = random.random()
        # se o número é menor que o perror, envia md5 errado
        if rnd < self.perror:
            print('enviou com erro', no)
            self.stats['incMd5'] += 1
            pkg = msg.changeMd5()

        else:
            print('enviou', no)
            pkg = msg.getLog()

        # envia mensagem de log e inicializa o temporizador
        self.sock.send(pkg)
        msg.setTimer(self.tout, self.resend, [msg])

    # faz o reenvio da mensagem de log
    def resend(self, msg):
        # se a mensagem já foi confirmada, ignora o temporizador
        if self.acks[msg.seqNum] == 1:
            return

        self.stats['sentMsg'] += 1

        # cálcula número aleatório
        rnd = random.random()
        # se o número é menor que o perror, reenvia com md5 errado
        if rnd < self.perror:
            print('reenviou com erro', msg.seqNum)
            self.stats['incMd5'] += 1
            pkg = msg.changeMd5()
        else:
            print('reenviou', msg.seqNum)
            pkg = msg.getLog()

        # reenvia mensagem de log e reseta o temporizador
        self.sock.send(pkg)
        msg.resetTimer(self.tout, self.resend, [msg])

    # método executado pela thread
    def confirmationThread(self):
        # inicializa lock para impedir condições de corrida
        lock = threading.Lock()

        # enquanto há mensagens não confirmadas
        while None in self.acks:
            # recebe pacote
            pkg = self.sock.get(36)

            # checa md5
            if self.checkAck(pkg):
                # extraí o número da mensagem que foi confirmada
                num,_,_ = struct.unpack('!QQL', pkg[:20])
                print('confirmou', num)
                # se ainda não houve confirmação
                if self.acks[num] is None:
                    with lock:
                        self.acks[num] = 1

    # checa md5 recebido no pacote de confirmação
    def checkAck(self, pkg):
        # extraí informações
        n, s, ns = struct.unpack('!QQL', pkg[:20])
        md5 = pkg[20:]

        # monta pacote temporário
        data = Package(no=n, s=s, n=ns)
        data.getPack()
        # calcula md5
        md5Tester = data.getMd5()

        # compara os md5
        if md5 == md5Tester:
            return True
        else:
            return False

    # método que retorna as estatísticas calculadas na execução da janela
    def getStats(self):
        return (self.stats['distMsg'], self.stats['sentMsg'], self.stats['incMd5'])

# classe que monta uma mensagem de log
class Package:
    # número de sequência
    seqNum = 0
    # segundos do timestamp
    seconds = 0
    # nanosegundos desde o segundo
    nanoseconds = 0
    # mensagem de log
    message = None
    # hash md5
    md5 = None
    # temporizador da mensagem
    timer = None

    # inicializa a mensagem
    def __init__(self, no, msg=None, s=None, n=None, m=None):
        self.seqNum = no
        self.seconds = s
        self.nanoseconds = n
        self.message = msg
        self.md5 = m

    # pega o timestamp da mensagem
    def getTimestamp(self):
        ts = time.time()
        self.seconds = int(ts)
        nano = ts - self.seconds
        self.nanoseconds = int(nano * (10**9))

    # monta pacote (sem md5)
    def getPack(self):
        # dois pacotes são possíveis:
        # sem mensagem de log (servidor -> cliente)
        if self.message is None:
            data = struct.pack('!QQL', self.seqNum, self.seconds, self.nanoseconds)
        # com mensagem de log (cliente -> servidor)
        else:
            msg = bytes(self.message, 'ascii')
            data = struct.pack('!QQLH', self.seqNum, self.seconds, self.nanoseconds, len(msg))
            data += msg
        return data

    # calcula md5
    def getMd5(self):
        pkg = self.getPack();
        hash = hashlib.md5(pkg).digest()
        return hash

    # monta o pacote completo a ser enviado para o servidor
    def getLog(self):
        self.getTimestamp()
        pkg = self.getPack()
        md5 = self.getMd5()

        data = pkg + md5
        return data

    # torna o md5 errado somando 1 ao pacote inteiro em bytes
    def changeMd5(self):
        pkg = self.getLog()

        try:
            # passa bytes -> inteiro e soma 1
            aux = int.from_bytes(pkg, 'big') + 1
            # passa inteiro -> bytes
            pack = bytes(aux.to_bytes(len(pkg), 'big'))
        except OverflowError:
            pack = pkg

        return pack

    # inicia o temporizador
    def setTimer(self, tout, func, a=None):
        self.timer = threading.Timer(tout, func, args=a)
        self.timer.start()

    # reinicia o temporizador
    def resetTimer(self, tout, func, a=None):
        self.timer.cancel()
        self.setTimer(tout, func, a)
