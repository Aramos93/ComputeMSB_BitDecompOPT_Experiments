from random import seed
from ComputeMSB import MyType
import random as rand


L = 4
N = 10
secrets = []
shares_0 = []
shares_1 = []
ZL = 2 ** L

zeroshares = False #set this false to get random shares. 0 shares easier for debugging

for i in range(N):
    secrets.append(rand.randint(0,ZL))


if zeroshares:
    shares_0 = secrets
    shares_1 = [0]*N
else:
    for i,x in enumerate(secrets):
        r = rand.randint(0,2*ZL)
        shares_1.append(MyType(r).x)
        shares_0.append(MyType(secrets[i] - r).x)

def writeSharesToFile():
    f0 = open("shares0.txt","w+")
    f1 = open("shares1.txt","w+")

    for s0,s1 in zip(shares_0, shares_1):
        f0.write("%d\n" % s0)
        f1.write("%d\n" % s1)
    
    f0.close()
    f1.close()

writeSharesToFile()

print(secrets)
print(shares_0)
print(shares_1)
print([sum(x) for x in zip(shares_0, shares_1)])


