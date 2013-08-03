import requests
import json

data = [
67, 17.2, 38.9, 11.5, 30.6, 42.5, 49.2, 7.2, 36.1, 39, 39.9, 49.1, 15.2, 40.8,
54.7, 20.7, 54.5, 34.4, 43.1, 31, 37, 36.2, 40.2, 35, 36.2, 46, 32.5, 29.1,
7, 13, 59.8, 35.1, 56.8, 31.7, 35.9, 45.5, 42.7, 37, 42.8, 35.9, 44.7, 14.6,
48.5, 43.4, 48.3, 38.7, 40.8, 30.2, 15, 7.8, 42.5, 31.4, 46.4, 7.8, 38.8, 59.2,
14, 40.2, 22.9, 30.8, 41.8, 25.9, 30.2, 33.4, 16.2, 37.6, 24.7, 48.2, 17.4
]
data_json = json.dumps(data)
payload = {'json_payload': data_json}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post("http://interact-data-analysis.appspot.com/condense", data=data_json, headers=headers)
print response.text
