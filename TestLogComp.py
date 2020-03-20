def multShares(x,y):
    res = x*y % 2
    return 0, res




s = 201

p1 = 150
p2 = 51

sb = [1,1,0,0,1,0,0,1]

alice1 = [1,0,0,1,0,1,1,0]
alice0 = [0,0,0,0,0,0,0,0]

bob1 =   [0,0,0,0,0,0,0,0]
bob0 =   [0,0,1,1,0,0,1,1]    

a,b = multShares(alice1[7],bob0[7])
alicec_1_0 = [a]
alicec_1_1 = [a]

bobc_1_0 = [b]
bobc_1_1 = [b]

alicex_1_0 = [alice1[7]+alice0[7] % 2]
alicex_1_1 = [alice1[7]+alice0[7] % 2]

bobx_1_0 = [bob1[7]+bob0[7] % 2]
bobx_1_1 = [bob1[7]+bob0[7] % 2]


for i in range(6,-1,-1) :  
    a,b = multShares(alice1[i],bob0[i])
    alicec_1_0.insert(0,a)
    bobc_1_0.insert(0,b)
    alicec_1_1.insert(0,(a+alice1[i]+alice0[i])%2)
    bobc_1_1.insert(0,(b+bob1[i]+bob0[i])%2)
    alicex_1_0.insert(0,(alice1[i]+alice0[i])%2)
    alicex_1_1.insert(0,(alice1[i]+alice0[i])%2)
    bobx_1_0.insert(0,(bob1[i]+bob0[i])%2)
    bobx_1_1.insert(0,(bob1[i]+bob0[i]+1)%2)


alicec_2_0 
alicec_2_1



