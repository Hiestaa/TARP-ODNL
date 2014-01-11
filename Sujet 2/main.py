from Reader import *
from Evo import *

#pathList = Reader.readFile('JDD1.txt')
pathList = Reader.readFile('test.txt')
evo = Evo(pathList)
evo.run()
