def eval(tab) :
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
	print tab
	return tab[nbColonnes - 1][nbLines - 1]
	
 
tab = [	[54, 79, 16, 66, 58],
		[83, 3, 89, 58, 56],
		[15, 11, 49, 31, 20],
		[71, 99, 15, 68, 85],
		[77, 56, 89, 78, 53],
		[36, 70, 45, 91, 35],
		[53, 99, 60, 13, 53],
		[38, 60, 23, 59, 41],
		[27, 5, 57, 49, 69],
		[87, 56, 64, 85, 13],
		[76, 3, 7, 85, 86],
		[91, 61, 1, 9, 72],
		[14, 73, 63, 39, 8],
		[29, 75, 41, 41, 49],
		[12, 47, 63, 56, 47],
		[77, 14, 47, 40, 87],
		[32, 21, 26, 54, 58],
		[87, 86, 75, 77, 18],
		[68, 5, 77, 51, 68],
		[94, 77, 40, 31, 28]]
print eval(tab)