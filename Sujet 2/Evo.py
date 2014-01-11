import numpy
import random

from eval import Eval

class Evo :

	def __init__(self, pathList):
		self.pathList = pathList
		self.evaluator = Eval(pathList)

	def eval(self, sol):
		self.evaluator.eval(sol)

	def run(self) :
		employees = []
		firstEmploye = []
		lenPahtList = self.pathList.shape[0]
		for j in xrange(5) :
			jour = []
			for i in xrange(lenPahtList) :
				jour.append(i % lenPahtList)
			firstEmploye.append(jour)
		# print firstEmploye
		employees.append(firstEmploye)
		self.eval(employees)
		# print 'employees', employees
		dupli = self.duplique(employees)
		print 'dupli', dupli
		for i in xrange(2) :
			self.mutation(dupli)
		print 'muted', dupli


	def duplique(self, employees) :
		employeesDupli = []
		for employee in employees :
			tmpEmployee = []
			for jour in employee :
				tmpjour = []
				for i in xrange(len(jour)) :
					tmpjour.append(jour[i])
				tmpEmployee.append(tmpjour)
			employeesDupli.append(tmpEmployee)
		return employeesDupli

	def mutation(self, employees) :
		# print 'mutation'
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
			print 'add employee first time'
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
				print 'add employee'

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
				print 'delete employee'

		else :
			# print 'No muted'
			return 0
		return 1


