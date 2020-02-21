import random

############# Globals ##########
L = 5


class Ring_ZL:
    def __init__(self, x):
        self.L = L
        self.x = x % (2 ** self.L)








def test_Ring_ZL():
    testListInput = [8,20,16,0,-3]
    testListRes = []
    for e in testListInput:
        testListRes.append(Ring_ZL(e).x)

    for x in testListRes:
        print(x)

test_Ring_ZL()