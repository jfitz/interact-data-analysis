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

def power_to_factor(power):
	return pow(10.0, power)

def front(value, power):
	factor = power_to_factor(power)
	return math.trunc((value / factor) + 0.5)

def fraction(value):
	return value - math.trunc(value)

def remainder(value, power):
	factor = power_to_factor(power)
	format = '%0' + str(power) + 'd'
	x1 = fraction(value / factor) * factor
	x2 = format % x1
	return x2[0]

def compute_power(maximum_value):
	power = 1
	while (maximum_value / power_to_factor(power)) > 20:
		power += 1
	return power

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

def stem_split(values, num_branches, power):
	branches = []
	factor = power_to_factor(power)
	for i in range(num_branches):
		minimum = i * factor
		maximum = (i + 1) * factor
		branch_values = []
		for value in values:
			rounded_value = value + (0.05 * factor)
			if rounded_value >= minimum and rounded_value < maximum:
				branch_values.append(rounded_value)
		branches.append( { 'minimum': minimum, 'maximum': maximum, 'values': branch_values } )
	return branches

def stem_graph(branches, power):
	stem_tuples = []
	for branch in branches:
		leader = front(int(branch['minimum']), power)
		value_chars = []
		for value in branch['values']:
			char = remainder(value, power)
			value_chars.append(char)
		value_chars.sort()
		stem_tuples.append( (leader, ''.join(value_chars)) )
	return stem_tuples
	
def stem_tuples_to_text(stem_tuples, leader_format):
	text_lines = []
	for stem_tuple in stem_tuples:
		leader, values = stem_tuple
		text_lines.append(leader_format % leader + '|' + values)
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
		points = json.loads(self.request.body)
		condensed_points = condense( points )
		range = condensed_points["maximum"] - condensed_points["minimum"]
		power = compute_power(range)
		interquartile_distance = condensed_points['maximum'] - condensed_points['minimum']
		scale_factor = power_to_factor(power)
		num_branches = math.trunc( round((interquartile_distance / scale_factor) + 0.5) ) + 1
		stem = stem_split(points, num_branches, power)
		self.response.out.write( json.dumps( stem ) )
		
class StemGraph(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		stem = json.loads(body)
		maximum = 0
		for branch in stem:
			maximum = max(branch["maximum"], maximum)
		power = compute_power(maximum)
		leader_length = len(str(math.trunc(maximum))) - power
		leader_format = '%0' + str(leader_length) + 'd'
		stem_tuples = stem_graph(stem, power)
		stem_texts = stem_tuples_to_text(stem_tuples, leader_format)
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
