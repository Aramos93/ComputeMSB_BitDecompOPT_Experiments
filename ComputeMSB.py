import random
import socket
import sys
import pickle
import time 
from ast import literal_eval
import threading
import time
import numpy as np
from ComposeNet import ComposeNet
from BigMat import BigMat

##################################################### Globals ########################################################
L = 64
p = 67
seed = random.randint(0,100)
file1 = "shares0.txt"
file2 = "shares1.txt"

######################################################################################################################


##################################################### Utilities ######################################################
modularize = lambda t: t % 2**L 
matmod = np.vectorize(modularize, otypes=[np.uint64]) 

modularize = lambda t: t % 2 
matmod2 = np.vectorize(modularize, otypes=[np.uint64])

def generateMatrixShares(M):
    M_0 = BigMat([[random.randint(0, (2**L)-1), random.randint(0, (2**L)-1)],[random.randint(0, (2**L)-1), random.randint(0, (2**L)-1)]])
    M_1 = (M - M_0) % L
    return M_0, M_1


# Generate shares in either ZL or Zl-1 of a number
def generateMyTypeShares(x, in_zl=True):
    if in_zl == True:
        r = random.randint(0, 2**L)
    else:
        r = random.randint(0, (2**L)-1)

    return MyType(r, is_zl=in_zl), MyType(x-r, is_zl=in_zl)

def generateBeaverTriplets(N):
    for _ in range(N):
        a = random.randint(0, 2**L)
        b = random.randint(0, 2**L)
        c = (a * b) % 2**L
        
        a_0, a_1 = generateMyTypeShares(a)
        b_0, b_1 = generateMyTypeShares(b)
        c_0, c_1 = generateMyTypeShares(c)
    
        p0.triplets.append([a_0.x, b_0.x, c_0.x])
        p1.triplets.append([a_1.x, b_1.x, c_1.x])

def generateMatBeaverTriplets(N):
    for _ in range(N):
        A = BigMat([[random.randint(0, (2**L)-1), random.randint(0, (2**L)-1)],[random.randint(0, (2**L)-1), random.randint(0, (2**L)-1)]])
        B = BigMat([[random.randint(0, (2**L)-1), random.randint(0, (2**L)-1)],[random.randint(0, (2**L)-1), random.randint(0, (2**L)-1)]])
        
        # A = np.random.randint(2**L, size=(2,2), dtype=np.uint64)
        # B = np.random.randint(2**L, size=(2,2), dtype=np.uint64)
        # A = np.array([[1,1], [1, 1]])
        # B = np.array([[1,1], [1,1]])
        C = (A @ B) % L 

        # A_0 = np.array([[0,0], [0,0]])
        # B_0 = np.array([[0,0], [0,0]])
        # C_0 = np.array([[0,0], [0,0]])
        
        A_0, A_1 = generateMatrixShares(A)
        B_0, B_1 = generateMatrixShares(B)
        C_0, C_1 = generateMatrixShares(C)
    
        p0.matTriplets.append([A_0, B_0, C_0])
        p1.matTriplets.append([A_1, B_1, C_1])


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

########################################### Party (Create p0, p1, p2) Protocols are here #############################

