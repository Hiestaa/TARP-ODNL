from const import Const

### L'evaluation se fait en plusieurs passes:
###		1 - LOC_INV = nombre de trajets invalides en terme de correspondance
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
		self.cur_empl_days_len = [0 for x in range(5)]
		# temps total travaille dans la journee pour l'employe courant
		self.cur_empl_work_len = [0 for x in range(5)]
		self.cur_day = None # jour en cours de traitement

		# sauvegarde l'heure de debut du premier trajet de la journee
		self.day_start_time = None
		# sauvegarde l'heure de fin du dernier trajet de la journee
		self.day_end_time = None

		# au cours de l'analyse, arrive du precedent trajet
		self.last_path_end_loc = None
		self.last_path_end_time = None

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

		print "NB_EMPL=", self.NB_EMPL
		print "PATH_INV=", self.PATH_INV
		print "OVER_DAY_LEN=", self.OVER_DAY_LEN
		print "OVER_WORK_LEN=", self.OVER_WORK_LEN
		print "sol: ", sol

		return self.NB_EMPL * 1 + self.PATH_INV * 1 + self.OVER_DAY_LEN * 1 + self.OVER_WORK_LEN * 1

	def onNewEmployee(self, empl):
		print "Employee: ", empl
		# compte un employe de plus
		self.NB_EMPL += 1
		# reinitialise les compteurs de temps des employes
		for x in range(5):
			self.cur_empl_days_len[x] = 0
			self.cur_empl_work_len[x] = 0
		# reinitialise la sauvegarde de lieu d'arrivee du dernier trajet
		self.last_path_end_loc = None


	def onNewDay(self, day):
		print "\tDay: ", day
		# l'heure du trajet precedent ne sera pas pris en compte pour le premier trajet du nouveau jour
		self.last_path_end_time = None
		self.cur_day = day
		self.day_start_time = None
		self.day_stop_time = None

	def onEndDay(self):
		# sauvegarde le temps total de travail de la journee passee
		if self.day_start_time is not None and self.day_end_time is not None:
			self.cur_empl_days_len[self.cur_day] = self.day_end_time - self.day_start_time
		else:
			self.cur_empl_days_len[self.cur_day] = 0
		# note : pour l'instant, l'evaluation ne tient pas compte du cout des journees trop chomees
		if self.cur_empl_days_len[self.cur_day] > 420:
			self.OVER_DAY_LEN += self.cur_empl_days_len[self.cur_day] - 420
		if self.cur_empl_work_len[self.cur_day] > 300:
			self.OVER_WORK_LEN += self.cur_empl_work_len[self.cur_day] - 300


	def onNextPath(self, id, start_loc, end_loc, start_time, end_time):
		print "\t\tTrajet: ", id
		print "\t\t\tStart:", chr(start_loc), "End: ", chr(end_loc)
		print "\t\t\tStart time:", str(start_time / 60)+":"+str(start_time % 60),
		print "End time: ", str(end_time / 60)+":"+str(end_time % 60)

		if self.onNextPathLocCheck(start_loc, end_loc):
			self.onNextPathTimeCheck(start_time, end_time)

	def onNextPathLocCheck(self, start_loc, end_loc):
		# si un trajet a deja ete effectue
		if self.last_path_end_loc is not None:
			# si le lieu de fin du trajet precedent n'est pas le meme que le suivant
			if start_loc != self.last_path_end_loc:
				print "\t\t\t\tStart loc:", chr(start_loc), "is not", chr(self.last_path_end_loc), ": INVALID !"
				self.PATH_INV += 1
				return False # on enregistre pas le lieu de fin de trajet (le trajet ne pourra pas etre effectue)
		self.last_path_end_loc = end_loc
		return True

	def onNextPathTimeCheck(self, start_time, end_time):
		# sauvegarde de l'heure de debut de journee
		if self.day_start_time is None:
			self.day_start_time = start_time

		if self.last_path_end_time is not None:
			# si lheure du trajet avant la fin du trajet precedent
			if start_time < self.last_path_end_time:
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
		self.cur_empl_work_len[self.cur_day] += end_time - start_time

		return True
# est-ce qu'on compte un trajet invalide dans le temps de travail de la journee d'un employe ? Non



