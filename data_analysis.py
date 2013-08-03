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

def stem_split(values, num_branches, scale_factor):
	branches = []
	for i in range(num_branches):
		minimum = i * scale_factor
		maximum = (i + 1) * scale_factor
		branch_values = []
		for value in values:
			rounded_value = round(value)
			if rounded_value >= minimum and rounded_value < maximum:
				branch_values.append(rounded_value)
		branches.append( { 'minimum': minimum, 'maximum': maximum, 'values': branch_values } )
	return branches

def stem_graph(branches):
	stem_tuples = []
	for branch in branches:
		leader_char = str(branch['minimum'] / 10)
		value_chars = []
		for value in branch['values']:
			value_chars.append(str(math.trunc((value / 10 - math.trunc(value / 10) + 0.05) * 10)))
		value_chars.sort()
		stem_tuples.append( (leader_char, ''.join(value_chars)) )
	return stem_tuples
	
def stem_tuples_to_text(stem_tuples):
	text_lines = []
	for stem_tuple in stem_tuples:
		leader, values = stem_tuple
		text_lines.append(leader + '|' + values)
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
		scale_factor = 5
		interquartile_distance = condensed_points['maximum'] - condensed_points['minimum']
		num_branches = math.trunc( round((interquartile_distance / scale_factor) + 0.5) ) + 1
		stem = stem_split(points, num_branches, scale_factor)
		self.response.out.write( json.dumps( stem ) )
		
class StemGraph(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		stem= json.loads(body)
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
