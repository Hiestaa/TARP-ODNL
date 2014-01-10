import pygame

class Graphx:
	"""Permet de faire l'affichage graphique"""
	def __init__(self):
		#params
		self.backgroundColor = (0, 0, 0)
		self.screensize = (self.screenwidth, self.screenheight) = (1024, 768)

		# initialise screen
		pygame.init()
		self.screen = pygame.display.set_mode(self.screensize, pygame.RESIZABLE | pygame.DOUBLEBUF)
		pygame.display.set_caption('TARP - ODNL, sujet 1')

		#create the font
		self.fontObj = pygame.font.Font('freesansbold.ttf', 28);

	#finalise le rendu graphique
	def update(self):
		pygame.display.flip()
		self.screen.fill(self.backgroundColor)


	#affiche le composant a la position x
	def draw_rect(self, pos):
		pygame.draw.rect(self.screen, pygame.color.Color('white'), pos, 1)

	def draw_line(self, pos1, pos2):
		pygame.draw.line(self.screen, pygame.color.Color('blue'), pos1, pos2, 2)

	def draw_lines(self, points, color=pygame.color.Color('white')):
		pygame.draw.lines(self.screen, color, False, points, 1)

	# affiche un texte a la position donnee
	def draw_text(self, pos, text):
		label = self.fontObj.render(text, 1, pygame.color.Color('white'))
		self.screen.blit(label, pos);
