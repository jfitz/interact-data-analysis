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
	count = len(points)
	upper_quartile = points[math.trunc(round(len(points)*0.75))]
	lower_quartile = points[math.trunc(round(len(points)*0.25))]
	iq = upper_quartile - lower_quartile
	upper_outlier_bound = upper_quartile + iq
	lower_outlier_bound = lower_quartile - iq
	mean = sum(points)/len(points)
	deviations = [x - mean for x in points]
	result = {
		'sum': sum(points),
		'count': count,
		'minimum': min(points),
		'maximum': max(points),
		'mean': mean,
		'mean_deviation': sum([abs(x - mean) for x in points])/count,
		'median': numpy.median(points),
		'standard_deviation': pow(sum([pow(x - mean, 2) for x in points])/count, 0.5),
		'upper_quartile': upper_quartile,
		'lower_quartile': lower_quartile,
		'upper_outliers': [x for x in points if x > upper_outlier_bound],
		'lower_outliers': [x for x in points if x < lower_outlier_bound]
	}
	return result

def outlier_character(value):
	if value == 0:
		return ' '
	if value < 10:
		return str(value)
	return '+'

def box_plot_text_horiz(lower_outlier_pos, scaled_lower_outliers, lower_quartile_pos, median_pos, upper_quartile_pos, upper_outlier_pos, scaled_upper_outliers, scale):
	lines = []
	line = ''
	# lower outliers
	for i in range(0, lower_outlier_pos - 1):
		line += outlier_character(scaled_lower_outliers.get(i, 0))
	line += '['

	# lower quartile
	line += '-' * (lower_quartile_pos - lower_outlier_pos - 2)
	line += 'L'

	# points around median
	line += '-' * (median_pos - lower_quartile_pos - 2)
	line += 'M'
	line += '-' * (upper_quartile_pos - median_pos - 2)

	# upper quartile
	line += 'U'
	line += '-' * (upper_outlier_pos - upper_quartile_pos - 2)

	# upper outliers
	line += ']'
	for i in range(upper_outlier_pos + 1, int(scale)):
		line += outlier_character(scaled_upper_outliers.get(i, 0))

	lines.append(line)

	return lines

def box_plot_text(condensed_points, orientation):
	data_range = condensed_points['maximum'] - condensed_points['minimum']
	scale = 100.0
	min_pos = 0
	max_pos = int(scale)
	median_pos = int((condensed_points['median'] - condensed_points['minimum']) / data_range * scale)
	upper_quartile_pos = int((condensed_points['upper_quartile'] - condensed_points['minimum']) / data_range * scale)
	lower_quartile_pos = int((condensed_points['lower_quartile'] - condensed_points['minimum']) / data_range * scale)
	iq = upper_quartile_pos - lower_quartile_pos
	upper_outlier_pos = min(upper_quartile_pos + iq, int(scale))
	lower_outlier_pos = max(lower_quartile_pos - iq, 0)

	scaled_lower_outliers = {}
	for point in condensed_points['lower_outliers']:
		scaled_point = int((point - condensed_points['minimum']) / data_range * scale)
		scaled_lower_outliers[scaled_point] = scaled_lower_outliers.get(scaled_point, 0) + 1

	scaled_upper_outliers = {}
	for point in condensed_points['upper_outliers']:
		scaled_point = int((point - condensed_points['minimum']) / data_range * scale)
		scaled_upper_outliers[scaled_point] = scaled_upper_outliers.get(scaled_point, 0) + 1

	lines = []
	if orientation == 'horizontal':
		lines = box_plot_text_horiz(lower_outlier_pos, scaled_lower_outliers, lower_quartile_pos, median_pos, upper_quartile_pos, upper_outlier_pos, scaled_upper_outliers, scale)
	return lines

def box_plot_processing(condensed_values, orientation):
	if orientation == 'vertical':
		template = jinja_environment.get_template('templates/vertical_boxplot.processing.jinja')
	else:
		template = jinja_environment.get_template('templates/horizontal_boxplot.processing.jinja')

	return template.render(condensed_values)

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
		if math.fabs(range_maximum) < 1e-16:
			range_maximum = 0
		group_values = []
		for value in values:
			if value >= range_minimum and value < range_maximum:
				group_values.append(value)
		group_values.sort()
		groups.append( { 'minimum': range_minimum, 'maximum': range_maximum, 'values': group_values } )
		i += step_size
		if math.fabs(i) < 1e-16:
			i = 0
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
	step_size, interval, leader_power = compute_group_info(range_maximum - range_minimum)
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

def transform_normalize(values):
	bias = min(values)
	scale = max(values) - bias
	transformed_values = []
	for value in values:
		transformed_values.append((value - bias) / scale)
	return transformed_values

def transform_zerobase(values):
	transformed_values = []
	bias = min(values)
	for value in values:
		transformed_values.append(value - bias)
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

class BoxPlot(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		format = self.request.get('format', 'text')
		orientation = self.request.get('orientation', 'horizontal')
		values = json.loads(body)
		box_plot_lines = []
		if format == 'text':
			box_plot_lines = box_plot_text(values, orientation)
			for line in box_plot_lines:
				self.response.out.write(line)
				self.response.out.write("\n")
		if format == 'processing':
			box_plot_lines = box_plot_processing(values, orientation)
			self.response.out.write(box_plot_lines)

class GroupValues(webapp.RequestHandler):
	def post(self):
		self.response.headers['Content-Type'] = 'application/json'
		values = json.loads(self.request.body)
		stem = group_values(values)
		self.response.out.write( json.dumps(stem) )

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
		power = float(self.request.get('power', '1.0'))
		transformed_values = transform_power(values, power)
		self.response.out.write( json.dumps( transformed_values ) )

class TransformLog(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		values = json.loads(body)
		transformed_values = transform_log(values)
		self.response.out.write( json.dumps( transformed_values ) )

class TransformNormalize(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		values = json.loads(body)
		transformed_values = transform_normalize(values)
		self.response.out.write( json.dumps( transformed_values ) )

class TransformZeroBase(webapp.RequestHandler):
	def post(self):
		body = self.request.body
		values = json.loads(body)
		transformed_values = transform_zerobase(values)
		self.response.out.write( json.dumps( transformed_values ) )

application = webapp.WSGIApplication(
	[
		('/', MainPage),
		('/condense', CondenseValues),
		('/boxplot', BoxPlot),
		('/group', GroupValues),
		('/stemgraph', StemGraph),
		('/transform/power', TransformPower),
		('/transform/log', TransformLog),
		('/transform/normalize', TransformNormalize),
		('/transform/zerobase', TransformZeroBase)
	],
	debug=False)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
