import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pygame
import heapq as q

import random
import time
import os, pdb

from task import Task
from evaluation import Evaluation
from guTarp import guTarp
from graphx import Graphx
import Log

class Tabu:
	"""Classe principale de l'algorithme tabu"""
	def __init__(self, input_file, enable_display=False):
		# suppression des anciens logs
		for fname in os.listdir('log'):
			if not fname == '__tabu.log.html' and not fname == "style":
				os.remove('log/' + fname)
		self.tabu_list = []
		self.tabu_length = 0
		self.tabu_max_length = 10000
		self.tabu_min_length = 1

		self.input_file = input_file
		self.nb_op = 0
		self.nb_tasks = 0
		self.seed = 0
		self.upperbound = 0
		self.lowerbound = 0
		self.tasks = []
		self.sequence = []
		self.starting_time = 0
		self.best_sol = (0, '') # the value of the solution, and the solution itself
		self.local_optimums = []
		self.enable_display = enable_display
		self.log = Log.Log('log/__tabu.log.html')

		self.decreasing = True
		self.nptasks = None
		self.nporder = None

		self.gpucomputer = None

		self.interesting = []
		self.same_value_counter = 0
		self.same_value_counter_max = 10

		# sauvegarde le valeurs du chemin pour afficher un graphique
		self.memory = []
		self.it_max = 0
		self.graphx = Graphx()

	def init_node(self):
		# initialise aleatoirement l'ordre des taches
		self.init_ord()
		node_name = reduce(lambda a,b: str(a)+"-"+str(b), self.sequence)
		node = (Evaluation(self.tasks, self.sequence, node_name).fast(), node_name, self.sequence)
		return node


	def run(self, it_max):
		self.it_max = it_max
		self.starting_time = time.time()
		# parse le fichier d'entree pour construire la liste de taches
		self.parse_input()
		self.init_ord()

		self.best_sol = self.init_node()
		#self.log.log_init_tabu(self.tabu_max_length, self.best_sol[1], self.best_sol[0])

		#self.log.log_event_success(time.time() - self.starting_time, 'Result', "Initial node: [" + str(self.best_sol[0]) + "] " + node_name)

		# appelle run_rec qui va construire et parcourir le graphe des
		#   suivant l'algorithme de recherche taboue de facon recursive
		cur_node = self.best_sol
		print "Starting. Initial node: [", self.best_sol[0], "]", self.sequence
		for i in range(it_max):
			self.memory.append((float(i) / float(it_max) * 1024, 800 - (cur_node[0] - self.lowerbound)))
			if cur_node[0] == self.upperbound:
				break
			else:
				print self.best_sol[0], self.upperbound

			# met a jour la memoire de l'historique
			if i > 2 and self.plot():
				break

			if (i*100) % it_max == 0:
				print "Progress: ", (float(i)/float(it_max)*100), '%'
			ret = self.run_tabu(cur_node)
			if ret[1] is not None:
				# enregistre la meilleure position
				if ret[0] < self.best_sol[0]:
				 	self.best_sol = ret

				# test si on est sur la meme valeur qu'au tour precedent
				if ret[0] == cur_node[0]:
					self.same_value_counter += 1


				# si le resultat (best adj) est moins bon que le noeud precedent et qu'on etait sur une courbe descendente
				#  ou si on est sur le premier noeud et que le meilleur voisin est moins bon que le noeud courant
				#  	on ajoute le noeud courant a la liste des optimums locaux
				if ret[0] >= cur_node[0] and self.decreasing:
					#self.log.log_event_warning(time.time() - self.starting_time, 'Result', 'Local optimum found: ['+str(cur_node[0])+'] '+str(cur_node[1])+' !')
					#if cur_node[1] in self.local_optimums:
						#self.log.log_event_error(time.time() - self.starting_time, 'Error', 'Local optimum: ['+str(cur_node[0])+'] '+str(cur_node[1])+' has already been found !')
					if not cur_node[1] in self.local_optimums:
						self.local_optimums.append(cur_node[1])
						#Evaluation(self.tasks, map(lambda arg: int(arg), cur_node[2]), cur_node[1]).simulation();
					self.decreasing = False # on est plus sur une courbe descendante
				# marque si on est sur une courbe descendante
				if ret[0] < cur_node[0] or cur_node[0] < 0:
					self.decreasing = True
				cur_node = ret

				# si on reste trop sur la meme valeur, on recommence a un point aleatoire du graphe
				if self.same_value_counter > self.same_value_counter_max:
					self.same_value_counter = 0
					cur_node = q.nlargest(1, self.interesting)[0]
					self.interesting.remove(cur_node)
					q.heapify(self.interesting)
