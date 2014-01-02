from __future__ import print_function

from task import Task

class Log:
	"""Give a set of functions to log datas into files"""
	def __init__(self, filename):
		self.filename = filename
		self.f = None
		self.typelist = []

		self.openhtml = '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>TARP Result</title>
    <link rel="stylesheet" href="style/custom.css">
    <link rel="stylesheet" href="style/ink-2.2.1/css/ink.css">
    <script type="text/javascript" src="style/jquery-2.0.3.js"></script>
    <script type="text/javascript" src="style/inc-2.2.1/js/ink.min.js"></script>
	<script type="text/javascript" src="style/inc-2.2.1/js/ink.progressbar.js"></script>
	<script type="text/javascript" src="style/inc-2.2.1/js/autoload.js"></script>
  </head>
  <body>
	  <div class="ink-grid">
	'''


		self.closehtml = '''
	<div class="column-group">
		<div class="large-100 push-center gutters">This is a generated file log from the TARP project, subject 1</div>
	</div>
  </body>
</html>'''

	def log_init_tabu(self, tabu_list_len, tabu_init_node):
		self.f = open(self.filename, 'w')
		self.log(self.openhtml)
		self.log('<div class="column-group"><div class="large-100"><h1> TARP Logger <h1><h2>Tabu search</h2>')
		self.log('<table class="ink-table bordered hover"><tr><th>Tabu list maximum length</th><td>' + str(tabu_list_len) + '</td></tr>')
		self.log('<tr><th>Tabu starting node</th><td>' + tabu_init_node + '</td></tr></table>')
		self.log('<h3>Table filter</h3><div class="column-group gutters" id="type_filter"></div>')
		self.log('<table class="ink-table alternating bordered hover"><thead><tr><th width="10%">Time</th><th width="20%">Type</th><th width="70%">Event</th></tr></thead><tbody>')

	def log_close_tabu(self, tabu_res):
		self.log('</tbody></table><h2>Tabu results</h2><table class="ink-table bordered hover">')
		self.log('<tr><th>Best result found</th><td>' + str(tabu_res[1]) + '</td><td>Score:' + str(tabu_res[0]) + '</td></tr></table>')
		self.log('</div>')
		self.log('<script type="text/javascript">')
		self.log('function apply_filter(type) {')
		self.log("\t"+'if ($(\'.\'+type).css(\'display\') == "none")')
		self.log("\t\t"+'$(\'.\'+type).css(\'display\', \'\')')
		self.log("\t"+'else')
		self.log("\t\t"+'$(\'.\'+type).css(\'display\', \'none\')')
		self.log('}')
		self.log('$( document ).ready(function() {')
		for t in self.typelist:
			self.log('$(\'#type_filter\').append(\'<div class="large-20"><h4><input type="checkbox" id="'+t+'" onclick="apply_filter(\\\''+t+'\\\')" checked>'+
				'<label for="'+t+'">'+t+'</label></h4></div>\')')
		self.log('});')
		self.log('</script>')
		self.log(self.closehtml)
		self.f.close()

	def log_init_tasklist(self, tasklist):
		self.f = open(self.filename, 'w')
		self.log(self.openhtml)
		self.log('<div class="column-group"><div class="large-100"><h1> TARP Logger <h1><h2>Tasks overview</h2>')
		self.log_tasklist(tasklist)
		self.log('<h3>Table filter</h3><div class="column-group gutters" id="type_filter"></div>')
		self.log('<h2> Process starting </h2>')
		self.log('<table class="ink-table alternating bordered hover"><thead><tr><th width="10%">Time</th><th width="20%">Status</th><th width="70%">Event</th></tr></thead><tbody>')

	def log_init_machines(self):
		self.log('</tbody></table></div></div>')
		self.log('<div class="column-group gutters">')
		self.log('<h2 class="vspace">Machine work overview</h2>')

	def log_machine_state(self, machine_id, working_time, waiting_time, joblist):
		self.log('<div class="large-50" style="margin-top: 30px">')
		self.log('<h4>Machine '+str(machine_id)+'</h4>')
		self.log('<h5>Working/Waiting time:</h5>')
		self.log('<div class="ink-progress-bar"><span class="caption">Working time: '+str(working_time)+'</span><div class="bar green" style="width: '+\
			str(float(working_time) / float(working_time + waiting_time) * 100)+'%"></div></div>')
		self.log('<div class="ink-progress-bar"><span class="caption">Waiting time: '+str(waiting_time)+'</span><div class="bar red" style="width: '+\
			str(float(waiting_time) / float(working_time + waiting_time) * 100)+'%"></div></div>')
		self.log('<h5>Work overview</h5>')
		self.log('<table class="ink-table alternating bordered hover">')
		self.log('<tr><th>Task</th><th>Operation</th><th>Working time</th></tr>')
		for j in joblist:
			self.log('<tr><td>'+str(j[0])+'</td><td>'+str(j[1])+'</td><td>'+str(j[2])+'</td></tr>')
		self.log('</table></div>')

	def log_close(self):
		self.log('</div>')
		self.log('<script type="text/javascript">')
		self.log('function apply_filter(type) {')
		self.log("\t"+'if ($(\'.\'+type).css(\'display\') == "none")')
		self.log("\t\t"+'$(\'.\'+type).css(\'display\', \'\')')
		self.log("\t"+'else')
		self.log("\t\t"+'$(\'.\'+type).css(\'display\', \'none\')')
		self.log('}')
		self.log('$( document ).ready(function() {')
		for t in self.typelist:
			self.log('$(\'#type_filter\').append(\'<div class="large-20"><h4><input type="checkbox" id="'+t+'" onclick="apply_filter(\\\''+t+'\\\')" checked>'+
				'<label for="'+t+'">'+t+'</label></h4></div>\')')
		self.log('});')
		self.log('</script>')
		print(self.closehtml, file=self.f)
		self.f.close()

	def log(self, msg, newline=True):
		if newline:
			print(msg, file=self.f)
		else:
			self.f.write(msg)

	def log_event(self, it, type, event):
		if not type.lower() in self.typelist:
			self.typelist.append(type.lower())
		self.log('<tr class="'+ type.lower() +'"><td>'+str(it)+'</td><td>'+type+'</td><td>'+event+'</td></tr>');

	def log_event_error(self, it, type, event):
		if not type.lower() in self.typelist:
			self.typelist.append(type.lower())
		self.log('<tr class="ink-label error invert ' + type.lower() +'"><td>'+str(it)+'</td><td>'+type+'</td><td>'+event+'</td></tr>');
	def log_event_warning(self, it, type, event):
		if not type.lower() in self.typelist:
			self.typelist.append(type.lower())
		self.log('<tr class="ink-label warning invert ' + type.lower() +'"><td>'+str(it)+'</td><td>'+type+'</td><td>'+event+'</td></tr>');
	def log_event_info(self, it, type, event):
		if not type.lower() in self.typelist:
			self.typelist.append(type.lower())
		self.log('<tr class="ink-label info invert ' + type.lower() +'"><td>'+str(it)+'</td><td>'+type+'</td><td>'+event+'</td></tr>');
	def log_event_success(self, it, type, event):
		if not type.lower() in self.typelist:
			self.typelist.append(type.lower())
		self.log('<tr class="ink-label success invert ' + type.lower() +'"><td>'+str(it)+'</td><td>'+type+'</td><td>'+event+'</td></tr>');

	def log_tasklist(self, tasklist):
		self.log('<table class="ink-table alternating bordered hover">')
		for task in tasklist:
			self.log('<tr><td>')
			self.log('Task '+str(task.id)+', time of operations')
			self.log('</td></tr>')
			self.log('<tr><td><pre>[ ', newline=False)
			for time in task.oplist:
				self.log(str(time)+' ', newline=False);
			self.log(']</pre></td></tr>')
		self.log('</table>')





