import socket;
import pickle;
class Connect:
    def __init__(self):
        self.address = '127.0.0.1'
        self.lookup = {
            "p0" :8000,
            "p1" :8001,
            "p2" :8002
        }

    def sendShares(self,sendTo,value):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            pickled = pickle.dumps(value)
            s.connect((self.address, self.lookup.get(sendTo)))
            s.send(pickled)

    def recvShares(self,recvParty):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.address, self.lookup.get(recvParty)))
            s.listen()
            conn, addr = s.accept()
            data = conn.recv(1024)
            data_arr = pickle.loads(data)
            return repr(data_arr)

        