class Party:
    #### Initialize Party ######
    def __init__(self, partyName):
        # Connection Initialization
        self.address = '127.0.0.1'

        self.lookup = {  "p0_send_to_p1":2011,
                    "p0_send_to_p2":2021,
                    "p1_send_to_p0":2101,
                    "p1_send_to_p2":2121,
                    "p2_send_to_p0":2201,
                    "p2_send_to_p1":2211,
                    "p0_recv_from_p1":2010,
                    "p0_recv_from_p2":2020,
                    "p1_recv_from_p0":2100,
                    "p1_recv_from_p2":2120,
                    "p2_recv_from_p0":2200,
                    "p2_recv_from_p1":2210
                }
        if(partyName == 0):
            self.socket01send = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.socket01send.bind((self.address,self.lookup.get('p0_send_to_p1')))
            self.socket01recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket01recv.bind((self.address,self.lookup.get('p0_recv_from_p1')))
            self.socket02send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket02send.bind((self.address,self.lookup.get('p0_send_to_p2')))
            self.socket02recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket02recv.bind((self.address,self.lookup.get('p0_recv_from_p2')))

        elif(partyName == 1):
            self.socket10send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket10send.bind((self.address,self.lookup.get('p1_send_to_p0')))
            self.socket10recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket10recv.bind((self.address,self.lookup.get('p1_recv_from_p0')))
            self.socket12send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket12send.bind((self.address,self.lookup.get('p1_send_to_p2')))
            self.socket12recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket12recv.bind((self.address,self.lookup.get('p1_recv_from_p2')))

        elif(partyName == 2):
            self.socket20send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket20send.bind((self.address,self.lookup.get('p2_send_to_p0')))
            self.socket20recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket20recv.bind((self.address,self.lookup.get('p2_recv_from_p0')))
            self.socket21send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket21send.bind((self.address,self.lookup.get('p2_send_to_p1')))
            self.socket21recv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket21recv.bind((self.address,self.lookup.get('p2_recv_from_p1')))
        
        self.listenBuffer = []
        
        


        # Party shares initialization
        if partyName > 2 or partyName < 0:
            raise Exception("PartyName must be 0, 1, or 2")
        self.party = "p"+str(partyName)
        self.partyName = partyName
        self.shares = []
        self.converted_shares = []
        self.multResults = []
        self.multListResults = []
        self.matMultResults = []
        self.matMultListResults = []
        self.msbResults = []
        self.matTriplets = []
        self.triplets = []
        self.bitDecompOptResults = []
        self.pcResult = None
        if partyName == 0:
            self.readFile(file1)
        elif partyName == 1:
            self.readFile(file2)
        self.setupCommunication()



    #Function to listen and append data to listenBuffer when received.
    def listen(self, listenSocket):
        listenSocket.listen()
        listenSocket, _ = listenSocket.accept()
        while True:
            data = listenSocket.recv(4096)
            self.listenBuffer.append(data)

    #Function to actively connect to a listening socket.
    def connect(self, sendSocket, targetAddress, target, source):
        while True:
            try:
                if(source == 0):
                    if(target == 1):
                        sendSocket.connect((targetAddress,self.lookup.get("p1_recv_from_p0")))
                    elif(target == 2):
                        sendSocket.connect((targetAddress,self.lookup.get("p2_recv_from_p0")))

                elif(source == 1):
                    if(target == 0):
                        sendSocket.connect((targetAddress,self.lookup.get("p0_recv_from_p1")))
                    elif(target == 2):
                        sendSocket.connect((targetAddress,self.lookup.get("p2_recv_from_p1")))

                elif(source == 2):
                    if(target == 0):
                        sendSocket.connect((targetAddress,self.lookup.get("p0_recv_from_p2")))
                    elif(target == 1):
                        sendSocket.connect((targetAddress,self.lookup.get("p1_recv_from_p2")))

                return
            except Exception as e:
                print(str(e))
                continue
    
    #Connects each socket with each other with connects/listens
    def setupCommunication(self):
        if(self.partyName == 0):
            

            thread1 = threading.Thread(target=self.connect,kwargs=dict(sendSocket=self.socket01send,targetAddress=self.address,target=1,source=0))
            thread1.daemon = True
            thread1.start()

            thread2 = threading.Thread(target=self.connect,kwargs=dict(sendSocket=self.socket02send,targetAddress=self.address,target=2,source=0))
            thread2.daemon = True
            thread2.start()

            thread3 = threading.Thread(target=self.listen,kwargs=dict(listenSocket=self.socket01recv))
            thread3.daemon = True            
            thread3.start()

            thread4 = threading.Thread(target=self.listen,kwargs=dict(listenSocket=self.socket02recv))
            thread4.daemon = True            
            thread4.start()

        if(self.partyName == 1):
           
            thread1 = threading.Thread(target=self.connect,kwargs=dict(sendSocket=self.socket10send,targetAddress=self.address,target=0,source=1))
            thread1.daemon = True
            thread1.start()

            thread2 = threading.Thread(target=self.connect,kwargs=dict(sendSocket=self.socket12send,targetAddress=self.address,target=2,source=1))
            thread2.daemon = True
            thread2.start()

            thread3 = threading.Thread(target=self.listen,kwargs=dict(listenSocket=self.socket10recv))
            thread3.daemon = True            
            thread3.start()

            thread4 = threading.Thread(target=self.listen,kwargs=dict(listenSocket=self.socket12recv))
            thread4.daemon = True            
            thread4.start()

        if(self.partyName == 2):

            thread1 = threading.Thread(target=self.connect,kwargs=dict(sendSocket=self.socket20send,targetAddress=self.address,target=0,source=2))
            thread1.daemon = True
            thread1.start()

            thread2 = threading.Thread(target=self.connect,kwargs=dict(sendSocket=self.socket21send,targetAddress=self.address,target=1,source=2))
            thread2.daemon = True
            thread2.start()

            thread3 = threading.Thread(target=self.listen,kwargs=dict(listenSocket=self.socket20recv))
            thread3.daemon = True            
            thread3.start()

            thread4 = threading.Thread(target=self.listen,kwargs=dict(listenSocket=self.socket21recv))
            thread4.daemon = True            
            thread4.start()
        
    # Get actual values of shares from MyType's
    def getShareVals(self):
        return [e.x for e in self.shares]
    
    # make list of shares as MyType objects for current party
    def readFile(self, filename):
        f = open(filename,"r")
        for line in f:
            self.shares.append(MyType(int(line.strip())))

    
   
    ################ Send and Receive shares ###################
    def sendShares(self, target, value):
        pickled = pickle.dumps(value)
        thread = threading.Thread(target=self.send,kwargs=dict(sendTo=target, value=pickled))
        thread.daemon = True
        thread.start()
        #self.send(sendTo,pickled)

    def recvShares(self,recvParty, length=0):
        while True:
            if(len(self.listenBuffer)==0):
                continue
            else:
                data = self.listenBuffer.pop(0)
                data_arr = pickle.loads(data)
                if(length != 0):
                    if (len(literal_eval(repr(data_arr))) == length):
                        return repr(data_arr)
                    else:
                        self.listenBuffer.append(data)
                        continue
                else:
                    return repr(data_arr)

    def send(self, sendTo, value):
        if(self.party == "p0"):
            if(sendTo == "p1"):
                self.socket01send.send(value)
            elif(sendTo == "p2"):
                self.socket02send.send(value)

        elif(self.party == "p1"):
            if(sendTo == "p2"):
                self.socket12send.send(value)
            elif(sendTo == "p0"):
                self.socket10send.send(value)

        elif(self.party == "p2"):
            if(sendTo == "p0"):
                self.socket20send.send(value)
            elif(sendTo == "p1"):
                self.socket21send.send(value)


    ############ Send and Receive single int ####################
    def sendInt(self,target,value):
        intBytes = bytes(str(value), 'utf8')
        thread = threading.Thread(target=self.send,kwargs=dict(sendTo=target, value=intBytes))
        thread.daemon = True
        thread.start()
        #self.send(sendTo,intBytes)

    def recvInt(self,recvParty):
        while True:
            if(len(self.listenBuffer)==0):
                continue
            else:
                data = self.listenBuffer.pop(0)
                strings = str(data, 'utf8')
                return(int(strings))
           
    # Reconstruct secret by sending shares from p1 to p0 and adding them and printing them
    def reconstruct2PC(self):
        if self.party == "p1":
            self.sendShares("p0",self.getShareVals())
        if self.party == "p0":
            p1_shares = literal_eval(self.recvShares(self.party))
            reconstructed = [MyType(x+y).x for x,y in zip(self.getShareVals(), p1_shares)]
            print("Reconstructed: ", reconstructed)
            return reconstructed
    
    # Reconstruct a single secret by sending its share from p1 to p0, adding each share and return result
    def reconstruct2PCSingleInt(self, a):
        res =  MyType(0)
        if self.party == "p1":
            self.sendInt("p0", a.x)
        if(self.party == "p0"):
            a_1 = self.recvInt(self.party)
            res = a + MyType(a_1)
        return res        
            
    #Check if a+b > ZL aka wraps around ZL
    def wrap(self, a, b):
        if(a.x + b.x >= 2**L):
            return 1
        else:
            return 0
    
    # convert integer to L sized bitstring with trailing zeros
    def convertToBitString(self, x):
        return format(x.x, "0"+str(L)+'b')
    
    # Generate shares of each bit of a number x
    def generateBitShares(self, x):
        random.seed(123)
        share0 = []
        share1 = []
        for i in range(L):
            num = int(x[i])
            r = random.randint(0,p)
            share1.append(r)
            share0.append((num - r) % p)

        return share0, share1
    

    def privateCompare(self, x=[], r=MyType(0), beta=MyType(-1)):
        if self.party != "p2":
            random.seed(123)
            x = x[::-1]
            t = MyType(r.x+1)
            t = self.convertToBitString(t)
            t = [int(e) for e in t][::-1]
            r_original = r
            r = self.convertToBitString(r)
            r = [int(e) for e in r][::-1]
            s = [random.randint(1,p) for _ in range(L)]
        

        w = [None]*L
        c = [None]*L
        if self.party == "p0":
            # print("p0 x",x)
            # print("p0 r",r)
            # print("p0 t",t)
            for i in range (L-1, -1, -1):
                if beta.x == 0:                     
                    w[i] = (x[i] - 2 * r[i] * x[i]) % p
                    if i == L-1:
                        c[i] = (-x[i]) % p
                    else:
                        sigma_sum = 0
                        for k in range(i+1, L):
                            sigma_sum = sigma_sum + w[k]
                        c[i] = (-x[i] + sigma_sum) % p
                elif beta.x == 1 and r_original.x != ((2**L) -1):
                    w[i] = (x[i] - 2 * t[i] * x[i]) % p
                    if i == L-1:
                        c[i] = (x[i]) % p
                    else:
                        sigma_sum = 0
                        for k in range(i+1, L):
                            sigma_sum = (sigma_sum + w[k]) % p
                        c[i] = (x[i] + sigma_sum) % p
                else:
                    #print("THIS ONE RIGHT HERE")
                    if i != 1:
                        c[i] = 1
                    else:
                        c[i] = -1 % p
            #print("c,p0",c)
            #print("p0 w:",w)
            #print("p0 c:",c)
            d = [s_x *c_x for s_x, c_x in zip(s,c)]
            self.sendShares("p2", d)

        if self.party == "p1":
            # print("p1 x",x)
            # print("p1 r",r)
            # print("p1 t",t)
            for i in range (L-1, -1, -1):
                if beta.x == 0:    
                    w[i] = (x[i] + r[i] - (2*r[i]*x[i])) % p
                    if i == L-1:
                        c[i] = (r[i] - x[i] + 1) % p
                    else:
                        sigma_sum = 0
                        for k in range(i+1, L):
                            sigma_sum = (sigma_sum + w[k]) % p
                        c[i] = (r[i] - x[i] + 1 + sigma_sum) % p
                elif beta.x == 1 and r_original.x != ((2**L) -1):
                    w[i] = (x[i] + t[i] - 2*t[i]*x[i]) % p
                    if i == L-1:
                        c[i] = (-t[i] + x[i] + 1) % p
                    else:
                        sigma_sum = 0
                        for k in range(i+1, L):
                            sigma_sum = sigma_sum + w[k]
                        c[i] = (-t[i] + x[i] + 1 + sigma_sum) % p
                else:
                    # print("THIS ONE RIGHT HERE")
                    # print(r_original.x)
                    if i != 1:
                        c[i] = 0
                    else:
                        c[i] = -1 % p
            #print("p1 w:",w)
            #print("p1 c:",c)
            #print("c,p1",c)
            d = [s_x *c_x for s_x, c_x in zip(s,c)]
        
            self.sendShares("p2", d)

        if self.party == "p2":
            d_0 = literal_eval(self.recvShares("p2"))
            d_1 = literal_eval(self.recvShares("p2"))
            d = [(x+y) % p for x,y in zip(d_0, d_1)]
            #print(d)
            if 0 in d:
                self.pcResult = 1
                return 1
            else:
                self.pcResult = 0
                return 0

    # Mimic private compare - actually just compares reconstructed value
    def dummyPC(self, x, r, beta):   
        return beta.x ^ (x.x > r.x)


    def matMult(self,X,Y):
        if self.party == "p0":
            A, B, C = self.matTriplets[0]; self.matTriplets.pop(0)
            E_0 = (X - A) % L
            F_0 = (Y - B) % L
            toSend = [E_0.matrix, F_0.matrix]
            self.sendShares("p1", toSend)
            E_1, F_1 = literal_eval(self.recvShares("p0"))
            E_1 = BigMat(E_1); F_1 = BigMat(F_1)
            E = (E_0 + E_1) % L
            F = (F_0 + F_1) % L

            res = ((X @ F) + (E @ Y) + C) % L
            self.matMultResults.append(res)
            return res
            
            
        if self.party == "p1":
            A, B, C = self.matTriplets[0]; self.matTriplets.pop(0)
            E_1 = (X - A) % L
            F_1 = (Y - B) % L
            toSend = [E_1.matrix, F_1.matrix]
            self.sendShares("p0", toSend)
            E_0, F_0 = literal_eval(self.recvShares("p1"))
            E_0 = BigMat(E_0); F_0 = BigMat(F_0)
            E = (E_0 + E_1) % L
            F = (F_0 + F_1) % L
        
            res = (((E @ F)*-1) + (X @ F) + (E @ Y) + C) % L
            self.matMultResults.append(res)
            return res

    
    def matMultList(self, X, Y):
        length = len(X)
        if self.party == "p0":
            A = [None]*length; B = [None]*length; C = [None]*length; 
            for i in range(length):
                a,b,c = self.matTriplets.pop(0)
                A[i] = a; B[i] = b; C[i] = c
             
        
            E_0_list = [((x - a) % L).matrix for x,a in zip(X,A)]
            F_0_list = [((y - b) % L).matrix for y,b in zip(Y,B)]
            toSend = [E_0_list, F_0_list]
            self.sendShares("p1", toSend)
            E_1, F_1 = literal_eval(self.recvShares("p0"))

            E_1_list = [BigMat(e) for e in E_1]
            F_1_list = [BigMat(f) for f in F_1]
            
            E = [((BigMat(e0) + e1) % L) for e0,e1 in zip(E_0_list,E_1_list)]
            F = [((BigMat(f0) + f1) % L) for f0,f1 in zip(F_0_list,F_1_list)]

            res = [(((x @ f) + (e @ y) + c) % L) for x,f,e,y,c in zip(X,F,E,Y,C)]
            self.matMultListResults = res
            return res
            
            
        if self.party == "p1":
            A = [None]*length; B = [None]*length; C = [None]*length; 
            for i in range(length):
                a,b,c = self.matTriplets.pop(0)
                A[i] = a; B[i] = b; C[i] = c
            E_1_list = [((x - a) % L).matrix for x,a in zip(X,A)]
            F_1_list = [((y - b) % L).matrix for y,b in zip(Y,B)]
            toSend = [E_1_list, F_1_list]
            self.sendShares("p0", toSend)
            E_0, F_0 = literal_eval(self.recvShares("p1"))
            
            E_0_list = [BigMat(e) for e in E_0]
            F_0_list = [BigMat(f) for f in F_0]
            
            
            E = [((e0 + BigMat(e1)) % L) for e0,e1 in zip(E_0_list,E_1_list)]
            F = [((f0 + BigMat(f1)) % L) for f0,f1 in zip(F_0_list,F_1_list)]

            res = [((((e @ f)*-1) + (x @ f) + (e @ y) + c) % 2) for x,f,e,y,c in zip(X,F,E,Y,C)]
            self.matMultListResults = res
            return res


    def mult(self, x=MyType(0), y=MyType(0)):
        if self.party == "p0":
            shares_0 = literal_eval(self.recvShares("p0",3))
            a = shares_0[0]; b = shares_0[1]; c = shares_0[2]
            e_0 = MyType(x.x - a)
            f_0 = MyType(y.x - b)
            e_f_shares_0 = [e_0.x, f_0.x]
            e_f_shares_1 = literal_eval(self.recvShares("p0",2))
            #print("e_f shares_0: ", e_f_shares_0)
            self.sendShares("p1", e_f_shares_0)
            #time.sleep(0.1) 
            e_1 = e_f_shares_1[0]; f_1 = e_f_shares_1[1]
            e = MyType(e_0.x + e_1); f = MyType(f_0.x + f_1)
            #print(f"p0 e and f: {e.x}, {f.x}")
            x_mult_y_0 = MyType(-self.partyName * e.x * f.x + x.x * f.x + e.x * y.x + c)
            self.multResults.append(x_mult_y_0)
            #print("p0 x*y_0: ", x_mult_y_0.x)
            return x_mult_y_0
        
        if self.party == "p1":
            shares_1 = literal_eval(self.recvShares("p1",3))
            a = shares_1[0]; b = shares_1[1]; c = shares_1[2]
            e_1 = MyType(x.x - a)
            f_1 = MyType(y.x - b)
            e_f_shares_1 = [e_1.x, f_1.x]
            # print("p1 e_1: ", e_1.x)
            # print("e_f shares_1: ", e_f_shares_1)
            self.sendShares("p0", e_f_shares_1)
            #time.sleep(0.1)
            e_f_shares_0 = literal_eval(self.recvShares("p1",2))    
            e_0 = e_f_shares_0[0]; f_0 = e_f_shares_0[1]
            #print("p1 e_0: ",e_0)
            e = MyType(e_0 + e_1.x); f = MyType(f_0 + f_1.x)
            #print(f"p1 e and f: {e.x}, {f.x}")
            x_mult_y_1 = MyType(-self.partyName * e.x * f.x + x.x * f.x + e.x * y.x + c)
            #print("p1 x*y_1: ",x_mult_y_1.x)
            self.multResults.append(x_mult_y_1)
            return x_mult_y_1

        if self.party == "p2":
            a = MyType(random.randint(0,2**L))
            b = MyType(random.randint(0,2**L))
            c = MyType(a.x*b.x)
            # a = MyType(15)
            # b = MyType(11)
            c = MyType(a.x*b.x)
            a_0, a_1 = generateMyTypeShares(a.x)
            b_0, b_1 = generateMyTypeShares(b.x)
            c_0, c_1 = generateMyTypeShares(c.x)
            #print(f"a, b, c: {a.x},{b.x},{c.x}")
            shares_0 = [a_0.x, b_0.x, c_0.x]; shares_1 = [a_1.x, b_1.x, c_1.x]
            # shares_0 = [3,10,2]; shares_1 = [12,1,3]
           # print(f"abc_0: {shares_0}, abc_1: {shares_1}")
            self.sendShares("p0", shares_0); self.sendShares("p1", shares_1)
            #time.sleep(0.1)


    def mult2(self,x,y):
        if self.party == "p0":
            a,b,c = self.triplets.pop(0)
            e_0 = (x.x - a) % 2**L
            f_0 = (y.x - b) % 2**L
            toSend = [e_0, f_0]
            self.sendShares("p1", toSend)
            e_1, f_1 = literal_eval(self.recvShares("p0"))     
            e_1 = int(e_1); f_1 = int(f_1)
            e = (e_0 + e_1) % 2**L
            f = (f_0 + f_1) % 2**L

            res = MyType((x.x*f) + (e*y.x) + c) 
            self.multResults.append(res)
            return res
                    
        if self.party == "p1":
            a,b,c = self.triplets.pop(0)
            e_1 = (x.x - a) % 2**L
            f_1 = (y.x - b) % 2**L
            toSend = [e_1, f_1]   
            e_0, f_0 = literal_eval(self.recvShares("p1"))
            self.sendShares("p0", toSend)
            e_0 = int(e_0); f_0 = int(f_0)
            e = (e_0 + e_1) % 2**L
            f = (f_0 + f_1) % 2**L

            res = MyType(-1*(e*f) + (x.x*f) + (e*y.x) + c)
            self.multResults.append(res)
            return res


    def multList(self, X, Y):
        length = len(X)
        if self.party == "p0":
            A = [None]*length; B = [None]*length; C = [None]*length; 

            for i in range(length):
                a,b,c = self.triplets.pop(0)
                A[i] = a; B[i] = b; C[i] = c
            
        
            E_0_list = [MyType(x - a).x for x,a in zip(X,A)]
            F_0_list = [MyType(y - b).x for y,b in zip(Y,B)]
            
            toSend = [E_0_list, F_0_list]
            
            self.sendShares("p1", toSend)
            E_1_list, F_1_list = literal_eval(self.recvShares("p0"))
            
            E = [MyType(e0+e1).x for e0,e1 in zip(E_0_list,E_1_list)]
            F = [MyType(f0+f1).x for f0,f1 in zip(F_0_list,F_1_list)]

            res = [MyType((x*f) + (e*y) + c).x for x,f,e,y,c in zip(X,F,E,Y,C)]
            self.multListResults.append(res)
            return res
        if self.party == "p1":
            A = [None]*length; B = [None]*length; C = [None]*length; 
            for i in range(length):
                a,b,c = self.triplets.pop(0)
                A[i] = a; B[i] = b; C[i] = c    
        
            E_1_list = [MyType(x - a).x for x,a in zip(X,A)]
            F_1_list = [MyType(y - b).x for y,b in zip(Y,B)]
            toSend = [E_1_list, F_1_list]
            self.sendShares("p0", toSend)
            E_0_list, F_0_list = literal_eval(self.recvShares("p1"))
               
            E = [MyType(e0+e1).x for e0,e1 in zip(E_0_list,E_1_list)]
            F = [MyType(f0+f1).x for f0,f1 in zip(F_0_list,F_1_list)]

            res = [MyType(-1*(e * f) + (x * f) + (e * y) + c).x for x,f,e,y,c in zip(X,F,E,Y,C)]
            self.multListResults.append(res)
            
            return res

    # Convert a shares of some value a in ZL to shares of the same value in ZL-1
    def shareConvert(self, a=MyType(0)):
        if self.party == "p0" or self.party == "p1":
            rec = self.reconstruct2PCSingleInt(a) # This reconstruction is only to check value of a
        # Use same random seed to ensure all parties share same common randomness: r, r_0, r_1, n''
        random.seed(seed)
        n_prime_prime = MyType(random.randint(0,1))
        r = MyType(random.randint(1,2**L)) #can't be 0 for some reason. Probably handled in PC which we don't implement

        r_0, r_1 = generateMyTypeShares(r.x)
        alpha = self.wrap(r_0, r_1)
        
        if(self.party == "p0"):
            if rec.x == ((2**L) - 1) :
                raise Exception(f"Reconstructed value 'a' is {rec.x} == L-1 {(2**L)-1} which is not allowed according to protocol")
            a_tilde = a + r_0
            beta = self.wrap(a, r_0)
            self.sendInt("p2", a_tilde.x)
            x_bit_0 = self.recvShares("p0") # bit shares of x not used because PC not implemented (only dummied)
            delta_0 = self.recvInt("p0")
            n_prime_0 = self.recvInt("p0")
            n_0 = MyType(n_prime_0 + (1 - self.partyName)*n_prime_prime.x - 2 * n_prime_prime.x * n_prime_0, is_zl=False)
            theta = MyType(beta + (1 - self.partyName) * (-alpha - 1) + delta_0 + n_0.x, is_zl=False)
            y_0 = MyType(a.x-theta.x, is_zl=False)

            #print("After convert - p0 a:",y_0.x)
            self.converted_shares.append(y_0)
            return y_0
        if(self.party == "p1"):
            a_tilde = a + r_1
            beta = self.wrap(a, r_1)
            self.sendInt("p2", a_tilde.x)
            x_bit_1 = self.recvShares("p1") # bit shares of x not used because PC not implemented (only dummied)
            delta_1 = self.recvInt("p1")
            n_prime_1 = self.recvInt("p1")
            n_1 = MyType(n_prime_1 + (1 - self.partyName) * n_prime_prime.x - 2 * n_prime_prime.x * n_prime_1, is_zl=False)
            theta = MyType(beta + (1 - self.partyName) * (-alpha - 1) + delta_1 + n_1.x, is_zl=False)
            y_1 = MyType(a.x-theta.x, is_zl=False)

            #print("After convert - p1 a:", y_1.x)
            self.converted_shares.append(y_1)
            return y_1
            
        if(self.party == "p2"):
            a_tilde_0 = MyType(self.recvInt("p2"))
            a_tilde_1 = MyType(self.recvInt("p2"))
            x = a_tilde_0 + a_tilde_1
            delta = self.wrap(a_tilde_0, a_tilde_1)
 
            x_bit_arr_0, x_bit_arr_1 = self.generateBitShares(self.convertToBitString(x))
            delta_0, delta_1 = generateMyTypeShares(delta, False)

            self.sendShares("p0", x_bit_arr_0); self.sendShares("p1", x_bit_arr_1)
            #time.sleep(0.1)
            self.sendInt("p0", delta_0.x); self.sendInt("p1", delta_1.x)
            #time.sleep(0.1)

            n_prime = self.dummyPC(x, r-MyType(1), n_prime_prime)
            n_prime_0, n_prime_1 = generateMyTypeShares(n_prime,False)
           

            self.sendInt("p0", n_prime_0.x); self.sendInt("p1", n_prime_1.x)
    

    def computeMSB(self, a=MyType(0)):
        if self.party == "p0" or self.party == "p1":
            rec = self.reconstruct2PCSingleInt(a)
        random.seed(seed)
        #beta = MyType(random.randint(0,1),is_zl=False)
        beta = MyType(1,is_zl=False)       

        if self.party == "p0":
            #if rec.x >= ((2**L) - 1):
             #   raise Exception(f"Reconstructed value 'a' is {rec.x} which is NOT in ZL-1 {(2**L) -1}")
            x_0 = MyType(self.recvInt("p0"), is_zl=False)   
            x_bit_arr_0 = literal_eval(self.recvShares("p0"))
            x_firstBit_0 = self.recvInt("p0")
            #x_firstBit_0 = 0
            #print(f"p0 received: x_0 {x_0.x}, x_bit_arr_0 {x_bit_arr_0}, xfirstbit {x_firstBit_0}")
            y_0 = MyType(2*a.x, is_zl=False) 
            r_0 = MyType(y_0.x + x_0.x, is_zl=False)  
            r_1 = MyType(self.recvInt("p0"), is_zl=False)   
            self.sendInt("p1", r_0.x)
            #time.sleep(0.1)             
            r = MyType(r_0.x + r_1.x, is_zl=False)

            self.privateCompare(x_bit_arr_0, r, beta)

            # print("p0 a: ", a.x)
            # print("p0 x_0: ", x_0.x)
            # print("p0 y_0: ", y_0.x)
            # print("p0 r_0: ", r_0.x)
            # print("p0 r_1: ", r_1.x)
            # print("p0 r: ", r.x)

            beta_prime_0 = MyType(self.recvInt("p0"))
            #beta_prime_0 = MyType(2)
            #print("p0 b':",beta_prime_0.x)
            gamma_0 = MyType(beta_prime_0.x + self.partyName * beta.x - 2 * beta.x * beta_prime_0.x)
            #print("p0 gamma0: ",gamma_0.x)
            delta_0 = MyType(x_firstBit_0 + self.partyName * int(bin(r.x)[-1]) - 2 * int(bin(r.x)[-1]) * x_firstBit_0)
            #print("p0 delta0: ",delta_0.x)
            #print(f"p0 mult: {gamma_0.x}, {delta_0.x}")

            theta_0 = self.mult(gamma_0, delta_0)
            #print("p0 multres: ", theta_0.x)
            alpha_0 = MyType(gamma_0.x + delta_0.x - 2 * theta_0.x)
            self.msbResults.append(alpha_0)
            return alpha_0

        if self.party == "p1":      
            x_1 = MyType(self.recvInt("p1"), is_zl=False) 
            x_bit_arr_1 = literal_eval(self.recvShares("p1"))
            x_firstBit_1 = self.recvInt("p1")
            #x_firstBit_1 = 0
            #print(f"p1 received: x_1 {x_1.x}, x_bit_arr_1 {x_bit_arr_1}, xfirstbit {x_firstBit_1}")
            y_1 = MyType(2*a.x, is_zl=False)    
            r_1 = MyType(y_1.x + x_1.x, is_zl=False)    
            self.sendInt("p0", r_1.x)
            #time.sleep(0.1)
            r_0 = MyType(self.recvInt("p1"), is_zl=False)     
            r = MyType(r_0.x + r_1.x, is_zl=False)

            self.privateCompare(x_bit_arr_1, r, beta)
            # print("p1 a: ", a.x)
            # print("p1 x_1: ", x_1.x)
            # print("p1 y_1: ", y_1.x)
            # print("p1 r_1: ", r_1.x)
            # print("p1 r_0: ", r_0.x)
            # print("p1 r: ", r.x)

            #self.sendInt("p2", r.x) #Doesn't actually happen in protocol, but p2 needs to dummy PC
        

            beta_prime_1 = MyType(self.recvInt("p1"))
            #beta_prime_1 = MyType(14)
            #print("p1 b':",beta_prime_1.x)
            gamma_1 = MyType(beta_prime_1.x + self.partyName * beta.x - 2 * beta.x * beta_prime_1.x)
            #print("p1 gamma1: ",gamma_1.x)
            delta_1 = MyType(x_firstBit_1 + self.partyName * int(bin(r.x)[-1]) - 2 * int(bin(r.x)[-1]) * x_firstBit_1)
            #print("p1 delta1: ",delta_1.x)
            #print(f"p1 mult: {gamma_1.x}, {delta_1.x}")

            theta_1 = self.mult(gamma_1, delta_1)
            #print("p1 multres: ", theta_1.x)
            alpha_1 = MyType(gamma_1.x + delta_1.x - 2 * theta_1.x)
            self.msbResults.append(alpha_1)
            return alpha_1

        if self.party == "p2":
            x = MyType(random.randint(0, (2**L) - 1), is_zl=False)
            #x = MyType(8, is_zl=False)
            x_0, x_1 = generateMyTypeShares(x.x, in_zl=False)
            #x_0, x_1 = MyType(12,is_zl=False), MyType(11,is_zl=False)
            bin_x = self.convertToBitString(x)
            x_bit_arr_0, x_bit_arr_1 = self.generateBitShares(bin_x)
            x_firstBit_0, x_firstBit_1 = generateMyTypeShares(int(bin_x[-1]))
            # print("x: ", x.x)
            # print(f"x_0: {x_0.x} x_1: {x_1.x}")
            # print("bin_x: ", bin_x)
            # print(f"x_bit_arr_0: {x_bit_arr_0}, x_bit_arr_1: {x_bit_arr_1}")
            # print(f"x_first_0: {x_firstBit_0.x}, x_first_1: {x_firstBit_1.x}")
          
            self.sendInt("p0", x_0.x); self.sendInt("p1", x_1.x)
            #time.sleep(0.1)
            self.sendShares("p0", x_bit_arr_0); self.sendShares("p1", x_bit_arr_1)
            #time.sleep(0.1)
            self.sendInt("p0", x_firstBit_0.x); self.sendInt("p1", x_firstBit_1.x)
            #time.sleep(0.1)
            #r = MyType(self.recvInt("p2"), is_zl=False)
            #print("p2 r: ", r.x)
            beta_prime = self.privateCompare()
            #print("beta': ",beta_prime)
            beta_prime_0, beta_prime_1 = generateMyTypeShares(beta_prime)
            #print(f"beta'0: {beta_prime_0.x}, beta'1: {beta_prime_1.x}")
            self.sendInt("p0", beta_prime_0.x); self.sendInt("p1", beta_prime_1.x)
            self.mult()


    def bitDecomp(self, a=MyType(0)):
        if self.party == "p0":
            a0 = self.convertToBitString(a)[::-1]
            a0 = [int(s) for s in a0]
            b0 = self.convertToBitString(MyType(0))
            b0 = [int(s) for s in b0]
            #print("a0",a0)

            c = [None]*L
            x = [None]*L
            d = [None]*L
            e = [None]*L
            
            c[0] = self.mult2(MyType(a0[0]),MyType(b0[0])).x % 2
            x[0] = a0[0] #not doing addition since other share is 0
            for i in range(1,L):
                d[i] = (self.mult2(MyType(a0[i]),MyType(b0[i])).x+1 ) % 2
                
                #print("p0:d:",i,"d[i]",d[i])

                e[i] = (self.mult2(MyType(a0[i]), MyType(c[i-1])).x+1)% 2
                #e[i] = (a0[i] * c[i-1]) % 2
             
                c[i] = (self.mult2(MyType(e[i]), MyType(d[i])).x+1 ) % 2
                
                x[i] = (a0[i] + c[i-1]) % 2
            # print("d:",d)
            # print("e:",e)
            # print("c:",c)
            # print("x",x)
            # print("")
            
            self.msbResults.append(x[-1])
        if self.party == "p1":
            
            a1 = self.convertToBitString(MyType(0))
            a1 = [int(s) for s in a1]
            b1 = self.convertToBitString(a)[::-1]
            b1 = [int(s) for s in b1]
            #print("b1",b1)
            c = [None]*L
            x = [None]*L
            d = [None]*L
            e = [None]*L
            
            c[0] = self.mult2(MyType(a1[0]),MyType(b1[0])).x % 2
            x[0] = b1[0]
            for i in range(1,L):
                d[i] = (self.mult2(MyType(a1[i]),MyType(b1[i])).x ) % 2 
               
                #print("p1:d:",i,"d[i]",d[i])
                e[i] = (self.mult2(MyType(b1[i]), MyType(c[i-1])).x ) % 2
                #e[i] = (b1[i] * c[i-1] +1) % 2
              
                c[i] = (self.mult2(MyType(e[i]), MyType(d[i])).x ) % 2
             
                x[i] = (b1[i] + c[i-1]) % 2
            #time.sleep(0.8)
            # print("d:",d)
            # print("e:",e)
            # print("c:",c)
            # print("x",x)
            
            self.msbResults.append(x[-1])
        # if self.party == "p2":
        #     for i in range(3*L-2):
        #         self.mult()


    def bitDecompOpt(self, a=MyType(0)):
        cnet = ComposeNet(L)
        if self.party == "p0":
            p0 = self.convertToBitString(a)[::-1] #reverse since 0 is lsb
            #print("p0",p0)
            b0 = self.convertToBitString(MyType(0))[::-1]
            g0 = [None]*L
            p0list = [int(a) for a in p0]
            b0list = [int(a) for a in b0]

            g0 = self.multList(p0list,b0list)
            g0 = [a % 2 for a in g0]  

            #print("g0",g0)
            M0 = [None]*L
            for i in range(L):
                M0[i] = BigMat( [ [p0list[i],g0[i]] , [0,0] ])
            #print("Mj (p0)",M0)
            for i in range(L-1):
                cnet.layers[1][i].matrix = M0[i]

            for i in range(2, cnet.numLayers+1):
                leftlist = []
                rightlist = []
                for cnnode in cnet.layers[i]:
                    leftlist.append(cnnode.left.matrix)
                    rightlist.append(cnnode.right.matrix)
                result = self.matMultList(rightlist,leftlist)
                result = [(c % 2) for c in result]
                #print(result)
                for cnode, res in zip(cnet.layers[i],result):
                    cnode.matrix = res
                
                

            M1_J_0 = cnet.getMatrixResults()
            
            
            C_J_0 = [(m.matrix[0][1]) % 2 for m in M1_J_0]
            S_J_0 = [p0list[0]]
            
            for i in range(1,len(p0)):
                S_J_0.append(p0list[i]^C_J_0[i-1])
            
            S_J_0.reverse()
            res = S_J_0
            

            self.bitDecompOptResults.append(res[0])
            return res

        if self.party == "p1":
            
            p1 = self.convertToBitString(a)[::-1] #reverse since 0 is lsb
            
            b1 = self.convertToBitString(MyType(0))[::-1]
            g1 = [None]*L
            p1list = [int(a) for a in p1]
            b1list = [int(a) for a in b1]

            g1 = self.multList(b1list,p1list)
           
            g1 = [a % 2 for a in g1]
        
            
            M1 = [None]*L
            for i in range(L):
                M1[i] = BigMat( [ [p1list[i],g1[i]] , [0,1] ])
            #print("Mj (p1)",M1)
            for i in range(L-1):
                cnet.layers[1][i].matrix = M1[i]

            for i in range(2, cnet.numLayers+1):
                leftlist = []
                rightlist = []
                for cnnode in cnet.layers[i]:
                    leftlist.append(cnnode.left.matrix)
                    rightlist.append(cnnode.right.matrix)
                result = self.matMultList(rightlist,leftlist)
                result = [c % 2 for c in result]
                for cnode, res in zip(cnet.layers[i],result):
                    cnode.matrix = res
                    
                    

            M1_J_1 = cnet.getMatrixResults()
            C_J_1 = [(m.matrix[0][1]) % 2 for m in M1_J_1]
            S_J_1 = [p1list[0]]
            for i in range(1,len(p1)):
                S_J_1.append(p1list[i]^C_J_1[i-1])
            S_J_1.reverse()
            res = S_J_1
            
            self.bitDecompOptResults.append(res[0])
            return res
            

        



  
