from evaluation import Evaluation
from task import Task

class Remi:
	def __init__(self, input_file):
		self.input_file = input_file
		self.nb_op = 0
		self.nb_tasks = 0
		self.seed = 0
		self.upperbound = 0
		self.lowerbound = 0
		self.tasks = []
		self.parse_input()

	def parse_input(self):
			f = open(self.input_file, 'r')
			f.readline() # jump header definition
			conf = f.readline()
			conf = conf.split()
			self.nb_tasks = int(conf[0])
			self.nb_op = int(conf[1])
			self.seed = int(conf[2])
			self.upperbound = int(conf[3])
			self.lowerbound = int(conf[4])

			f.readline() # jump header definitions

			for i in range(self.nb_tasks):
				# initializing each task with an empty list of operation
				self.tasks.append(Task(i, []))

			for i in range(self.nb_op):
				op = f.readline() # get the ith job for each task
				op = op.split()
				for j in range(self.nb_tasks):
					self.tasks[j].add_operation(int(op[j]))
			f.close()

	def eval(self, seq):
		print (Evaluation(self.tasks, seq, reduce(lambda a,b: str(a)+"-"+str(b), seq)).simulation(), seq)

r = Remi('PB20x5_1.txt')
r.eval([8,14,5,16,3,2,18,13,17,7,15,10,12,4,6,0,1,9,19,11])
r.eval([8,14,0,2,10,5,18,16,13,4,3,1,12,17,6,7,15,9,19,11])
r.eval([8,14,5,4,7,3,18,13,2,17,15,16,6,10,12,0,1,9,19,11])
r.eval([16,8,14,13,2,7,10,12,17,15,4,5,6,0,18,3,1,9,19,11])