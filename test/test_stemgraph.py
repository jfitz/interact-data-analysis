import requests
import json

data = [
	{"maximum": 5, "values": [], "minimum": 0},
	{"maximum": 10, "values": [7.0, 7.0, 8.0, 8.0], "minimum": 5},
	{"maximum": 15, "values": [12.0, 13.0, 14.0], "minimum": 10},
	{"maximum": 20, "values": [15.0, 15.0, 15.0, 16.0, 17.0, 17.0], "minimum": 15},
	{"maximum": 25, "values": [21.0, 23.0], "minimum": 20},
	{"maximum": 30, "values": [25.0, 26.0, 29.0], "minimum": 25},
	{"maximum": 35, "values": [30.0, 30.0, 31.0, 31.0, 31.0, 31.0, 32.0, 33.0, 33.0, 34.0], "minimum": 30},
	{"maximum": 40, "values": [35.0, 35.0, 36.0, 36.0, 36.0, 36.0, 36.0, 37.0, 37.0, 38.0, 39.0, 39.0, 39.0, 39.0], "minimum": 35},
	{"maximum": 45, "values": [40.0, 40.0, 40.0, 41.0, 41.0, 42.0, 43.0, 43.0, 43.0, 43.0, 43.0, 43.0], "minimum": 40},
	{"maximum": 50, "values": [45.0, 46.0, 46.0, 46.0, 48.0, 48.0, 49.0, 49.0, 49.0], "minimum": 45},
	{"maximum": 55, "values": [], "minimum": 50},
	{"maximum": 60, "values": [55.0, 55.0, 57.0, 59.0], "minimum": 55},
	{"maximum": 65, "values": [60.0], "minimum": 60},
	{"maximum": 70, "values": [67.0], "minimum": 65}
]

data_json = json.dumps(data)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post("http://localhost:8080/stemgraph", data=data_json, headers=headers)
print response.text
