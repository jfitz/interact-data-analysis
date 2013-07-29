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

class MainPage(webapp.RequestHandler):
	def get(self):
		template_values = { }
		template = jinja_environment.get_template('templates/index.html')
		self.response.out.write(template.render(template_values))

class Condense(webapp.RequestHandler):
	def post(self):
		point_data = json.loads(self.request.body)
		point_data.sort()
		t_list = {
			'sum': sum(point_data),
			'count':len(point_data),
			'minimum': min(point_data),
			'maximum': max(point_data),
			'median': numpy.median(point_data),
			'upper_quartile': point_data[math.trunc(round(len(point_data)*0.75))],
			'lower_quartile': point_data[math.trunc(round(len(point_data)*0.25))]
		}
		s = json.dumps( t_list )
		
		self.response.headers['Content-Type'] = 'application/json'
		self.response.out.write(s)

application = webapp.WSGIApplication(
	[
		('/', MainPage),
		('/condense', Condense)
	],
	debug=False)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
