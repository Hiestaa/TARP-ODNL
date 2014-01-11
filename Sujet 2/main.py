from Reader import *
from Evo import *
import sys
import time

if len(sys.argv) < 2:
	print "Please specify the number of iterations: ./main.py 1000"
	exit(1)
else:
	print sys.argv[0], sys.argv[1]

pathList = Reader.readFile('JDD1.txt')
#pathList = Reader.readFile('test.txt')
evo = Evo(pathList)
t = time.time()
evo.run(int(sys.argv[1]))
print "Executed in: ", time.time() - t, "s"