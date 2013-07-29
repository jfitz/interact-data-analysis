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
	stem = []
	for i in range(num_branches):
		minimum = i * scale_factor
		maximum = (i + 1) * scale_factor
		branch_values = []
		for value in values:
			if value >= minimum and value < maximum:
				branch_values.append(value)
		stem.append( { 'minimum': minimum, 'maximum': maximum, 'values': branch_values } )
	return stem

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
		
application = webapp.WSGIApplication(
	[
		('/', MainPage),
		('/condense', Condense),
		('/stem', Stem)
	],
	debug=False)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
