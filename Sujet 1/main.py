from tabu import Tabu
import sys
import time

if len(sys.argv) < 2:
	print "Please specify the number of iterations: ./main.py 1000"
	exit(1)
else:
	print sys.argv[0], sys.argv[1]

t = time.time()
#Tabu('test2.txt').run(int(sys.argv[1]))
Tabu('PB20x5_1.txt').run(int(sys.argv[1]))

#Tabu('PB50x10_1.txt').run(int(sys.argv[1]))


#Tabu('PB100x10_1.txt').run(int(sys.argv[1]))

print "Executed in: ", str(time.time() - t), "s."
