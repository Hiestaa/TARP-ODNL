import numpy
import random
import pygame
import heapq
import pdb

from eval import Eval
from const import Const
from graphx import Graphx

class Evo :

	def __init__(self, pathList, dict_id):
		self.pathList = pathList
		self.evaluator = Eval(pathList)
		self.population = []
		self.dict_id = dict_id

		self.memory = [[] for x in range(10)]
		self.graphx = Graphx()
		self.colors = [
			pygame.color.Color(0, 255, 0, 0), # green = total
			#pygame.color.Color(128, 255, 0, 0),
			#pygame.color.Color(0, 255, 128, 0),
			#pygame.color.Color(128, 255, 255, 0),
			#pygame.color.Color(255, 255, 128, 0),
			#pygame.color.Color(255, 255, 0, 0),
			#pygame.color.Color(255, 128, 0, 0),
			#pygame.color.Color(255, 128, 0, 0),
			#pygame.color.Color(255, 128, 128, 0),
			#pygame.color.Color(255, 0, 0, 0),

			pygame.color.Color(255, 255, 0, 0), # yellow = NB_EMPL
			pygame.color.Color(0, 0, 255, 0),	# blue = PATH_INV
			pygame.color.Color(255, 0, 255, 0),	# magenta = OVER_DAY_LENGTH
			pygame.color.Color(255, 0, 0, 0),	# red = OVER_WORK_LENGTH
		]


	def eval(self, sol):
		return self.evaluator.eval(sol, self.dict_id)

	def run(self, it_max) :
		employees = []
		lenPathList = self.pathList.shape[0]
		for i in xrange(lenPathList):
			fiveEmp = []
			for k in xrange(5):
				emp = []
				for j in xrange(5):
					day = []
					emp.append(day)
				fiveEmp.append(emp)
			for j in xrange(5):
				fiveEmp[j][j].append(self.pathList[i][Const.ID_PATH])
			employees += fiveEmp

			# emp = []
			# for j in xrange(5):
			# 	day = [self.pathList[i][Const.ID_PATH]]
			# 	emp.append(day)
			# employees.append(emp)

		print employees

		heapq.heappush(self.population, (self.eval(employees),employees))

		# print 'employees', employees
		for i in xrange(it_max):

			if i > 3 and self.plot():
				break

			llen = len(self.population)
			pop = heapq.nsmallest(llen, self.population)
			for j in xrange(llen):
				for x in xrange(10):
					dupli = self.duplique(pop[j][1])
					while not self.mutation(dupli):
						pass
					heapq.heappush(self.population, (self.eval(dupli),dupli))

			#self.population = heapq.nsmallest(10, self.population)
			best = heapq.nsmallest(1, self.population)
			evalres = self.evaluator.eval_for_mem(best[0][1], self.dict_id)
			for m in xrange(5):
				print evalres[m],
				self.memory[m].append((5 + float(i - 1) / float(it_max) * 1024, 700 - (evalres[m]) / 300))
			print ""
			if i > 1:
				self.population = self.select2(10)

			print "Iteration: ", i, "Sol:\t", reduce(lambda a,b: str(a)+"\t"+str(b),map(lambda x: x[0], heapq.nsmallest(5, self.population)))

		self.evaluator.pp(heapq.nsmallest(1, self.population)[0][1], self.dict_id)
		print "Solution Value: ", heapq.nsmallest(1, self.population)[0][0]
		#self.evaluator.pp(heapq.nsmallest(2, self.population)[1][1])
		#print heapq.heappop(self.population)
		#print heapq.heappop(self.population)

		done = False
		while not done:
			done = self.plot()

	def select1(self, nb):
		newpop = []
		newpoplen = 0
		prev = None
		while newpoplen < nb and len(self.population) > 0:
			tmp = heapq.heappop(self.population)
			if prev is None or tmp[0] != prev[0]:
				heapq.heappush(newpop, tmp)
				prev = tmp
				newpoplen += 1
			elif not self.same(prev[1], tmp[1]):
				heapq.heappush(newpop, tmp)
				prev = tmp
				newpoplen += 1
		return newpop

	def select2(self, nb):
		newpop = []
		newpoplen = 0
		prev = None
		nb_best = 0
		best = None
		while newpoplen < nb and len(self.population) > 0:
			tmp = heapq.heappop(self.population)
			if best is None:
				best = tmp
			if prev is None or tmp[0] != prev[0]:
				heapq.heappush(newpop, tmp)
				prev = tmp
				if tmp[0] == best[0]:
					nb_best += 1
				newpoplen += 1
			elif not self.same(prev[1], tmp[1]):
				heapq.heappush(newpop, tmp)
				prev = tmp
				if tmp[0] == best[0]:
					nb_best += 1

		# selection aleatoire parmis les meilleurs
		lst = heapq.nsmallest(nb_best, newpop)
		tmp = nb/2
		if (tmp > nb_best):
			tmp = nb_best
		newpop2 = random.sample(lst, tmp)
		# selection aleatoire parmis les autres
		tmp = nb-tmp
		lst = heapq.nlargest(len(newpop) - nb_best, newpop)
		newpop2 = newpop2 + random.sample(lst, tmp)
		return newpop2

	def duplique(self, employees) :
		employeesDupli = []
		for employee in employees :
			tmpEmployee = []
			for jour in employee :
				tmpjour = []
				for i in xrange(len(jour)):
					tmpjour.append(jour[i])
				tmpEmployee.append(tmpjour)
			employeesDupli.append(tmpEmployee)
		return employeesDupli

	def mutation(self, employees) :
		# print 'mutation'
		ratio = len(employees) / len(self.pathList) * 5
		if random.random() < ratio :
			return self.moveOnePathOnAnotherEmployee(employees)
		else :
			rand = random.random() * 3
			if rand <= 1 :
				return self.swapOnEmployee(employees)
			elif rand <= 2 :
				return self.swapBetweenEmployee(employees)
			else :
				return self.moveOnePathOnAnotherEmployee(employees)

	def swapOnEmployee(self, employees) :
		# print 'swapOnEmployee'
		randEmployee = int(random.random() * len(employees))
		if randEmployee == len(employees) :
			randEmployee = randEmployee - 1
		# print 'randEmployee:', randEmployee

		randJour = int(random.random() * 5)
		if randJour == 5 :
			randJour = randJour - 1
		# print 'randJour:', randJour

		randPos1 = int(random.random() * len(employees[randEmployee][randJour]))
		if randPos1 == len(employees[randEmployee][randJour]) :
			randPos1 = randPos1 - 1
		# print 'randPos1:', randPos1

		randPos2 = int(random.random() * len(employees[randEmployee][randJour]))
		if randPos2 == len(employees[randEmployee][randJour]) :
			randPos2 = randPos2 - 1
		# print 'randPos2:', randPos2

		if len(employees[randEmployee][randJour]) == 0 or randPos1 == randPos2:
			# print 'no muted'
			return 0

		tmp = employees[randEmployee][randJour][randPos1]
		employees[randEmployee][randJour][randPos1] = employees[randEmployee][randJour][randPos2]
		employees[randEmployee][randJour][randPos2] = tmp

		return 1

	def swapBetweenEmployee(self, employees) :
		# print 'swapBetweenEmployee'
		if len(employees) == 1 :
			# print 'no muted'
			return 0

		randEmployee1 = int(random.random() * len(employees))
		if randEmployee1 == len(employees) :
			randEmployee1 = randEmployee1 - 1
		# print 'randEmployee1:', randEmployee1

		randEmployee2 = int(random.random() * len(employees))
		if randEmployee2 == len(employees) :
			randEmployee2 = randEmployee2 - 1
		# print 'randEmployee2:', randEmployee2

		if randEmployee1 == randEmployee2 :
			# print 'no muted'
			return 0

		randJour = int(random.random() * 5)
		if randJour == 5 :
			randJour = randJour - 1
		# print 'randJour:', randJour

		if len(employees[randEmployee1][randJour]) == 0 or len(employees[randEmployee2][randJour]) == 0 :
			# print 'no muted'
			return 0

		randPos1 = int(random.random() * len(employees[randEmployee1][randJour]))
		if randPos1 == len(employees[randEmployee1][randJour]) :
			randPos1 = randPos1 - 1
		# print 'randPos1:', randPos1

		randPos2 = int(random.random() * len(employees[randEmployee2][randJour]))
		if randPos2 == len(employees[randEmployee2][randJour]) :
			randPos2 = randPos2 - 1
		# print 'randPos2:', randPos2

		tmp = employees[randEmployee1][randJour][randPos1]
		employees[randEmployee1][randJour][randPos1] = employees[randEmployee2][randJour][randPos2]
		employees[randEmployee2][randJour][randPos2] = tmp

		return 1



	def moveOnePathOnAnotherEmployee(self, employees) :
		# print 'moveOnePathOnAnotherEmployee'
		if len(employees) == 1 :
			randEmployee1 = 0
			randEmployee2 = 1
			employees.append([[],[],[],[],[]])
			#print 'add employee first time'
		else :
			randEmployee1 = int(random.random() * len(employees))
			if randEmployee1 == len(employees) :
				randEmployee1 = randEmployee1 - 1


			randEmployee2 = int(random.random() * (len(employees) + 1))
			if randEmployee2 > len(employees) :
				randEmployee2 = randEmployee2 - 1

		if randEmployee1 != randEmployee2 :
			randJour = int(random.random() * 5)
			if randJour == 5 :
				randJour = randJour - 1
			# print 'randJour:', randJour

			if randEmployee2 == len(employees) :
				if len(employees[randEmployee1][randJour]) == 0 :
					# print 'no muted'
					return 0
				employees.append([[],[],[],[],[]])
				#print 'add employee'

			if len(employees[randEmployee1][randJour]) == 0 :
				if len(employees[randEmployee2][randJour]) > 0 :
					tmp = randEmployee1
					randEmployee1 = randEmployee2
					randEmployee2 = tmp
				else :
					# print 'No muted'
					return 0
			# print 'randEmployee1:', randEmployee1
			# print 'randEmployee2:', randEmployee2

			randPos1 = int(random.random() * len(employees[randEmployee1][randJour]))
			if randPos1 == len(employees[randEmployee1][randJour]) :
				randPos1 = randPos1 - 1
			# print 'randPos1:', randPos1

			randPos2 = int(random.random() * len(employees[randEmployee2][randJour]))
			# if randPos2 == len(employees[randEmployee2][randJour]) :
				# randPos2 = randPos2 - 1
			# print 'randPos2:', randPos2

			if randPos2 == len(employees[randEmployee2][randJour]) :
				employees[randEmployee2][randJour].append(employees[randEmployee1][randJour].pop(randPos1))
			else :
				employees[randEmployee2][randJour].insert(randPos2, employees[randEmployee1][randJour].pop(randPos1))

		if len(employees[randEmployee1][0]) == 0 and len(employees[randEmployee1][1]) == 0 \
			and len(employees[randEmployee1][2]) == 0 and len(employees[randEmployee1][3]) == 0 \
			and len(employees[randEmployee1][4]) == 0 :
				employees.pop(randEmployee1)
				#print 'delete employee'

		else :
			# print 'No muted'
			return 0
		return 1

	def same(self, sol1, sol2):
		if len(sol1) != len(sol2) :
			return 0
		for k in xrange(len(sol1)) :
			for i in xrange(5) :
				if len(sol1[k][i]) != len(sol2[k][i]) :
					return 0
			for i in xrange(5) :
				for j in xrange(len(sol1[k][i])) :
					if sol1[k][i][j] != sol2[k][i][j] :
						return 0
		return 1

	def plot(self):
		self.graphx.update()
		# self.graphx.draw_lines([(0, 700 - (self.upperbound - self.lowerbound)), (1024, 700 - (self.upperbound - self.lowerbound))],
		# 	color=pygame.color.Color('red'))
		# self.graphx.draw_lines([(0, 700 - (self.best_sol[0] - self.lowerbound)), (1024, 700 - (self.best_sol[0] - self.lowerbound))],
		# 	color=pygame.color.Color('green'))
		for m in xrange(5):
			self.graphx.draw_lines(self.memory[m], self.colors[m])
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				return True