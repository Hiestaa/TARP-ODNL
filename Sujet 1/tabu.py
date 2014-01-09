import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

import random
import time
import os, pdb

from task import Task
from evaluation import Evaluation
from guTarp import guTarp
import Log

class Tabu:
	"""Classe principale de l'algorithme tabu"""
	def __init__(self, input_file, enable_display=False):
		self.tabu_list = []
		self.tabu_length = 0
		self.tabu_max_length = 100
		self.tabu_min_length = 1

		self.sol_graph = nx.Graph(name=input_file)
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


	def run(self, it_max):
		self.starting_time = time.time()
		# parse le fichier d'entree pour construire la liste de taches
		self.parse_input()
		# initialise aleatoirement l'ordre des taches
		self.init_ord()

		node_name = reduce(lambda a,b: str(a)+"-"+str(b), self.sequence)
		self.best_sol = (Evaluation(self.tasks, self.sequence, node_name).fast(), node_name)
		#self.log.log_init_tabu(self.tabu_max_length, self.best_sol[1], self.best_sol[0])
		# cree le graphe avec un noeud correspondant a cet ordonnancement
		self.sol_graph.add_node(
			node_name, time=self.starting_time - time.time(),
			value=self.best_sol[0],
			list=[x for x in self.sequence]
		)
		#self.log.log_event_success(time.time() - self.starting_time, 'Result', "Initial node: [" + str(self.best_sol[0]) + "] " + node_name)

		# appelle run_rec qui va construire et parcourir le graphe des
		#   suivant l'algorithme de recherche taboue de facon recursive
		cur_node = self.best_sol
		print "Starting. Initial node: [", self.best_sol[0], "]", self.sequence
		for i in range(it_max):
			print "Progress: ", (float(i)/float(it_max)*100), '%'
			#pdb.set_trace()
			ret = self.run_tabu(cur_node[1])
			if ret[1] is not None:
				# enregistre la meilleure position
				if ret[0] < self.best_sol[0]:
				 	self.best_sol = ret
				# si le resultat (best adj) est moins bon que le noeud precedent et qu'on etait sur une courbe descendente
				#  ou si on est sur le premier noeud et que le meilleur voisin est moins bon que le noeud courant
				#  	on ajoute le noeud courant a la liste des optimums locaux
				if ret[0] >= cur_node[0] and self.decreasing:
					#self.log.log_event_warning(time.time() - self.starting_time, 'Result', 'Local optimum found: ['+str(cur_node[0])+'] '+str(cur_node[1])+' !')
					#if cur_node[1] in self.local_optimums:
						#self.log.log_event_error(time.time() - self.starting_time, 'Error', 'Local optimum: ['+str(cur_node[0])+'] '+str(cur_node[1])+' has already been found !')
					if not cur_node[1] in self.local_optimums:
						print 'Local optimum found: '+str(cur_node)+' ! Creating machines log...'
						self.local_optimums.append(cur_node[1])
						Evaluation(self.tasks, map(lambda arg: int(arg), cur_node[1].split('-')), cur_node[1]).fast();
						print "Done. Continuing..."
					self.decreasing = False # on est plus sur une courbe descendante
				# marque si on est sur une courbe descendante
				if ret[0] < cur_node[0] or cur_node[0] < 0:
					self.decreasing = True
				cur_node = ret
			else:
				#self.log.log_event_error(time.time() - self.starting_time, 'Error', "All the adjacents nodes are in the tabu list")
				#self.log.log_event_error(time.time() - self.starting_time, 'Error', 'Truncating tabu list to length: ' + str(self.tabu_min_length))
				# on doit gerer le fait que tous les voisins du noeud courant sont dans la liste taboue
				# on devrait remonter tans la liste du chemin parcouru jusqu'a trouver un autre chemin possible
				# pour l'instant, on tronque la liste a sa taille minimum et on continue
				self.tabu_list = self.tabu_list[self.tabu_length - self.tabu_min_length:self.tabu_length]
				self.tabu_length = len(self.tabu_list)
				#self.tabu_length = self.tabu_max_length
				if self.tabu_length != self.tabu_min_length:
					print "List len error: ", self.tabu_length
					exit()
				print cur_node
			#self.log.log_event_success(time.time() - self.starting_time, 'Result', "Best solution found for now: [" + str(self.best_sol[0]) + "] " + str(self.best_sol[1]))
			#self.log.log_event(time.time() - self.starting_time, 'State', "Tabu list size:" + str(self.tabu_length))


		# on supprime le log pour ne garder que les infos des optimums locaux
		# for fname in os.listdir('log'):
		# 	if not fname == '__tabu.log.html' and not fname == "style" and not fname[:-9] in self.local_optimums:
		# 		if '14-10-8-5-4-0-3-16-18-12-15-7-13-17-11-1-9-2-6-19' in fname:
		# 			print "Deleting an optimum!"
		# 		os.remove('log/' + fname)
		#self.log.log_close_tabu(self.best_sol)
		#self.display_graph()
		if len(self.local_optimums) > 0:
			print "Local optimums: "+reduce(
				lambda a,b:
					a+"\r\n"+b,
				self.local_optimums)
		else:
			print "No local optimum found"
		print "Best solution found: " + str(self.best_sol)

	# lance la recherche taboue sur le noeud donne. Si de nouveaux noeuds sont ajoutes, ils seront evalues.
	# le noeud avec le meilleur score est retourne.
	def run_tabu(self, node):
		# log le process sur ce noeud
		#self.log.log_event_info(time.time() - self.starting_time, 'State', "Processing node: " + node)

		#ajout de ce noeud a la liste taboue
		if node not in self.tabu_list:
			self.tabu_list.append(node)
			self.tabu_length += 1

		best_adj = (-1, None)
		lst = self.sol_graph.node[node]['list']
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
				#ajoute a la list taboue:
				# test si le noeud existe deja
				if node_name in self.sol_graph:
					# si oui, on ajoute juste un lien vers ce noeud
					self.sol_graph.add_edge(node, node_name)
					#self.log.log_event(time.time() - self.starting_time, 'Graph', "Node [" + node_name + "] is already present (val="+str(self.sol_graph.node[node_name]['value'])+") !")
					# ajout du noeud adjacent a la liste des noeuds adjacents
					# 	swap inverse (retour a l'etat initial de la list pour le swap suivant)
					lst[i], lst[j] = lst[j], lst[i]
				else:
					#si non, on evalue la solution
					#res = (Evaluation(self.tasks, lst, node_name).fast(), node_name)
					# on ajoute le noeud
					self.sol_graph.add_node(
						node_name, time=self.starting_time - time.time(),
						value=0,
						list=[x for x in lst])
					#self.log.log_event(time.time() - self.starting_time, 'Graph', "Added new node : [" + str(0) + "] " + node_name)
					# on ajoute le lien vers ce noeud
					self.sol_graph.add_edge(node, node_name)
					# swap inverse
					lst[i], lst[j] = lst[j], lst[i]

				# # point on this node if it's the best adjacent node
				# if (best_adj[0] < 0 or self.sol_graph.node[node_name]['value'] < best_adj[0]):
				# 	if node_name not in self.tabu_list:
				# 		best_adj = (self.sol_graph.node[node_name]['value'], node_name)
				# 	else:
				# 		#self.log.log_event(time.time() - self.starting_time, 'State', "Solution: " + node_name + " is in the tabu list ! Ignoring...")

				# add this adjacent node to the tabu list
				# if node_name not in self.tabu_list:
				# 	self.tabu_list.append(node_name)
				# 	self.tabu_length += 1
		# lance le calcul sur la carte graphique
		result = self.gpucomputer.compute(self.nporder)
		best = -1
		best_index = 0
		for x in range(orderpos):
			#print "adj: ", neighboors_name[x], " : ", result[x][0]
			if best is -1 or best > result[x][0] and not neighboors_name[x] in self.tabu_list:
				best_index = x
				best = result[x][0]

		#print "New best adj: ", neighboors_name[best_index]," : ", result[best_index][0]
		#print "Old best adj: ", best_adj[1], " : ", best_adj[0]

		best_name = neighboors_name[best_index]

		best_adj = (best, best_name)
		#print "Best adj: ", best_adj[1], " : ", best_adj[0]

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

	def init_ord(self):
		self.sequence = [task.id for task in self.tasks]
		random.shuffle(self.sequence)

