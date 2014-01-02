import networkx as nx
import matplotlib.pyplot as plt

import random
import time
import os, pdb

from task import Task
from evaluation import Evaluation
import Log

class Tabu:
	"""Classe principale de l'algorithme tabu"""
	def __init__(self, input_file, enable_display=False):
		self.tabu_list = []
		self.tabu_length = 0
		self.tabu_max_length = 10000
		self.tabu_min_length = 10

		self.sol_graph = nx.Graph(name=input_file)
		self.drawable_graph = nx.Graph()
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

		self.path = []
		self.colorpath = []
		self.colorpathstate = (0, 1, 0)
		self.decreasing = False


	def run(self):
		self.starting_time = time.time()
		# parse le fichier d'entree pour construire la liste de taches
		self.parse_input()
		# initialise aleatoirement l'ordre des taches
		self.init_ord()

		reduced_sol = reduce(lambda a,b: str(a)+"-"+str(b), self.sequence)
		self.best_sol = (Evaluation(self.tasks, self.sequence, reduced_sol).run(), reduced_sol)
		self.log.log_init_tabu(self.tabu_max_length, self.best_sol[1])
		# cree le graphe avec un noeud correspondant a cet ordonnancement
		self.sol_graph.add_node(
			reduced_sol, time=self.starting_time - time.time(),
			value=self.best_sol[0],
			list=[x for x in self.sequence]
		)
		self.drawable_graph.add_node(
			reduced_sol, time=self.starting_time - time.time(),
			value=self.best_sol[0],
			list=[x for x in self.sequence]
		)

		# appelle run_rec qui va construire et parcourir le graphe des
		#   suivant l'algorithme de recherche taboue de facon recursive
		cur_node = (-1, reduced_sol)
		it_max = 10
		for i in range(it_max):
			print "Progress: ", (float(i)/float(it_max)*100), '%'
			#pdb.set_trace()
			ret = self.run_tabu(cur_node[1])
			if ret is not None:
				self.drawable_graph.add_edge(cur_node[1], ret[1])
				# si le resultat (best adj) est moins bon que le noeud precedent et qu'on etait sur une courbe descendente
				#  on ajoute le noeud courant a la liste des optimums locaux
				if ret[0] >= cur_node[0] and self.decreasing:
					self.log.log_event_warning(time.time() - self.starting_time, 'Result', 'Local optimum found: '+str(cur_node)+' !')
					print 'Local optimum found: '+str(cur_node)+' !'
					self.decreasing = False # on est plus sur une courbe descendante
					self.local_optimums.append(cur_node[1])
				# marque si on est sur une courbe descendante
				if ret[0] < cur_node[0] or cur_node[0] < 0:
					self.decreasing = True
				cur_node = ret
			else:
				self.log.log_event_error(time.time() - self.starting_time, 'Error', "All the adjacents nodes are in the tabu list")
				self.log.log_event_error(time.time() - self.starting_time, 'Error', 'Truncating tabu list to length: ' + str(self.tabu_min_length))
				# on doit gerer le fait que tous les voisins du noeud courant sont dans la liste taboue
				# on devrait remonter tans la liste du chemin parcouru jusqu'a trouver un
			self.log.log_event_success(time.time() - self.starting_time, 'Result', "Best solution found for now: " + str(self.best_sol))
			self.log.log_event(time.time() - self.starting_time, 'State', "Tabu list size:" + str(self.tabu_length))


		# on supprime le log pour ne garder que les infos des optimums locaux
		for fname in os.listdir('log'):
			if not fname == '__tabu.log.html' and not fname == "style" and not fname[:-9] in self.local_optimums:
				if '14-10-8-5-4-0-3-16-18-12-15-7-13-17-11-1-9-2-6-19' in fname:
					print "Deleting an optimum!"
				os.remove('log/' + fname)
		self.log.log_close_tabu(self.best_sol)
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
		self.log.log_event_info(time.time() - self.starting_time, 'State', "Processing node: " + node)
		# ajout de ce noeud au path
		self.path.append(node)
		self.colorpath.append(self.colorpathstate)
		self.colorpathstate = (self.colorpathstate[0], self.colorpathstate[1] * 0.99, self.colorpathstate[2])

		#ajout de ce noeud a la liste taboue
		if node not in self.tabu_list:
			self.tabu_list.append(node)
			self.tabu_length += 1

		best_adj = (-1, None)
		lst = self.sol_graph.node[node]['list']
		# effectue toutes les combinaisons de permutations possibles sur l'ordonnancement
		for i in range(self.nb_tasks):
			for j in xrange(i+1,self.nb_tasks):
				lst[i], lst[j] = lst[j], lst[i] # swap
				reduced_sol = reduce(lambda a,b: str(a)+"-"+str(b), lst) # calcule le nom du noeud
				#ajoute a la list taboue:
				# test si le noeud existe deja
				if reduced_sol in self.sol_graph:
					# si oui, on ajoute juste un lien vers ce noeud
					self.sol_graph.add_edge(node, reduced_sol)
					self.log.log_event(time.time() - self.starting_time, 'Graph', "Added edge between " + node + " and " + reduced_sol)
					# ajout du noeud adjacent a la liste des noeuds adjacents
					# swap inverse (retour a l'etat initial de la list pour le swap suivant)
					lst[i], lst[j] = lst[j], lst[i]
				else:
					#si non, on evalue la solution
					res = (Evaluation(self.tasks, lst, reduced_sol).run(), reduced_sol)
					# on verifie si elle est meilleure que celle trouvee
					if res[0] < self.best_sol[0]:
						self.best_sol = res
					# on ajoute le noeud
					self.sol_graph.add_node(
						reduced_sol, time=self.starting_time - time.time(),
						value=res[0], list=[x for x in lst])
					self.log.log_event(time.time() - self.starting_time, 'Graph', "Added new node : [" + str(res[0]) + "] " + reduced_sol)
					# on ajoute le lien vers ce noeud
					self.sol_graph.add_edge(node, reduced_sol)
					# swap inverse
					lst[i], lst[j] = lst[j], lst[i]

				# point on this node if it's the best adjacent node
				if (best_adj[0] < 0 or self.sol_graph.node[reduced_sol]['value'] < best_adj[0]) and reduced_sol not in self.tabu_list:
					best_adj = (self.sol_graph.node[reduced_sol]['value'], reduced_sol)

		# tronque la list taboue a la longueur
		if self.tabu_length > self.tabu_max_length:
			self.tabu_list = self.tabu_list[self.tabu_length - self.tabu_max_length:self.tabu_length]
			self.tabu_length = len(self.tabu_list)
			#self.tabu_length = self.tabu_max_length
			if self.tabu_length != self.tabu_max_length:
				print "List len error: ", self.tabu_length
				exit()


		# ajoute ce noeud a graph du path
		#self.drawable_graph.add_node(best_adj[1], time=self.sol_graph.node[best_adj[1]]['time'],
		#	value=self.sol_graph.node[best_adj[1]]['value'], list=self.sol_graph.node[best_adj[1]]['list'])
		if best_adj[1] is not None:
			self.log.log_event_info(time.time() - self.starting_time, 'State', 'Best adjacent node of ' + node + ': [' + str(best_adj[0]) + '] ' + best_adj[1])
		else:
			self.log.log_event_warning(time.time() - self.starting_time, 'State', 'All adjacent nodes of ' + node + ' are in the tabu list !')

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

		for i in range(self.nb_tasks):
			# initializing each task with an empty list of operation
			self.tasks.append(Task(i, []))

		for i in range(self.nb_op):
			op = f.readline() # get the ith job for each task
			op = op.split()
			for j in range(self.nb_tasks):
				self.tasks[j].add_operation(int(op[j]))

		f.close()

		random.seed(self.seed)

		#self.parse_test()

	def parse_test(self):
		print "Number of jobs:", self.nb_tasks
		print "Number of machines:", self.nb_op
		print "Initial seed:", self.seed
		print "Upper bound:", self.upperbound
		print "Lower bound:", self.lowerbound

		for task in self.tasks:
			print ""
			print "Task", task.id, ": ",
			for o in task.oplist:
				print o,
		print ""

	def init_ord(self):
		self.sequence = [task.id for task in self.tasks]
		random.shuffle(self.sequence)
		print self.sequence
		pass

	def display_graph(self):
		labels=dict((n,d['value']) for n,d in self.sol_graph.nodes(data=True))
		pos = nx.spring_layout(self.sol_graph)
		nx.draw_networkx_edges(self.sol_graph, pos=pos)
		tabu = [x for x in self.tabu_list if x not in self.path]
		remain = [x for x in self.sol_graph.nodes() if x not in tabu and x not in self.path]
		nx.draw(self.sol_graph, pos=pos, nodelist=remain, node_size=1000, node_color='b')
		nx.draw(self.sol_graph, pos=pos, nodelist=tabu, node_size=500, node_color='r')
		nx.draw(self.sol_graph, pos=pos, nodelist=self.path, node_size=2000, node_color=self.colorpath)
		plt.show()