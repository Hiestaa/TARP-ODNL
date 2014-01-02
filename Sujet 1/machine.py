import Log
from task import Task

class Machine:
	"""Represente une machine capable d'executer une operation
	De plus, assigner une tache a un machine sous la forme d'une liste d'operation
	permet d'automatiser le passage de l'operation suivante a la machine suivante lorsque l'operation courante est terminee"""
	def __init__(self, mid, log):
		self.id = mid
		self.next = None # prochaine machine de la liste
		self.currentoptime = 0 # temps total necessaire pour l'operation en cours
		self.currentopstate = 0 # etat du travail sur l'operation en cours
		self.working = False # la machine est-elle en train de travailler ?
		self.currenttask = None
		self.waitingtask = []
		self.onopdone = None # callback a appeler lorsque l'operation est terminee
		self.ontaskdone = None # callback a appeler lorsque la tache est terminee
		self.time = 0

		self.total_working_time = 0
		self.total_waiting_time = 0
		self.work_history = [] # list of tupples (taskid, opid, time of work)
		self.log = log

	def assignTask(self, task, onopdone, ontaskdone):
		self.log.log_event(self.time, "MachineEvent",  "Machine "+str(self.id)+": assign task "+str(task.id)+" operation "+str(task.opdone))
		self.currenttask = task
		self.assign_operation(self.currenttask.get_next_op())
		self.start()
		self.onopdone = onopdone
		self.ontaskdone = ontaskdone

		self.work_history.append((task.id, task.opdone, self.currentoptime))

	def assign_operation(self, optime):
		self.log.log_event(self.time, "MachineEvent",  "Machine "+str(self.id)+": assign op time="+str(optime))
		self.currentoptime = optime
		self.currentopstate = optime
		self.working = False

	def start(self):
		self.working = True

	def on_next_op_done(self):
		if self.waitingtask:
			task = self.waitingtask.pop(0)
			self.next.assignTask(task, self.on_next_op_done, self.ontaskdone)

	def update(self, time):
		self.time = time

		if self.working:
			self.total_working_time += 1
			# if machine is working, decrease current op counter
			self.currentopstate -= 1
			if self.currentopstate == 0:
				# the machine ended it's work

				# log that the operation has finished
				self.log.log_event_info(time, 'MachineEvent', "Machine " + str(self.id) +
					" just finished task " + str(self.currenttask.id) +
					" operation " + str(self.currenttask.opdone) +
					" (time: " + str(self.currentoptime)+')')

				if self.next:
					# notify task that it is complete
					self.currenttask.op_done()
					# add to the fifo  of task waiting for the next machine to be free
					self.waitingtask.append(self.currenttask)
				else:
					# if next is None, this is the last machine of the chain
					# notify that the current task is done
					self.ontaskdone(self.currenttask)

				# note that we are not working anymore
				self.working = False
				# notify that the operation is done and machine is free
				self.onopdone()
		else:
			self.total_waiting_time += 1
		# if there is a machine after this
		if self.next:
			# update the machine
			self.next.update(self.time)
			if self.waitingtask and self.next.working == False:
				# assign the first
				task = self.waitingtask.pop(0)
				self.next.assignTask(task, self.on_next_op_done, self.ontaskdone)

	def getNbMachines(self):
		if not self.next:
			return 1
		else:
			return 1 + self.next.getNbMachines()



