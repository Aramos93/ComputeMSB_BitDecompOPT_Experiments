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
seed = random.randint(0,100)
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

########################################### Party (Create p0, p1, p2) Protocols are here #############################

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
        self.partyName = partyName
        self.shares = []
        self.converted_shares = []
        self.matMultResults = []
        self.msbResults = []
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

    
    ################ Send and Receive shares ###################
    def sendShares(self, sendTo, value):
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
    
    
    ############ Send and Receive single int ####################
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
            time.sleep(0.1)
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
        share0 = []
        share1 = []
        for i in range(L):
            num = int(x[i])
            r = random.randint(0,p)
            share1.append(r)
            share0.append((num - r) % p)

        return share0, share1
    
    # Generate shares in either ZL or Zl-1 of a number
    def generateMyTypeShares(self, x, in_zl=True):
        if in_zl == True:
            r = random.randint(0, 2**L)
        else:
            r = random.randint(0, (2**L)-1)

        return MyType(r, is_zl=in_zl), MyType(x-r, is_zl=in_zl)
    
    # Mimic private compare - actually just compares reconstructed value
    def dummyPC(self, x, r, beta):   
        return beta.x ^ (x.x > r.x) 
    
    def mult(self, x=MyType(0), y=MyType(0)):
        if self.party == "p0":
            shares_0 = literal_eval(self.recvShares("p0"))
            a = shares_0[0]; b = shares_0[1]; c = shares_0[2]
            e_0 = MyType(x.x - a)
            f_0 = MyType(y.x - b)
            e_f_shares_0 = [e_0.x, f_0.x]
            e_f_shares_1 = literal_eval(self.recvShares("p0"))
            self.sendShares("p1", e_f_shares_0)
            time.sleep(0.1) 
            e_1 = e_f_shares_1[0]; f_1 = e_f_shares_1[1]
            e = MyType(e_0.x + e_1); f = MyType(f_0.x + f_1)
            x_mult_y_0 = MyType(-self.partyName * e.x * f.x + x.x * f.x + e.x * y.x + c)
            self.matMultResults.append(x_mult_y_0)
            return x_mult_y_0
        
        if self.party == "p1":
            shares_1 = literal_eval(self.recvShares("p1"))
            a = shares_1[0]; b = shares_1[1]; c = shares_1[2]
            e_1 = MyType(x.x - a)
            f_1 = MyType(y.x - b)
            e_f_shares_1 = [e_1.x, f_1.x]
            self.sendShares("p0", e_f_shares_1)
            time.sleep(0.1)
            e_f_shares_0 = literal_eval(self.recvShares("p1"))    
            e_0 = e_f_shares_0[0]; f_0 = e_f_shares_0[1]
            e = MyType(e_0 + e_1.x); f = MyType(f_0 + f_1.x)
            x_mult_y_1 = MyType(-self.partyName * e.x * f.x + x.x * f.x + e.x * y.x + c)
            self.matMultResults.append(x_mult_y_1)
            return x_mult_y_1

        if self.party == "p2":
            a = MyType(random.randint(0,2**L))
            b = MyType(random.randint(0,2**L))
            c = MyType(a.x*b.x)
            a_0, a_1 = self.generateMyTypeShares(a.x)
            b_0, b_1 = self.generateMyTypeShares(b.x)
            c_0, c_1 = self.generateMyTypeShares(c.x)
            shares_0 = [a_0.x, b_0.x, c_0.x]; shares_1 = [a_1.x, b_1.x, c_1.x]
            self.sendShares("p0", shares_0); self.sendShares("p1", shares_1)
            time.sleep(0.1)

             
        
    # Convert a shares of some value a in ZL to shares of the same value in ZL-1
    def shareConvert(self, a=MyType(0)):
        if self.party == "p0" or self.party == "p1":
            rec = self.reconstruct2PCSingleInt(a) # This reconstruction is only to check value of a

        # Use same random seed to ensure all parties share same common randomness: r, r_0, r_1, n''
        random.seed(seed)
        n_prime_prime = MyType(random.randint(0,1))
        r = MyType(random.randint(1,2**L)) #can't be 0 for some reason. Probably handled in PC which we don't implement

        r_0, r_1 = self.generateMyTypeShares(r.x)
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
            delta_0, delta_1 = self.generateMyTypeShares(delta, False)

            self.sendShares("p0", x_bit_arr_0); self.sendShares("p1", x_bit_arr_1)
            time.sleep(0.1)
            self.sendInt("p0", delta_0.x); self.sendInt("p1", delta_1.x)
            time.sleep(0.1)

            n_prime = self.dummyPC(x, r-MyType(1), n_prime_prime)
            n_prime_0, n_prime_1 = self.generateMyTypeShares(n_prime,False)
           

            self.sendInt("p0", n_prime_0.x); self.sendInt("p1", n_prime_1.x)
    

    def computeMSB(self, a=MyType(0)):
        if self.party == "p0" or self.party == "p1":
            rec = self.reconstruct2PCSingleInt(a)
        random.seed(seed)
        beta = MyType(random.randint(0,1),is_zl=False)
        

        if self.party == "p0":
            #if rec.x >= ((2**L) - 1):
             #   raise Exception(f"Reconstructed value 'a' is {rec.x} which is NOT in ZL-1 {(2**L) -1}")
            x_0 = MyType(self.recvInt("p0"), is_zl=False)   
            x_bit_arr_0 = self.recvShares("p0")
            x_firstBit_0 = self.recvInt("p0")
            #print(f"p0 received: x_0 {x_0.x}, x_bit_arr_0 {x_bit_arr_0}, xfirstbit {x_firstBit_0}")
            y_0 = MyType(2*a.x, is_zl=False) 
            r_0 = MyType(y_0.x - x_0.x, is_zl=False)  
            r_1 = MyType(self.recvInt("p0"), is_zl=False)   
            self.sendInt("p1", r_0.x)
            time.sleep(0.1)             
            r = MyType(r_0.x + r_1.x, is_zl=False)

            # print("p0 a: ", a.x)
            # print("p0 x_0: ", x_0.x)
            # print("p0 y_0: ", y_0.x)
            # print("p0 r_0: ", r_0.x)
            # print("p0 r_1: ", r_1.x)
            #print("p0 r: ", r.x)

            beta_prime_0 = MyType(self.recvInt("p0"))
            gamma_0 = MyType(beta_prime_0.x + self.partyName * beta.x - 2 * beta.x * beta_prime_0.x)
            delta_0 = MyType(x_firstBit_0 + self.partyName * int(bin(r.x)[-1]) - 2 * int(bin(r.x)[-1]) * x_firstBit_0)
            print(f"p0 mult: {gamma_0.x}, {delta_0.x}")

            theta_0 = self.mult(gamma_0, delta_0)
            print("p0 multres: ", theta_0.x)
            alpha_0 = MyType(gamma_0.x + delta_0.x - 2 * theta_0.x)
            self.msbResults.append(alpha_0)
            return alpha_0

        if self.party == "p1":      
            x_1 = MyType(self.recvInt("p1"), is_zl=False) 
            x_bit_arr_1 = self.recvShares("p1")
            x_firstBit_1 = self.recvInt("p1")
            #print(f"p1 received: x_1 {x_1.x}, x_bit_arr_1 {x_bit_arr_1}, xfirstbit {x_firstBit_1}")
            y_1 = MyType(2*a.x, is_zl=False)    
            r_1 = MyType(y_1.x - x_1.x, is_zl=False)    
            self.sendInt("p0", r_1.x)
            time.sleep(0.1)
            r_0 = MyType(self.recvInt("p1"), is_zl=False)     
            r = MyType(r_0.x + r_1.x, is_zl=False)

            # print("p1 a: ", a.x)
            # print("p1 x_1: ", x_1.x)
            # print("p1 y_1: ", y_1.x)
            # print("p1 r_1: ", r_1.x)
            # print("p1 r_0: ", r_0.x)
            #print("p1 r: ", r.x)

            self.sendInt("p2", r.x) #Doesn't actually happen in protocol, but p2 needs to dummy PC
            time.sleep(0.1)

            beta_prime_1 = MyType(self.recvInt("p1"))
            gamma_1 = MyType(beta_prime_1.x + self.partyName * beta.x - 2 * beta.x * beta_prime_1.x)
            delta_1 = MyType(x_firstBit_1 + self.partyName * int(bin(r.x)[-1]) - 2 * int(bin(r.x)[-1]) * x_firstBit_1)
            print(f"p1 mult: {gamma_1.x}, {delta_1.x}")

            theta_1 = self.mult(gamma_1, delta_1)
            print("p1 multres: ", theta_1.x)
            alpha_1 = MyType(gamma_1.x + delta_1.x - 2 * theta_1.x)
            self.msbResults.append(alpha_1)
            return alpha_1

        if self.party == "p2":
            #x = MyType(random.randint(0, (2**L) - 1), is_zl=False)
            x = MyType(8, is_zl=False)
            x_0, x_1 = self.generateMyTypeShares(x.x, in_zl=False)
            bin_x = self.convertToBitString(x)
            x_bit_arr_0, x_bit_arr_1 = self.generateBitShares(bin_x)
            x_firstBit_0, x_firstBit_1 = self.generateMyTypeShares(int(bin_x[-1]))
            # print(x.x)
            # print(x_0.x,x_1.x)
            # print(bin_x)
            # print(x_bit_arr_0, x_bit_arr_1)
            # print(x_firstBit_0.x, x_firstBit_1.x)
          
            self.sendInt("p0", x_0.x); self.sendInt("p1", x_1.x)
            time.sleep(0.1)
            self.sendShares("p0", x_bit_arr_0); self.sendShares("p1", x_bit_arr_1)
            time.sleep(0.1)
            self.sendInt("p0", x_firstBit_0.x); self.sendInt("p1", x_firstBit_1.x)
            time.sleep(0.1)
            r = MyType(self.recvInt("p2"), is_zl=False)
            #print("p2 r: ", r.x)
            beta_prime = self.dummyPC(x, r, beta)
            beta_prime_0, beta_prime_1 = self.generateMyTypeShares(beta_prime)
            self.sendInt("p0", beta_prime_0.x); self.sendInt("p1", beta_prime_1.x)
            self.mult()






  
