import random
import socket
import pickle
from ast import literal_eval
import threading
import time

##################################################### Globals ########################################################
L = 4
file1 = "shares0.txt"
file2 = "shares1.txt"

######################################################################################################################


########################################## MyType (Convert number to ZL or ZL-1) #####################################
class MyType:
    def __init__(self, x, is_zl = True): #if True --> Zl else --> ZL-1
        self.L = L
        self.is_zl = is_zl
        if self.is_zl:
            self.x = x % (2 ** self.L)
        else:
            self.x = x % ((2 ** self.L) - 1)

######################################################################################################################

########################################### Process (Create p0, p1, p2) ##############################################

class Process:
    def __init__(self, partyName):
        # Connection Initialization
        self.address = '127.0.0.1'
        self.lookup = {
            "p0" :8000,
            "p1" :8001,
            "p2" :8002
        }

        # Process shares initialization
        if partyName > 2 or partyName < 0:
            raise Exception("PartyName must be 0, 1, or 2")
        self.party = "p"+str(partyName)
        self.shares = []
        if partyName == 0:
            self.readFile(file1)
        elif partyName == 1:
            self.readFile(file2)


    
    def readFile(self, filename):
        f = open(filename,"r")
        for line in f:
            self.shares.append(int(line.strip()))

    # def sendInt(self,sendTo,value):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.connect((self.address, self.lookup.get(sendTo)))
    #         s.send(bytes(str(value), 'utf8'))

    # def recvInt(self,recvParty):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.bind((self.address, self.lookup.get(recvParty)))
    #         s.listen()
    #         conn, addr = s.accept()
    #         data = conn.recv(1024)
    #         strings = str(data, 'utf8')
    #         return(int(strings))
    
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
    
    def reconstruct2PC(self):
        if self.party == "p1":
            self.sendShares("p0",self.shares)
        if self.party == "p0":
            p1_shares = literal_eval(self.recvShares(self.party))
            reconstructed = [MyType(sum(e)).x for e in zip(self.shares, p1_shares)]
            print("Reconstructed: ", reconstructed)
        
        




        
    


    
    # def convertToZlMinusOne(self, toZL = False ):
    #     self.shares = [MyType(e, toZL).x for e in self.shares]
        
######################################################################################################################    




####################################################### Tests ########################################################
def test_MyType():
    testListInput = [8,20,16,0,-3]
    testListRes = []
    for e in testListInput:
        testListRes.append(MyType(e).x)

    for x in testListRes:
        print(x)


def test_Process():
    p0 = Process(0)
    print("p0 shares: ", p0.shares)
    p1 = Process(1)
    print("p1 shares: ", p1.shares)
    p2 = Process(2)
    print("p2 shares (empty): ", p2.shares)

def test_reconstruct2PC():
    p0 = Process(0)
    p1 = Process(1)
    thread1 = threading.Thread(target=p0.reconstruct2PC, args=())
    thread1.start()
    thread2 = threading.Thread(target=p1.reconstruct2PC, args=())
    thread2.start()
   


def test_ConvertTo3PShares():
    print("implement this")


    
test_reconstruct2PC()
#test_MyType()