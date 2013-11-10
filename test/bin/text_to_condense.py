import sys
import json

def to_number(s):
	try:
		f = float(s)
		return f
	except ValueError:
		return s
        
file_text = sys.stdin.readlines()

dictionary = {}
for line in file_text:
	parts = line.strip().split(': ')
	if len(parts) == 2:
		name = parts[0]
		value = to_number(parts[1])
		dictionary[name] = value

print json.dumps(dictionary)