######################################################################################################################    



####################################################### Tests ########################################################

parties = []
p0 = Party(0); p1 = Party(1); p2 = Party(2)
parties.append(p0); parties.append(p1)
time.sleep(1)

def test_MyType():
    testListInput = [8,20,16,0,-3]
    testListRes = []
    for e in testListInput:
        testListRes.append(MyType(e).x)
    print(testListRes)

def test_bitDecomp():
    generateBeaverTriplets(100)
    #p0.shares = [MyType(2)]
    #p1.shares = [MyType(5)]
    for c in range(len(p0.shares)):

        thread = threading.Thread(target=p2.bitDecomp, args=())
        thread.start()
        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.bitDecomp, args=(p.shares[c],))
            threads[i].start()
        
        for p,t in zip(parties, threads):
            t.join(2)
        thread.join(2)
        
    time.sleep(0.2)
    
    print("##########################################################")
    print("BITDECOMP TEST")
    print("Share_0 input: ", [s.x for s in p0.shares])
    print("Share_1 input: ", [s.x for s in p1.shares])
    print("Reconstructed inputs", [MyType(s0.x+s1.x).x for s0,s1 in zip(p0.shares,p1.shares)])
    print("Inputs in Binary: ", [p0.convertToBitString(MyType(s0.x+s1.x)) for s0,s1 in zip(p0.shares,p1.shares)])
    print("Results:")
    print("alpha0 values (shares_0 of MSB): ", [s for s in p0.msbResults])
    print("alpha1 values (shares_1 of MSB): ", [s for s in p1.msbResults])
    print("Reconstructed MSB: ", [(s0+s1) % 2 for s0,s1 in zip(p0.msbResults,p1.msbResults)])
    print("#########################################################")
    print("")
    
