import sys
import json

file_text = sys.stdin.read()
json_data = json.loads(file_text)
for item in json_data:
	keys = item.keys()
	keys.sort()
	for key in keys:
		print key + ": " + str(item[key])
