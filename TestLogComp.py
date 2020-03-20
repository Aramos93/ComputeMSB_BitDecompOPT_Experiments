def multShares(x0,x1,y0,y1):
    res = ((x0+x1)%2)*((y0+y1)%2) % 2
    return 0, res




s = 201

p1 = 150
p2 = 51

sb = [1,1,0,0,1,0,0,1]

alice1 = [1,0,0,1,0,1,1,0]
alice0 = [0,0,0,0,0,0,0,0]

bob1 =   [0,0,0,0,0,0,0,0]
bob0 =   [0,0,1,1,0,0,1,1]    

a,b = multShares(alice1[7],alice0[7],bob0[7],bob1[7])
alicec_1_0 = [a]
alicec_1_1 = [a]

bobc_1_0 = [b]
bobc_1_1 = [b]

alicex_1_0 = [alice1[7]+alice0[7] % 2]
alicex_1_1 = [alice1[7]+alice0[7] % 2]

bobx_1_0 = [bob1[7]+bob0[7] % 2]
bobx_1_1 = [bob1[7]+bob0[7] % 2]


for i in range(6,-1,-1) :  
    a,b = multShares(alice1[i],alice0[i],bob0[i],bob1[i])
    alicec_1_0.insert(0,a)
    bobc_1_0.insert(0,b)
    alicec_1_1.insert(0,(a+alice1[i]+alice0[i])%2)
    bobc_1_1.insert(0,(b+bob1[i]+bob0[i])%2)
    alicex_1_0.insert(0,(alice1[i]+alice0[i])%2)
    alicex_1_1.insert(0,(alice1[i]+alice0[i])%2)
    bobx_1_0.insert(0,(bob1[i]+bob0[i])%2)
    bobx_1_1.insert(0,(bob1[i]+bob0[i]+1)%2)

a,b = multShares(alice0[6],alice1[6],bob0[6],bob1[6])
toalice = a^(alice0[6]*alicec_1_0[7])^(alice1[6]*alicec_1_0[7])
tobob = b^(bob0[6]*bobc_1_0[7])^(bob1[6]*bobc_1_0[7])
alicec_2_0 = [[toalice,alicec_1_0[7]]]
alicec_2_1 = [[toalice,alicec_1_0[7]]]
bobc_2_0 = [[tobob,bobc_1_0[7]]]
bobc_2_1 = [[tobob,bobc_1_0[7]]]

for i in range(4,-1,-2) :
    a,b = multShares(alice0[i],alice1[i],bob0[i],bob1[i])

    toalice = a^(alice0[i]*alicec_1_0[i+2])^(alice1[i]*alicec_1_0[i+2])
    tobob = b^(bob0[i]*bobc_1_0[i+2])^(bob1[i]*bobc_1_0[i+2])
    alicec_2_0.insert(0,[alicec_1_0[i],alicec_1_0[i+1]])
    bobc_2_0.insert(0,[bobc_1_0[i],bobc_1_0[i+1]])

    toalice = a^(alice0[i]*alicec_1_1[i+2])^(alice1[i]*alicec_1_1[i+2])
    tobob = b^(bob0[i]*bobc_1_1[i+2])^(bob1[i]*bobc_1_1[i+2])
    alicec_2_1.insert(0,[alicec_1_1[i],alicec_1_1[i+1]])
    bobc_2_1.insert(0,[bobc_1_1[i],bobc_1_1[i+1]])
        