def test_bitDecompOpt():
    generateBeaverTriplets(20000)
    generateMatBeaverTriplets(20000)
    #p0.shares = [MyType(9223372036854775808)]
    #p1.shares = [MyType(9223372036854775809)]
    start = time.time()
    for c in range(len(p0.shares)):
        threads = [None]*2
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.bitDecompOpt, args=(p.shares[c],))
            threads[i].start()
        
        for p,t in zip(parties, threads):
            t.join(10)

    end = time.time()
    print("TIME TAKEN",end - start)

    print("##########################################################")
    print("BITDECOMP TEST FOR TRUTH")
    real = [int(p0.convertToBitString(MyType(s0.x+s1.x))[0]) for s0,s1 in zip(p0.shares,p1.shares)]
    calculated = [(int(s0)+int(s1)) % 2 for s0,s1 in zip(p0.bitDecompOptResults,p1.bitDecompOptResults)]
    
    for i, (r, c) in enumerate(zip(real,calculated)):
        if r == c:
            continue
        else:
            print("r is ",r)
            print("c is ",c)
            print("p0 value:",p0.shares[i].x)
            print("p1 value:",p1.shares[i].x)
    print("#########################################################")
    print("")

def test_bitDecompOpt_time():
    generateBeaverTriplets(300)
    generateMatBeaverTriplets(300)
    p0.shares = [MyType(799616587)]
    p1.shares = [MyType(1156032192)]
    start = time.time()
    for c in range(len(p0.shares)):
        threads = [None]*2
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.bitDecompOpt, args=(p.shares[c],))
            threads[i].start()
        
        for p,t in zip(parties, threads):
            t.join(10)

    end = time.time()
    print("TIME TAKEN",end - start)

    print("##########################################################")
    print("BITDECOMP TEST")
    print("Share_0 input: ", [s.x for s in p0.shares])
    print("Share_1 input: ", [s.x for s in p1.shares])
    print("Reconstructed inputs", [MyType(s0.x+s1.x).x for s0,s1 in zip(p0.shares,p1.shares)])
    print("Inputs in Binary: ", [p0.convertToBitString(MyType(s0.x+s1.x)) for s0,s1 in zip(p0.shares,p1.shares)])
    print("Results:")
    print("alpha0 values (shares_0 of MSB): ", [s for s in p0.bitDecompOptResults])
    print("alpha1 values (shares_1 of MSB): ", [s for s in p1.bitDecompOptResults])
    print("Reconstructed Bit Decomp: ", [(int(s0)+int(s1)) % 2 for s0,s1 in zip(p0.bitDecompOptResults,p1.bitDecompOptResults)])
    print("#########################################################")
    print("")
    