#					cur_node = self.init_node()
			else:
				#self.log.log_event_error(time.time() - self.starting_time, 'Error', "All the adjacents nodes are in the tabu list")
				#self.log.log_event_error(time.time() - self.starting_time, 'Error', 'Truncating tabu list to length: ' + str(self.tabu_min_length))
				# on doit gerer le fait que tous les voisins du noeud courant sont dans la liste taboue
				# on pique dans la liste des sommets interessants
				cur_node = q.nlargest(1, self.interesting)[0]
				self.interesting.remove(cur_node)
				q.heapify(self.interesting)
			#self.log.log_event_success(time.time() - self.starting_time, 'Result', "Best solution found for now: [" + str(self.best_sol[0]) + "] " + str(self.best_sol[1]))
			#self.log.log_event(time.time() - self.starting_time, 'State', "Tabu list size:" + str(self.tabu_length))


		#self.log.log_close_tabu(self.best_sol)

		if len(self.local_optimums) > 0:
			print "Local optimums: "
			for x in self.local_optimums:
				print x,":",Evaluation(self.tasks, map(lambda arg: int(arg), x.split('-')), x).fast()
		else:
			print "No local optimum found"
		print "Best solution found: " + str(self.best_sol)


		done = False
		while not done:
			done = self.plot()
	# lance la recherche taboue sur le noeud donne. Si de nouveaux noeuds sont ajoutes, ils seront evalues.
	# le noeud avec le meilleur score est retourne.
	def run_tabu(self, node):
		# log le process sur ce noeud
		#self.log.log_event_info(time.time() - self.starting_time, 'State', "Processing node: " + node)

		#ajout de ce noeud a la liste taboue
		if node[1] not in self.tabu_list:
			self.tabu_list.append(node[1])
			self.tabu_length += 1

		best_adj = (-1, None)
		# TODO: retrieve list lst = self.sol_graph.node[node]['list']
		lst = node[2]
		# effectue toutes les combinaisons de permutations possibles sur l'ordonnancement
		orderpos = 0
		neighboors_name = []
		for i in range(self.nb_tasks):
			for j in xrange(i+1,self.nb_tasks):
				lst[i], lst[j] = lst[j], lst[i] # swap
				# copie dans la numpy_array des ordres
				for k in range(self.nb_tasks):
					self.nporder[orderpos][k] = lst[k]
				orderpos += 1

				# calcule le nom du noeud
				node_name = reduce(lambda a,b: str(a)+"-"+str(b), lst)
				neighboors_name.append(node_name)

				# swap inverse
				lst[i], lst[j] = lst[j], lst[i]

		# lance le calcul sur la carte graphique
		result = self.gpucomputer.compute(self.nporder)
		ordered = []
		for x in range(orderpos):
			q.heappush(ordered, (result[x][0], x))


		best = q.heappop(ordered)
		while neighboors_name[best[1]] in self.tabu_list:
			best = q.heappop(ordered)
		interest = q.nlargest(1, ordered)[0]
		if neighboors_name[interest[1]] in self.tabu_list or interest[0] == best[0]:
			interest = None

		best_adj = (best[0], neighboors_name[best[1]], [int(x) for x in neighboors_name[best[1]].split('-')])
		if interest:
			interest_adj = (interest[0], neighboors_name[interest[1]], [int(x) for x in neighboors_name[interest[1]].split('-')])
			q.heappush(self.interesting, interest_adj)

		# tronque la liste taboue a la longueur
		if self.tabu_length > self.tabu_max_length:
			self.tabu_list = self.tabu_list[self.tabu_length - self.tabu_max_length:self.tabu_length]
			self.tabu_length = len(self.tabu_list)
			#self.tabu_length = self.tabu_max_length
			if self.tabu_length != self.tabu_max_length:
				print "List len error: ", self.tabu_length
				exit()

		# if best_adj[1] is not None:
		# 	#self.log.log_event_info(time.time() - self.starting_time, 'State', 'Best adjacent node of ' + node + ': [' + str(best_adj[0]) + '] ' + best_adj[1])
		# else:
			#self.log.log_event_warning(time.time() - self.starting_time, 'State', 'All adjacent nodes of ' + node + ' are in the tabu list !')

		# retourne le nom du meilleur noeud voisin
		return best_adj

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
		self.nptasks = np.empty([self.nb_op,self.nb_tasks], dtype=np.int32)
		self.nporder = np.empty([self.nb_tasks*(self.nb_tasks-1)/2,self.nb_tasks], dtype=np.int32)

		for i in range(self.nb_tasks):
			# initializing each task with an empty list of operation
			self.tasks.append(Task(i, []))

		for i in range(self.nb_op):
			op = f.readline() # get the ith job for each task
			op = op.split()
			for j in range(self.nb_tasks):
				self.tasks[j].add_operation(int(op[j]))
				self.nptasks[i][j] = op[j]

		f.close()

		self.gpucomputer = guTarp(self.nptasks)

		random.seed(self.seed)
		#random.seed(time.time())

	def init_ord(self):
		self.sequence = [task.id for task in self.tasks]
		random.shuffle(self.sequence)

	def plot(self):
		self.graphx.update()
		self.graphx.draw_lines([(0, 800 - (self.upperbound - self.lowerbound)), (1024, 800 - (self.upperbound - self.lowerbound))],
			color=pygame.color.Color('red'))
		self.graphx.draw_lines([(0, 800 - (self.best_sol[0] - self.lowerbound)), (1024, 800 - (self.best_sol[0] - self.lowerbound))],
			color=pygame.color.Color('green'))
		self.graphx.draw_lines(self.memory)
		for event in pygame.event.get():
			if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				return True