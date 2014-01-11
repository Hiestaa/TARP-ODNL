from Reader import *
from Evo import *

pathList = Reader.readFile('JDD1.txt')
evo = Evo(pathList)
evo.run()
