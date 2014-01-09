import pyopencl as cl
import numpy

class guTarp :
	def __init__(self, baseTab):
		self.baseTab = baseTab

		self.ctx = cl.create_some_context()
		self.queue = cl.CommandQueue(self.ctx)
		f = open("gutarp.cl", 'r')
		fstr = "".join(f.readlines())
		self.guTarpCL = cl.Program(self.ctx, fstr).build()

		self.baseTabBuffer = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=self.baseTab)
		cl.enqueue_write_buffer(self.queue, self.baseTabBuffer, self.baseTab)

	def compute(self, idTab) :

		idTabBuffer = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=idTab)
		cl.enqueue_write_buffer(self.queue, idTabBuffer, idTab)

		result = numpy.empty([idTab.shape[0], 1], dtype=numpy.int32)

		resultBuffer = cl.Buffer(self.ctx, cl.mem_flags.READ_WRITE | cl.mem_flags.COPY_HOST_PTR, hostbuf=result)
		cl.enqueue_write_buffer(self.queue, resultBuffer, result)

		self.guTarpCL.gutarp(self.queue, (idTab.shape[0],), None, self.baseTabBuffer, idTabBuffer,
								numpy.int32(self.baseTab.shape[0]), numpy.int32(self.baseTab.shape[1]), resultBuffer)

		cl.enqueue_read_buffer(self.queue, resultBuffer, result).wait()
		return result