def test_reconstruct2PC():
    print("p0 shares: ", p0.getShareVals())
    print("p1 shares: ", p1.getShareVals())
    for p in parties:
        thread = threading.Thread(target=p.reconstruct2PC,args=())
        thread.start()

def test_shareConvert():
    for c in range(len(p0.shares)):

        thread = threading.Thread(target=p2.shareConvert, args=())
        thread.start()

        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.shareConvert, args=(p.shares[c],))
            threads[i].start()
        
        for p,t in zip(parties, threads):
            t.join(2)
        thread.join(2)
    
    print("##########################################################")
    print("SHARECONVERT TEST")
    print("Shares in ZL")    
    print([s.x for s in p0.shares])
    print([s.x for s in p1.shares])
    print("Reconstructed: ", [(s0+s1).x for s0,s1 in zip(p0.shares,p1.shares)])
    print()
    print("Shares in ZL-1")
    print([s.x for s in p0.converted_shares])
    print([s.x for s in p1.converted_shares])
    print("Reconstructed: ", [MyType(s0.x+s1.x, is_zl=False).x for s0,s1 in zip(p0.converted_shares,p1.converted_shares)])
    print("##########################################################")
    print("")

def test_privateCompare():
    x = MyType(5)
    r = MyType(2)
    beta = MyType(1)

    x_bin = p0.convertToBitString(x)
    x_0, x_1 = p0.generateBitShares(x_bin)

   
    thread1 = threading.Thread(target=p0.privateCompare, kwargs={'x':x_0, 'r':r, 'beta':beta}); thread1.start()
    thread2 = threading.Thread(target=p1.privateCompare, kwargs={'x':x_1, 'r':r, 'beta':beta}); thread2.start()
    thread3 = threading.Thread(target=p2.privateCompare, args=()); thread3.start()

    thread1.join(2); thread2.join(2); thread3.join(2)

    print("##########################################################")
    print("PRIVATE COMPARE TEST")
    print(f"Comparing {x.x} > {r.x} with beta = {beta.x}")
    print(f"{beta.x} XOR ({x.x} > {r.x})")
    print("Result:",p2.pcResult)
    print("##########################################################")
    print()