######################################################################################################################    



####################################################### Tests ########################################################

parties = []
p0 = Party(0); p1 = Party(1); p2 = Party(2)
parties.append(p0); parties.append(p1)

def test_MyType():
    testListInput = [8,20,16,0,-3]
    testListRes = []
    for e in testListInput:
        testListRes.append(MyType(e).x)
    print(testListRes)


def test_Party():
    p0 = Party(0)
    print("p0 shares: ", p0.getShareVals())
    p1 = Party(1)
    print("p1 shares: ", p1.getShareVals())
    p2 = Party(2)
    print("p2 shares (empty): ", p2.shares)

def test_reconstruct2PC():
    print(p0.getShareVals()); print(p1.getShareVals())
    for p in parties:
        thread = threading.Thread(target=p.reconstruct2PC,args=())
        thread.start()

def test_shareConvert():
    for c in range(len(p0.shares)):

        thread = threading.Thread(target=p2.shareConvert, args=())
        thread.start()
        time.sleep(0.1)

        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.shareConvert, args=(p.shares[c],))
            threads[i].start()
            time.sleep(0.1)
        
        for p,t in zip(parties, threads):
            t.join(2)
        thread.join(2)
        #print("")
    print("Shares in ZL")    
    print([s.x for s in p0.shares])
    print([s.x for s in p1.shares])
    print("Reconstructed: ", [(s0+s1).x for s0,s1 in zip(p0.shares,p1.shares)])
    print()
    print("Shares in ZL-1")
    print([s.x for s in p0.converted_shares])
    print([s.x for s in p1.converted_shares])
    print("Reconstructed: ", [MyType(s0.x+s1.x, is_zl=False).x for s0,s1 in zip(p0.converted_shares,p1.converted_shares)])


