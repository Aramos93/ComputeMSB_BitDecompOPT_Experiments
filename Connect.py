import socket;
class Connect:
    def __init__(self):
        self.address = '127.0.0.1'
        self.lookup = {
            "p0" :8000,
            "p1" :8001,
            "p2" :8002
        }

    def sendMyType(self,sendParty,value):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.address, self.lookup.get(sendParty)))
            s.send(bytes(str(value), 'utf8'))

    def recvMyType(self,recvParty):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.address, self.lookup.get(recvParty)))
            s.listen()
            conn, addr = s.accept()
            data = conn.recv(1024)
            strings = str(data, 'utf8')
            return(int(strings))

        