def test_computeMSB():
    p0.converted_shares = [MyType(10),MyType(1),MyType(3),MyType(7),MyType(10),MyType(2),MyType(3),MyType(7),MyType(5),MyType(11)]
    p1.converted_shares = [MyType(2),MyType(7),MyType(11),MyType(14),MyType(5),MyType(12),MyType(12),MyType(0),MyType(10),MyType(7)]
        
    for c in range(len(p0.converted_shares)):
        threads = [None]*len(parties)
        for i, p in enumerate(parties):
           
            threads[i] = threading.Thread(target=p.computeMSB, args=(p.converted_shares[c],))
            threads[i].start()
           
        
        thread = threading.Thread(target=p2.computeMSB, args=())
        thread.start()

        for t in threads:
            t.join(2)
        thread.join(2)
      
    print("##########################################################")
    print("MSB TEST")
    print("Reconstructed inputs", [MyType(s0.x+s1.x, is_zl=False).x for s0,s1 in zip(p0.converted_shares,p1.converted_shares)])
    print("Inputs in Binary: ", [p0.convertToBitString(MyType(s0.x+s1.x,is_zl=False)) for s0,s1 in zip(p0.converted_shares,p1.converted_shares)])
    print("Results:")
    print("alpha0 values (shares_0 of MSB): ", [s.x for s in p0.msbResults])
    print("alpha1 values (shares_1 of MSB): ", [s.x for s in p1.msbResults])
    print("Reconstructed MSB: ", [MyType(s0.x+s1.x).x for s0,s1 in zip(p0.msbResults,p1.msbResults)])
    print("#########################################################")
    print("")