def test_computeMSB():
    
    p0.converted_shares = [MyType(2),MyType(1),MyType(3),MyType(7),MyType(10),MyType(2),MyType(3),MyType(7),MyType(5),MyType(11)]
    p1.converted_shares = [MyType(10),MyType(7),MyType(11),MyType(14),MyType(5),MyType(12),MyType(12),MyType(0),MyType(10),MyType(7)]
        
    for c in range(len(p0.shares)):
        threads = [None]*len(parties)
        for i, p in enumerate(parties):
            threads[i] = threading.Thread(target=p.computeMSB, args=(p.converted_shares[c],))
            threads[i].start()
            time.sleep(0.1)
        
        thread = threading.Thread(target=p2.computeMSB, args=())
        thread.start()

        for t in threads:
            t.join(5)
        thread.join(5)
      

    print("MSB inputs: ", [MyType(s0.x+s1.x, is_zl=False).x for s0,s1 in zip(p0.converted_shares,p1.converted_shares)])
    print("MSB inputs in binary: ", [p0.convertToBitString(MyType(s0.x+s1.x,is_zl=False)) for s0,s1 in zip(p0.converted_shares,p1.converted_shares)])
    print("MSB results")
    print(len(p0.msbResults), len(p1.msbResults))
    print("alpha0 values: ", [s.x for s in p0.msbResults])
    print("alpha1 values: ", [s.x for s in p1.msbResults])
    print("Reconstructed MSB: ", [MyType(s0.x+s1.x).x for s0,s1 in zip(p0.msbResults,p1.msbResults)])

def test_mult():
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
        print("")

#test_shareConvert()
test_computeMSB()
#test_mult()
#test_Party()    
#test_reconstruct2PC()
#test_MyType()
