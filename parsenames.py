from difflib import get_close_matches
import sys


filename='names/yob2018.txt'
with open(filename, 'r') as f:
    data = f.read()

data = data.split(sep='\n')
for i, line in enumerate(data):
    data[i] = line.split(sep=',')

patterns = [i[0] for i in data]


def closeMatches(name):
    matshes = get_close_matches(name, patterns)
    if len(matshes)>0:
        ind = patterns.index(matshes[0])
        return data[ind][1]
    else:
        return None

if __name__=='__main__':
    if len(sys.argv)==1:
        print('Usage: python parsenames.py <name>')
        sys.exit();
    print(closeMatches(sys.argv[1]))