def test_mult():
    p0.shares = [MyType(2), MyType(4), MyType(2), MyType(3), MyType(8), MyType(4), MyType(9), MyType(0), MyType(10), MyType(1)]
    p1.shares = [MyType(1), MyType(1), MyType(2), MyType(5), MyType(8), MyType(3), MyType(9), MyType(1), MyType(2), MyType(1)]
    for c in range(len(p0.shares)-1):

        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.mult, args=(p.shares[c], p.shares[c+1]))
            threads[i].start()
        time.sleep(0.1)    
        thread = threading.Thread(target=p2.mult, args=())
        thread.start()

        for t in threads:
            t.join(2)
        thread.join(2)
    
    print("##########################################################")
    print("MULT TEST")
    print("Reconstructed inputs (each value c multiplied with c+1)", [MyType(s0.x+s1.x).x for s0, s1 in zip(p0.shares, p1.shares)])
    print("Results:")
    print("Share 0 of result: ", [s.x for s in p0.multResults])
    print("Share 1 of result: ", [s.x for s in p1.multResults])
    print("Reconstructed results: ", [MyType(s0.x + s1.x).x for s0, s1 in zip(p0.multResults, p1.multResults)])
    print("##########################################################")
    print("")

def test_mult2():
    generateBeaverTriplets(20)
    p0.shares = [MyType(2), MyType(4), MyType(2), MyType(3), MyType(8), MyType(4), MyType(9), MyType(0), MyType(10), MyType(1)]
    p1.shares = [MyType(1), MyType(1), MyType(2), MyType(5), MyType(8), MyType(3), MyType(9), MyType(1), MyType(2), MyType(1)]
    for c in range(len(p0.shares)-1):

        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.mult2, args=(p.shares[c], p.shares[c+1]))
            threads[i].start()
        

        for t in threads:
            t.join(2)
        
    
    print("##########################################################")
    print("MULT TEST")
    print("Reconstructed inputs (each value c multiplied with c+1)", [MyType(s0.x+s1.x).x for s0, s1 in zip(p0.shares, p1.shares)])
    print("Results:")
    print("Share 0 of result: ", [s.x for s in p0.multResults])
    print("Share 1 of result: ", [s.x for s in p1.multResults])
    print("Reconstructed results: ", [MyType(s0.x + s1.x).x for s0, s1 in zip(p0.multResults, p1.multResults)])
    print("##########################################################")
    print("")

