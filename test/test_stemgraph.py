import requests
import json

data = [{"minimum": 0, "maximum": 5, "values": []}, {"minimum": 5, "maximum": 10, "values": [7.2]}, {"minimum": 10, "maximum": 15, "values": [11.5]}, {"minimum": 15, "maximum": 20, "values": [15.2, 17.2]}, {"minimum": 20, "maximum": 25, "values": [20.7]}, {"minimum": 25, "maximum": 30, "values": [29.1]}, {"minimum": 30, "maximum": 35, "values": [30.6, 31, 32.5, 34.4]}, {"minimum": 35, "maximum": 40, "values": [35, 36.1, 36.2, 36.2, 37, 38.9, 39, 39.9]}, {"minimum": 40, "maximum": 45, "values": [40.2, 40.8, 42.5, 43.1]}, {"minimum": 45, "maximum": 50, "values": [46, 49.1, 49.2]}, {"minimum": 50, "maximum": 55, "values": [54.5, 54.7]}, {"minimum": 55, "maximum": 60, "values": []}, {"minimum": 60, "maximum": 65, "values": []}]
data_json = json.dumps(data)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post("http://localhost:8080/stemgraph", data=data_json, headers=headers)
print response.text
