import requests
import json

data = [ 67, 17.2, 38.9, 11.5, 30.6, 42.5, 49.2, 7.2, 36.1, 39, 39.9, 49.1, 15.2, 40.8,
54.7, 20.7, 54.5, 34.4, 43.1, 31, 37, 36.2, 40.2, 35, 36.2, 46, 32.5, 29.1 ]
data_json = json.dumps(data)
payload = {'json_payload': data_json}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post("http://localhost:8080/stem", data=data_json, headers=headers)
print response.text
