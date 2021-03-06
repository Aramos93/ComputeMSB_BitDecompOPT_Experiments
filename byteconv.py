
#Helper class to convert matrices in modulo 2 to byte representation to lower communication overhead.

#Takes a matrix and extracts bits, and converts to bytes.
def mattobyte(mat):
    bitstring = "0000"+str(mat[0][0])+str(mat[0][1])+str(mat[1][0])+str(mat[1][1])
    return bytes([int(bitstring,2)])

#Takes an integer and gets the 8 bit representation, then returns the 4 least significant bits and adds them to a matrix.
def inttomat(b):
    bitarray = format(b,'b').zfill(8)
    return [ [int(bitarray[4]),int(bitarray[5])] , [int(bitarray[6]),int(bitarray[7])] ]


#Takes a list of lists of matrices and converts them to a bytestring.
def makebytes(twolists):
    one = twolists[0]
    two = twolists[1]
    res = b''+bytes([len(one)])+bytes([len(two)])
    
    for mat in one:
        res = res+mattobyte(mat)
    
    for mat in two:
        res = res+mattobyte(mat)
    return res

#Takes a bytestring and converts it to a list of lists of matrices.
def makemats(bytes):
    one = []
    two = []
    len_one = bytes[0]
    len_two = bytes[1]
    for i in range(2,2+len_one):
        one.append(inttomat(bytes[i]))
    for i in range(2+len_one,2+len_one+len_two):
        two.append(inttomat(bytes[i]))
    return [one,two]

