import random
import socket
import pickle
import time 
from ast import literal_eval
import threading
import time

##################################################### Globals ########################################################
L = 4
p = 11
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
    
    def __add__(self, other):
        return MyType(self.x + other.x % (2**self.L))
    
    def __sub__(self, other):
        return MyType(self.x - other.x % (2**self.L))

######################################################################################################################

########################################### Party (Create p0, p1, p2) ##############################################

class Party:
    #### Initialize Party ######
    def __init__(self, partyName):
        # Connection Initialization
        self.address = '127.0.0.1'
        self.lookup = {
            "p0" :8000,
            "p1" :8001,
            "p2" :8002
        }

        # Party shares initialization
        if partyName > 2 or partyName < 0:
            raise Exception("PartyName must be 0, 1, or 2")
        self.party = "p"+str(partyName)
        self.shares = []
        if partyName == 0:
            self.readFile(file1)
        elif partyName == 1:
            self.readFile(file2)

    # Get actual values of shares from MyType's
    def getShareVals(self):
        return [e.x for e in self.shares]
    
    # make list of shares as MyType objects for current party
    def readFile(self, filename):
        f = open(filename,"r")
        for line in f:
            self.shares.append(MyType(int(line.strip())))

    
    # Send own shares to some party (sendTo)
    def sendShares(self, sendTo, value):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            pickled = pickle.dumps(value)
            s.connect((self.address, self.lookup.get(sendTo)))
            s.send(pickled)

    # Receive shares from some party
    def recvShares(self,recvParty):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.address, self.lookup.get(recvParty)))
            s.listen()
            conn, addr = s.accept()
            data = conn.recv(1024)
            data_arr = pickle.loads(data)
            return repr(data_arr)
    
    # Add shares and convert result to be of MyType (number in ZL) 
    def addMyType(self, x, y):
        return MyType(x+y).x   
    
    # Reconstruct secret by sending shares from p1 to p0 and adding them and printing them
    def reconstruct2PC(self):
        if self.party == "p1":
            self.sendShares("p0",self.getShareVals())
        if self.party == "p0":
            p1_shares = literal_eval(self.recvShares(self.party))
            reconstructed = [self.addMyType(x,y) for x,y in zip(self.getShareVals(), p1_shares)]
            print("Reconstructed: ", reconstructed)


    def wrap(self, a, b):
        if(a.x + b.x >= 2**L):
            return 1
        else:
            return 0
    
    def convertToBitString(self, x):
        return format(x.x, "0"+str(L)+'b')
    

    def generateBitShares(self, x):
        share0 = []
        share1 = []
        for i in range(L):
            num = int(x[i])
            r = random.randint(0,p)
            share1.append(r)
            share0.append((num - r) % p)

        return share0, share1
    
    def generateMyTypeShares(self, x, in_zl=True):
        if in_zl == True:
            r = random.randint(0, 2**L)
        else:
            r = random.randint(0, (2**L)-1)

        return MyType(r, is_zl=in_zl), MyType(x-r, is_zl=in_zl)
    
    def dummyPC(self, x, r, beta):    
        return beta.x ^ (x.x > r.x) 
        

    def shareConvert(self, a=MyType(0)):
        #replace these with actual values
        if(a == 2**L - 1):
            raise Exception("a can't be ZL-1")
        n_prime_prime = MyType(1)
        r = MyType(7)
        r_0 = MyType(3)
        r_1 = MyType(4)
        alpha = self.wrap(r_0, r_1)

        if(self.party == "p0"):
            a_tilde = a + r_0
            beta = self.wrap(a, r_0)
            self.sendInt("p2", a_tilde.x)
            x_bit_0 = self.recvShares("p0")
            delta_0 = self.recvInt("p0")
        if(self.party == "p1"):
            a_tilde = a + r_1
            beta = self.wrap(a, r_1)
            self.sendInt("p2", a_tilde.x)
            x_bit_1 = self.recvShares("p1")
            delta_1 = self.recvInt("p1")
        if(self.party == "p2"):
            a_tilde_0 = MyType(self.recvInt("p2"))
            a_tilde_1 = MyType(self.recvInt("p2"))

            x = a_tilde_0 + a_tilde_1
            delta = self.wrap(a_tilde_0, a_tilde_1)

            bin_x = self.convertToBitString(x)
            x_bit_arr_0, x_bit_arr_1 = self.generateBitShares(bin_x)
            delta_0, delta_1 = self.generateMyTypeShares(delta, False)

            self.sendShares("p0", x_bit_arr_0); self.sendShares("p1", x_bit_arr_1)
            time.sleep(0.1)
            self.sendInt("p0", delta_0.x); self.sendInt("p1", delta_1.x)
            time.sleep(0.1)

            n_prime = self.dummyPC(x, r-MyType(1), n_prime_prime)
            n_prime_0, n_prime_1 = self.generateMyTypeShares(n_prime,False)

            self.sendInt("p0", n_prime_0); self.sendInt("p1", n_prime_1)
            

        
     




    

    ############ Send and Receive for single int ####################
    def sendInt(self,sendTo,value):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.address, self.lookup.get(sendTo)))
            s.send(bytes(str(value), 'utf8'))

    def recvInt(self,recvParty):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.address, self.lookup.get(recvParty)))
            s.listen()
            conn, addr = s.accept()
            data = conn.recv(1024)
            strings = str(data, 'utf8')
            return(int(strings))



        


    
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


def test_Party():
    p0 = Party(0)
    print("p0 shares: ", p0.getShareVals())
    p1 = Party(1)
    print("p1 shares: ", p1.getShareVals())
    p2 = Party(2)
    print("p2 shares (empty): ", p2.shares)

def test_reconstruct2PC():
    parties = []
    p0 = Party(0); p1 = Party(1)
    parties.append(p0); parties.append(p1)
    print(p0.getShareVals()); print(p1.getShareVals())
    for p in parties:
        thread = threading.Thread(target=p.reconstruct2PC,args=())
        thread.start()

def test_shareConvert():
    parties = []
    p0 = Party(0); p1 = Party(1); p2 = Party(2)
    parties.append(p0); parties.append(p1)
    thread = threading.Thread(target=p2.shareConvert, args=())
    thread.start()
    time.sleep(0.1)
    for p in parties:
        thread = threading.Thread(target=p.shareConvert, args=(p.shares[0],))
        thread.start()
        time.sleep(0.1)
    



def test_ConvertTo3PShares():
    print("implement this")

test_shareConvert()
#test_Party()    
#test_reconstruct2PC()
#test_MyType()