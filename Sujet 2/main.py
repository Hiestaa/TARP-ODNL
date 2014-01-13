from Reader import *
from Evo import *
import sys
import time

if len(sys.argv) < 3:
	print "Please specify the number of iterations: ./main.py 1000 JDD1.txt"
	exit(1)
# else:
	# print sys.argv[0], sys.argv[1]

pathList, dict_id = Reader.readFile(sys.argv[2])
#pathList = Reader.readFile('test.txt')
evo = Evo(pathList, dict_id)
t = time.time()
evo.run(int(sys.argv[1]))
print "Executed in: ", time.time() - t, "s"