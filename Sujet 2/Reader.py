import numpy

class Reader :
	
	@staticmethod
	def readFile(file) :
		lines = []
		f = open(file, 'r')
		line = f.readline()
		while line != '' :
			splitedLine = line.split()
			lines.append(splitedLine)
			# print ord(splitedLine[1])
			line = f.readline()
		# print lines
		result = numpy.empty([len(lines), 7], dtype=numpy.int32)
		for i in xrange(len(lines)) :
			result[i][0] = int(lines[i][0]) - 1
			result[i][1] = ord(lines[i][1])
			result[i][2] = ord(lines[i][2])
			start = lines[i][3].split(':')
			result[i][3] = start[0]
			result[i][4] = start[1]
			end = lines[i][4].split(':')
			result[i][5] = end[0]
			result[i][6] = end[1]
		return result
		