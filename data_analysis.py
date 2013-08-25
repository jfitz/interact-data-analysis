from __future__ import division
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import time, re, datetime
import jinja2
import os
import json
import math
import numpy

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def fraction(value):
	return value - math.trunc(value)

def remainder(value, power):
	factor = pow(10.0, power)
	format = '%0' + str(power) + 'd'
	x1 = fraction(value / factor) * factor
	x2 = format % x1
	return x2[0]

def compute_power(maximum_value):
	power = 1
	interval = 1
	step_size = int(pow(10.0, power) * interval)
	while (maximum_value / step_size) > 20:
		if interval == 1:
			interval = 2
		else:
			if interval == 2:
				interval = 5
			else:
				interval = 1
				power += 1
		step_size = int(pow(10.0, power) * interval)
	return (step_size, interval, power)

def condense(points):
	points.sort()
	result = {
		'sum': sum(points),
		'count':len(points),
		'minimum': min(points),
		'maximum': max(points),
		'median': numpy.median(points),
		'upper_quartile': points[math.trunc(round(len(points)*0.75))],
		'lower_quartile': points[math.trunc(round(len(points)*0.25))]
	}
	return result

def stem_split(values):
	branches = []
	maximum = max(values)
	minimum = min(values)
	data_range = maximum - minimum
	step_size, interval, power = compute_power(data_range)
	i = 0
	while i < maximum:
		range_minimum = i
		range_maximum = range_minimum + step_size
		branch_values = []
		for value in values:
			if value >= range_minimum and value < range_maximum:
				branch_values.append(value)
		branch_values.sort()
		branches.append( { 'minimum': range_minimum, 'maximum': range_maximum, 'values': branch_values } )
		i += step_size
	return branches

def stem_graph(branches):
	stem_tuples = []
	range_maximum = 0
	range_minimum = 0
	for branch in branches:
		range_maximum = max(branch["maximum"], range_maximum)
		range_minimum = min(branch["minimum"], range_minimum)
	step_size, interval, power = compute_power(range_maximum)
	for branch in branches:
		leader = int(branch['minimum'] / pow(10, power))
		value_chars = []
		for value in branch['values']:
			char = remainder(value, power)
			value_chars.append(char)
		value_chars.sort()
		stem_tuples.append( {'leader': leader, 'values': ''.join(value_chars)} )
	return stem_tuples
	
def stem_tuples_to_text(stem_tuples):
	text_lines = []
	leader_length = 2 if (len(stem_tuples) > 10) else 1
	leader_format = '%0' + str(leader_length) + 'd'
	for stem_tuple in stem_tuples:
		text_lines.append(leader_format % stem_tuple['leader'] + '|' + stem_tuple['values'])
	return text_lines

class MainPage(webapp.RequestHandler):
	def get(self):
		template_values = { }
		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))

class Condense(webapp.RequestHandler):
	def post(self):
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write( json.dumps( condense( json.loads(self.request.body) ) ) )
		
class Stem(webapp.RequestHandler):
	def post(self):
		self.response.headers['Content-Type'] = 'application/json'
		values = json.loads(self.request.body)
		stem = stem_split(values)
		self.response.out.write( json.dumps( stem ) )
		
class StemGraph(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		stem = json.loads(body)
		stem_tuples = stem_graph(stem)
		stem_texts = stem_tuples_to_text(stem_tuples)
		for text_line in stem_texts:
			self.response.out.write(text_line)
			self.response.out.write("\n")
		
application = webapp.WSGIApplication(
	[
		('/', MainPage),
		('/condense', Condense),
		('/stem', Stem),
		('/stemgraph', StemGraph)
	],
	debug=False)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
