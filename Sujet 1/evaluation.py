from machine import Machine
from task import Task
import Log

import time



class Evaluation:
	def __init__(self, tasks, sequence, id):
		self.tasks = []
		for ti in sequence:
			self.tasks.append(tasks[ti])
		self.nbtasks = len(self.tasks)
		self.taskcomplete = 0
		self.machinelist = None
		self.time = 0
		self.log = None
		#self.log = Log.Log('log/last.log.html')
		self.id = id

	def fast(self) :
		tab = []
		for t in self.tasks:
			copytask = []
			for op in t.oplist:
				copytask.append(op)
			tab.append(copytask)
		nbLines = len(tab[0])
		nbColonnes = len(tab)

		i = 1
		while i < nbLines :
			tab[0][i] = tab[0][i - 1] + tab[0][i]
			i += 1

		j = 1
		while j < nbColonnes :
			tab[j][0] = tab[j - 1][0] + tab[j][0]
			i = 1
			while i < nbLines :
				if tab[j - 1][i] > tab[j][i - 1] :
					tmp = tab[j - 1][i]
				else :
					tmp = tab[j][i - 1]
				tab[j][i] = tab[j][i] + tmp
				i += 1
			j += 1
		return tab[nbColonnes - 1][nbLines - 1]


	def ontaskdone(self, task):
		self.taskcomplete += 1
		self.log.log_event_success(self.time, 'TaskEvent',"A task has been finished: " +str(task.id))

	def onopdone(self):
		self.log.log_event(self.time, 'TaskEvent', "An operation has been finished on first machine !")
		if len(self.tasks):
			task = self.tasks.pop(0)
			task.reinit()
			self.machinelist.assignTask(task, self.onopdone, self.ontaskdone)

	def simulation(self):
		self.log = Log.Log('log/' + id +'.log.html')
		self.log.log_init_tasklist(self.tasks)
		self.log.log_event_info(self.time, 'Execution', "Execution started !")
		task = self.tasks.pop(0)
		task.reinit()

		k = 0
		for op in task.oplist:
			m = Machine(k, self.log)
			k += 1
			if not self.machinelist:
				self.machinelist = m
			else:
				tmp = self.machinelist
				while tmp.next:
					tmp = tmp.next
				tmp.next = m
		self.log.log_event(self.time, 'Execution', str(self.machinelist.getNbMachines()) + " machines added to process operations.")

		self.machinelist.assignTask(task, self.onopdone, self.ontaskdone)

		while self.taskcomplete is not self.nbtasks:
			#print self.time,
			self.time += 1
			self.machinelist.update(self.time)

		self.log.log_event_success(self.time, 'Execution', "All tasks done, execution successfully done !")
		self.log.log_init_machines()
		m = self.machinelist
		while m:
			self.log.log_machine_state(m.id, m.total_working_time, m.total_waiting_time, m.work_history)
			m = m.next

		self.log.log_close()

		return self.time


if __name__ == '__main__':
	tasks = [
		Task(1, [10, 40, 30]),
		Task(2, [20, 50, 10]),
		Task(3, [1, 5, 10]),
		Task(4, [5, 20, 10]),
		Task(5, [10, 15, 5])
	]

	seq = [4, 3, 1, 2, 0]
	t = time.time()
	itern = Evaluation(tasks, seq).run()
	print ""
	print "Evaluation time: ", time.time() - t, "s"
	print "Evaluation result: ", itern, 'iterations'