from const import Const

### L'evaluation se fait en plusieurs passes:
###		1 - PATH_INV = nombre de trajets invalides en terme de correspondance
###		3 - NB_EMPL = nombre total d'employes de la solution
###		4 - OVER_DAY_LEN = cumul du temps passe en heures sup de tous les employes sur tous les jours
###		5 - OVER_WORK_LEN = cumul du temps passe en heures travaillees en trop pour tous les employes sur tous les jours
### Pour optimiser au maximum, l'evaluation se fait par callbacks. Chaque element de la solution est parcouru une seule et unique fois.
class Eval:
	def __init__(self, pathlist):
		self.pathList = pathlist
		self.init_compute()

	def init_compute(self):
		self.NB_EMPL = 0
		self.PATH_INV = 0
		self.OVER_DAY_LEN = 0
		self.OVER_WORK_LEN = 0

		# temps de travail total dans la journee pour l'employe courant
		self.cur_empl_day_len = 0
		# temps total travaille dans la journee pour l'employe courant
		self.cur_empl_work_len = 0
		self.cur_day = None # jour en cours de traitement

		# sauvegarde l'heure de debut du premier trajet de la journee
		self.day_start_time = None
		# sauvegarde l'heure de fin du dernier trajet de la journee
		self.day_end_time = None

		# au cours de l'analyse, arrive du precedent trajet
		self.last_path_end_loc = None
		self.last_path_end_time = None
		self.day_nb_path = 0

	def eval(self, sol):
		self.init_compute()
		for x in range(len(sol)): # for each employee
			self.onNewEmployee(x)
			for y in range(len(sol[x])): # for each day
				self.onNewDay(y)
				for z in range(len(sol[x][y])): # for each path
					self.onNextPath(z, self.pathList[sol[x][y][z]][Const.START_LOC], self.pathList[sol[x][y][z]][Const.END_LOC],
						self.pathList[sol[x][y][z]][Const.START_HOUR] * 60 + self.pathList[sol[x][y][z]][Const.START_MIN],
						self.pathList[sol[x][y][z]][Const.END_HOUR] * 60 + self.pathList[sol[x][y][z]][Const.END_MIN])
				self.onEndDay()

		return self.NB_EMPL * 400 + self.PATH_INV * 1000 + self.OVER_DAY_LEN * 10 + self.OVER_WORK_LEN * 10

	def eval_for_mem(self, sol):
		self.init_compute()
		for x in range(len(sol)): # for each employee
			self.onNewEmployee(x)
			for y in range(len(sol[x])): # for each day
				self.onNewDay(y)
				for z in range(len(sol[x][y])): # for each path
					self.onNextPath(z, self.pathList[sol[x][y][z]][Const.START_LOC], self.pathList[sol[x][y][z]][Const.END_LOC],
						self.pathList[sol[x][y][z]][Const.START_HOUR] * 60 + self.pathList[sol[x][y][z]][Const.START_MIN],
						self.pathList[sol[x][y][z]][Const.END_HOUR] * 60 + self.pathList[sol[x][y][z]][Const.END_MIN])
				self.onEndDay()

		return (self.NB_EMPL * 400 + self.PATH_INV * 1000 + self.OVER_DAY_LEN * 10 + self.OVER_WORK_LEN * 10,
			self.NB_EMPL * 400, self.PATH_INV * 1000, self.OVER_DAY_LEN * 10, self.OVER_WORK_LEN * 10)

	def pp(self, sol):
		self.init_compute()
		for x in range(len(sol)): # for each employee
			print "Employee: ", x
			self.onNewEmployee(x)
			for y in range(len(sol[x])): # for each day
				print "\tDay: ", y
				self.onNewDay(y)
				for z in range(len(sol[x][y])): # for each pathlist
					print "\t\tTrajet: ", z
					print "\t\t\tStart:", chr(self.pathList[sol[x][y][z]][Const.START_LOC]), "End: ", chr(self.pathList[sol[x][y][z]][Const.END_LOC])
					print "\t\t\tStart time:", str(self.pathList[sol[x][y][z]][Const.START_HOUR])+":"+str(self.pathList[sol[x][y][z]][Const.START_MIN]),
					print "End time: ", str(self.pathList[sol[x][y][z]][Const.END_HOUR])+":"+str(self.pathList[sol[x][y][z]][Const.END_MIN])
					self.onNextPath(z, self.pathList[sol[x][y][z]][Const.START_LOC], self.pathList[sol[x][y][z]][Const.END_LOC],
						self.pathList[sol[x][y][z]][Const.START_HOUR] * 60 + self.pathList[sol[x][y][z]][Const.START_MIN],
						self.pathList[sol[x][y][z]][Const.END_HOUR] * 60 + self.pathList[sol[x][y][z]][Const.END_MIN],
						True)
				self.onEndDay(True)
		print "cur_empl_days_len: ", self.cur_empl_days_len

		print "NB_EMPL=", self.NB_EMPL
		print "PATH_INV=", self.PATH_INV
		print "OVER_DAY_LEN=", self.OVER_DAY_LEN
		print "OVER_WORK_LEN=", self.OVER_WORK_LEN
		print "sol: ", sol

	def onNewEmployee(self, empl):
		# compte un employe de plus
		self.NB_EMPL += 1
		# reinitialise les compteurs de temps des employes
		# reinitialise la sauvegarde de lieu d'arrivee du dernier trajet
		self.last_path_end_loc = None


	def onNewDay(self, day):
		#
		# l'heure du trajet precedent ne sera pas pris en compte pour le premier trajet du nouveau jour
		self.last_path_end_time = None
		self.cur_day = day
		self.day_start_time = None
		self.day_stop_time = None
		self.cur_empl_day_len = 0
		self.cur_empl_work_len = 0
		self.day_end_time = None
		self.day_nb_path = 0

	def onEndDay(self, pp=False):
		# sauvegarde le temps total de travail de la journee passee
		if self.day_start_time is not None and self.day_end_time is not None:
			self.cur_empl_days_len = self.day_end_time - self.day_start_time
			if pp:
				print "\tDay length:", str(self.cur_empl_days_len / 60)+":"+str(self.cur_empl_days_len % 60)
		else:
			self.cur_empl_days_len = 0
		# note : pour l'instant, l'evaluation ne tient pas compte du cout des journees trop chomees
		if self.cur_empl_days_len > 420:
			self.OVER_DAY_LEN += self.cur_empl_days_len - 420
			if pp:
				print "\t\tDay is TOO LONG :", self.cur_empl_days_len, " - 420 =", self.cur_empl_days_len - 420
		if self.cur_empl_work_len > 300:
			self.OVER_WORK_LEN += self.cur_empl_work_len - 300
			if pp:
				print "\t\tDay has TOO MUCH WORK of:", self.cur_empl_work_len, " - 300 = ", self.cur_empl_work_len - 300

		if self.day_nb_path == 0:
			self.last_path_end_loc = None


	def onNextPath(self, id, start_loc, end_loc, start_time, end_time, pp=False):
		self.day_nb_path += 1
		if self.onNextPathLocCheck(start_loc, end_loc, pp):
			self.onNextPathTimeCheck(start_time, end_time, pp)

	def onNextPathLocCheck(self, start_loc, end_loc, pp):
		# si un trajet a deja ete effectue
		if self.last_path_end_loc is not None:
			# si le lieu de fin du trajet precedent n'est pas le meme que le suivant
			if start_loc != self.last_path_end_loc:
				if pp:
					print "\t\t\t\tStart loc:", chr(start_loc), "is not", chr(self.last_path_end_loc), ": INVALID !"
				self.PATH_INV += 1
				return False # on enregistre pas le lieu de fin de trajet (le trajet ne pourra pas etre effectue)
		self.last_path_end_loc = end_loc
		return True

	def onNextPathTimeCheck(self, start_time, end_time, pp):
		# sauvegarde de l'heure de debut de journee
		if self.day_start_time is None:
			self.day_start_time = start_time

		if self.last_path_end_time is not None:
			# si lheure du trajet avant la fin du trajet precedent
			if start_time < self.last_path_end_time:
				if pp:
					print "\t\t\t\tStart time:", str(start_time / 60)+":"+str(start_time % 60), "is before",
					print str(self.last_path_end_time / 60)+":"+str(self.last_path_end_time / 60), ": INVALID !"
				self.PATH_INV += 1
				return False # on ne prend pas en compte ce trajet

		# sauvegarde de l'heure de fin de journee
		if self.day_end_time is None or self.day_end_time < end_time:
			self.day_end_time = end_time

		# sauvegarde l'heure de fin du trajet precedent
		self.last_path_end_time = end_time

		# ajout du temps de ce trajet au temps total de cet employe et de ce jour
		self.cur_empl_work_len += end_time - start_time

		return True
# est-ce qu'on compte un trajet invalide dans le temps de travail de la journee d'un employe ? Non



