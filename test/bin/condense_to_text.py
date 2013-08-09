import sys
import json

file_text = sys.stdin.read()
json_data = json.loads(file_text)
keys = json_data.keys()
keys.sort()
for key in keys:
	print key + ": " + str(json_data[key])