def test_multList():
    generateBeaverTriplets(4)
    X_0_list = [14105040557866319647, 2, 3, 4]
    Y_0_list = [6223324861258668224, 3, 4, 5]
    X_1_list = [0, 0, 0, 0]
    Y_1_list = [0, 0, 0, 0]
    p0.shares = [X_0_list, Y_0_list]
    p1.shares = [X_1_list, Y_1_list]

    for c in range(len(p0.shares)-1):
        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.multList, args=(p.shares[c], p.shares[c+1]))
            threads[i].start()
        time.sleep(0.1)    
        

        for t in threads:
            t.join(2)

    
    print("##########################################################")
    print("MULTLIST TEST")
    print("Reconstructed X inputs", [s0+s1 for s0, s1 in zip(X_0_list, X_1_list)])
    print("Reconstructed Y inputs", [s0+s1 for s0, s1 in zip(Y_0_list, Y_1_list)])
    print("Results:")

    print("Result XY:", [MyType(s0+s1).x for s0, s1 in zip(p0.multListResults[0], p1.multListResults[0])])
    print("##########################################################")
    print("")

def test_matMult():
    generateMatBeaverTriplets(1)
    X = np.array([[1,2], [3,4]])
    Y = np.array([[4,3], [2,1]])
    # X_0 = np.array([[0,0], [0,0]])
    # Y_0 = np.array([[0,0], [0,0]])
    # X_1 = X
    # Y_1 = Y
    X_0, X_1 = generateMatrixShares(X)
    Y_0, Y_1 = generateMatrixShares(Y)
    p0.shares = [X_0, Y_0]
    p1.shares = [X_1, Y_1]
    
    for c in range(len(p0.shares)-1):
        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.matMult, args=(p.shares[c], p.shares[c+1]))
            threads[i].start()
            time.sleep(0.1)
    
    for t in threads:
        t.join(2)
    
    print("#######################################################")
    print("MATMULT Test")
    print("MATRIX X:", X)
    print("Matrix Y:", Y)
    print("Result XY:", [matmod(s0+s1) for s0, s1 in zip(p0.matMultResults, p1.matMultResults)])
   
def test_matMultList():
    generateMatBeaverTriplets(5)
    X = np.array([[1,2], [3,4]])
    Y = np.array([[4,3], [2,1]])
    
    X_0, X_1 = generateMatrixShares(X)
    Y_0, Y_1 = generateMatrixShares(Y)

    X_0 = [X_0]
    X_1 = [X_1]
    Y_0 = [Y_0]
    Y_1 = [Y_1]
    p0.shares = [X_0, Y_0,X_0,Y_0]
    p1.shares = [X_1, Y_1,X_1,Y_1]

    
    for c in range(len(p0.shares)-1):
        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.matMultList, args=(p.shares[c], p.shares[c+1]))
            threads[i].start()
            time.sleep(0.1)
    
    for t in threads:
        t.join(2)
    
    print("#######################################################")
    print("MATMULTLIST Test")
    print("MATRIX X:", X)
    print("Matrix Y:", Y)
    print("Result XY:", [matmod(s0+s1) for s0, s1 in zip(p0.matMultListResults[0], p1.matMultListResults[0])])
   
def test_connection():
    p0.sendInt("p2",100)
    print(p2.recvInt("p2"))
    p0.sendInt("p2",1000)
    print(p2.recvInt("p2"))
    p0.sendInt("p1",200)
    print(p1.recvInt("p1"))
    p0.sendInt("p1",12200)
    print(p1.recvInt("p2"))

    p1.sendInt("p2",10330)
    print(p2.recvInt("p2"))
    p1.sendInt("p2",12200)
    print(p2.recvInt("p2"))
    p1.sendInt("p0",100)
    print(p0.recvInt("p2"))
    p1.sendInt("p0",100)
    print(p0.recvInt("p2"))

    p2.sendInt("p1",1033330)
    print(p1.recvInt("p2"))
    p2.sendInt("p1",122040)
    print(p1.recvInt("p2"))
    p2.sendInt("p0",10330)
    print(p0.recvInt("p2"))
    p2.sendInt("p0",1300)
    print(p0.recvInt("p2"))



# test_matMultList() 
# test_matMult()
# test_bitDecomp()
# test_shareConvert()
test_computeMSB()
# test_mult()   
# test_privateCompare()
# test_multList()
# test_reconstruct2PC()
# test_MyType()
# test_connection()
# test_bitDecompOpt()
# test_bitDecompOpt_time()
# test_mult2()