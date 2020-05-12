import ctypes
import pyparsenames as pn
import sys

so_file = 'parsenames.so'

parsenames = ctypes.CDLL(so_file)

parsenames.gender.restype = ctypes.c_char
parsenames.gender.argtypes = [ctypes.POINTER(ctypes.c_char), ]

def closeMatches(name):
    ca = parsenames.gender(name.encode("utf-8")).decode("utf-8")
    if ca!='E':
        return [ca]
    else:
        a = pn.closeMatches(name)
        return a
  

if __name__=="__main__":
    from datetime import datetime
    if len(sys.argv)==1:
        print("Usage : python parsenames_optimized.py <name>")
        sys.exit()
    startt = datetime.now()
    print(closeMatches(sys.argv[1])) 
    print(datetime.now() - startt)
