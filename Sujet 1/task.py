class Task:
	"""Represente une tach a executer"""
	def __init__(self, tid, oplist):
		self.oplist = oplist
		self.id = tid
		self.opnum = len(oplist)
		self.opdone = 0

	def reinit(self):
		self.opdone = 0

	def add_operation(self, optime):
		self.oplist.append(optime)
		self.opnum += 1

	def op_done(self):
		self.opdone += 1

	def get_next_op(self):
		#print "task:", self.id, "opdone: ", self.opdone
		if self.opdone < self.opnum:
			return self.oplist[self.opdone]
		else:
			return None
