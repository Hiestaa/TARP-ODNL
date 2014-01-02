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
		self.log = Log.Log('log/' + id +'.log.html')
		#self.log = Log.Log('log/last.log.html')
		self.log.log_init_tasklist(self.tasks)
		self.id = id


	def ontaskdone(self, task):
		self.taskcomplete += 1
		self.log.log_event_success(self.time, 'TaskEvent',"A task has been finished: " +str(task.id))

	def onopdone(self):
		self.log.log_event(self.time, 'TaskEvent', "An operation has been finished on first machine !")
		if len(self.tasks):
			task = self.tasks.pop(0)
			task.reinit()
			self.machinelist.assignTask(task, self.onopdone, self.ontaskdone)

	def run(self):
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