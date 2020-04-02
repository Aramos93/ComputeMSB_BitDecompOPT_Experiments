import math
import time

class ComposeNet:
    def __init__(self,x):
        self.size = x
        self.numLayers = int(math.ceil(math.log(self.size-1,2))+1) 
        self.layers = [ [] for x in range(self.numLayers+1)]



        #first Layer
        for i in range(1,self.size):
            self.layers[1].append(self.ComposeNode(i,i))
        
    
        #All other layers
        for i in range(2,self.size):
            self.insert(self.ComposeNode(1,i))


    def exists(self, node):
            l = node.layer
            return node in self.layers[l]

    def get(self,node):
        for n in self.layers[node.layer]:
            if node.x == n.x and node.y == n.y:
                return n

    def insert(self, node):
        additive = 2**(node.layer-2)
        left = self.ComposeNode(node.x,node.x+additive-1)
        right = self.ComposeNode(node.x+additive,node.y)  

        if not self.exists(left):
            node.left = left
            self.insert(left)
        else:
            node.left = self.get(left)

        if not self.exists(right):
            node.right = right
            self.insert(right)
            
        else:
            node.right = self.get(right)

        self.layers[node.layer].append(node)

    def getMatrixResults(self):
        res = []
        for l in self.layers:
            for n in l:
                if(n.x == 1):
                    res.append(n.matrix)
                else:
                    continue
        return res
    
    class ComposeNode:
        def __init__(self,x,y):
            self.layer = self.getLayer(x,y)
            self.x = x
            self.y = y
            self.left = None
            self.right = None
            self.matrix = None

        def __eq__(self, other):
            return (self.x == other.x and self.y == other.y)

        
        def getLayer(self,x,y):
            if(x==y):
                return 1
            diff = y-x
            for i in range(1,10):
                if(2**i > diff):
                    #print(i+1)
                    return i+1
                