class BigMat:
    def __init__(self,x):
        self.matrix = x

    def fromList(self,x):
        self.matrix = x

    def __matmul__(self, B):
        return BigMat([ [ self.matrix[0][0]*B.matrix[0][0]+self.matrix[0][1]*B.matrix[1][0] , self.matrix[0][0]*B.matrix[0][1]+self.matrix[0][1]*B.matrix[1][1] ] , 
                 [ self.matrix[1][0]*B.matrix[0][0]+self.matrix[1][1]*B.matrix[1][0] , self.matrix[1][0]*B.matrix[0][1]+self.matrix[1][1]*B.matrix[1][1] ] ])
    
    def __mul__(self,B):
        return BigMat([ [ self.matrix[0][0]*B , self.matrix[0][1]*B ] , 
                 [ self.matrix[1][0]*B , self.matrix[1][1]*B ] ]) 

    def __sub__(self,B):
        return BigMat([ [ self.matrix[0][0]-B.matrix[0][0] , self.matrix[0][1]-B.matrix[0][1] ] , 
                 [ self.matrix[1][0]-B.matrix[1][0] , self.matrix[1][1]-B.matrix[1][1] ] ]) 


    def __add__(self,B):
        return BigMat([ [ self.matrix[0][0]+B.matrix[0][0] , self.matrix[0][1]+B.matrix[0][1] ] , 
                 [ self.matrix[1][0]+B.matrix[1][0] , self.matrix[1][1]+B.matrix[1][1] ] ]) 

    def __mod__(self,M):
        return BigMat([ [ self.matrix[0][0] % M , self.matrix[0][1] % M ] , 
                 [ self.matrix[1][0] % M , self.matrix[1][1] % M ] ]) 