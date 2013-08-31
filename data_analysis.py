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

def stem_char(value, range_minimum, range_maximum, interval, power):
	factor = pow(10.0, power)
	delta = factor / 1000.0
	range_size = range_maximum - range_minimum
	range_midpoint = (range_maximum + range_minimum) / 2.0
	value_less_than_midpoint = False
	if value > 0:
		if range_midpoint - value - delta > 0.0:
			value_less_than_midpoint = True
	else:
		if range_midpoint - value + delta < 0.0:
			value_less_than_midpoint = True

	format = '%0' + str(power) + 'd'

	if value < 0:
		x1 = math.fabs(math.fabs(value) - math.fabs(range_maximum))
	else:
		x1 = value - range_minimum

	if math.fabs(value) < 1.0:
		x2 = int(x1 / factor * 10.0 + delta)
	else:
		x2 = int(x1)

	x3 = format % x2

	if interval == 1:
		retval = x3[0]
	else:
		if value_less_than_midpoint:
			retval = x3[0]
		else:
			retval = '@' 
	return retval

def compute_group_info(maximum_value):
	power = 1
	if maximum_value < 1:
		while 10.0 ** power > maximum_value:
			power -= 1
		power += 1
		interval = 5
		step_size = (10.0 ** power) * interval
		while (maximum_value / step_size) < 5:
			if interval == 5:
				interval = 2
			else:
				if interval == 2:
					interval = 1
				else:
					interval = 5
					power -= 1
			step_size = (10.0 ** power) * interval
	else:
		interval = 1
		step_size = int((10.0 ** power) * interval)
		while (maximum_value / step_size) > 20:
			if interval == 1:
				interval = 2
			else:
				if interval == 2:
					interval = 5
				else:
					interval = 1
					power += 1
			step_size = int((10.0 ** power) * interval)
			
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

def group_values(values):
	groups = []
	maximum = max(values)
	minimum = min(values)
	data_range = maximum - minimum
	step_size, interval, power = compute_group_info(data_range)
	i = 0
	while i > minimum:
		i -= step_size
	while i < 0:
		range_minimum = i
		range_maximum = range_minimum + step_size
		group_values = []
		for value in values:
			if value >= range_minimum and value < range_maximum:
				group_values.append(value)
		group_values.sort()
		groups.append( { 'minimum': range_minimum, 'maximum': range_maximum, 'values': group_values } )
		i += step_size
	i = 0
	while i < maximum:
		range_minimum = i
		range_maximum = range_minimum + step_size
		group_values = []
		for value in values:
			if value >= range_minimum and value < range_maximum:
				group_values.append(value)
		group_values.sort()
		groups.append( { 'minimum': range_minimum, 'maximum': range_maximum, 'values': group_values } )
		i += step_size
	return groups

def stem_graph(groups):
	stem_tuples = []
	range_maximum = 0
	range_minimum = 0
	for group in groups:
		range_maximum = max(group["maximum"], range_maximum)
		range_minimum = min(group["minimum"], range_minimum)
	step_size, interval, leader_power = compute_group_info(range_maximum)
	for group in groups:
		leader = int(group['minimum'] / pow(10, leader_power))
		value_chars = []
		for value in group['values']:
			char = stem_char(value, group["minimum"], group["maximum"], interval, leader_power)
			value_chars.append(char)
		value_chars.sort()
		stem_tuples.append( {'leader': leader, 'values': ''.join(value_chars)} )
	return stem_tuples
	
def stem_tuples_to_text(stem_tuples):
	text_lines = []
	leader_length = 2 if (len(stem_tuples) > 10) else 1
	for stem_tuple in stem_tuples:
		leader = stem_tuple['leader']
		this_leader_length = leader_length
		if leader < 0:
			this_leader_length += 1
		leader_format = '%0' + str(this_leader_length) + 'd'
		leader_string = leader_format % leader
		text_lines.append(leader_string + '|' + stem_tuple['values'])
	return text_lines

def transform_power(values, power):
	transformed_values = []
	for value in values:
		transformed_values.append(value ** power)
	return transformed_values

def transform_log(values):
	transformed_values = []
	for value in values:
		transformed_values.append(math.log10(value))
	return transformed_values

class MainPage(webapp.RequestHandler):
	def get(self):
		template_values = { }
		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))

class CondenseValues(webapp.RequestHandler):
	def post(self):
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write( json.dumps( condense( json.loads(self.request.body) ) ) )
		
class GroupValues(webapp.RequestHandler):
	def post(self):
		self.response.headers['Content-Type'] = 'application/json'
		values = json.loads(self.request.body)
		stem = group_values(values)
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
		
class TransformPower(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		values = json.loads(body)
		power = float(self.request.get('power'))
		transformed_values = transform_power(values, power)
		self.response.out.write( json.dumps( transformed_values ) )
		
class TransformLog(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		values = json.loads(body)
		transformed_values = transform_log(values)
		self.response.out.write( json.dumps( transformed_values ) )
		
application = webapp.WSGIApplication(
	[
		('/', MainPage),
		('/condense', CondenseValues),
		('/group', GroupValues),
		('/stemgraph', StemGraph),
		('/transform/power', TransformPower),
		('/transform/log', TransformLog)
	],
	debug=False)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
