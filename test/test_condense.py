import requests
import json

data = [ 10, 20, 30 ]
data_json = json.dumps(data)
payload = {'json_payload': data_json}
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post("http://localhost:8080/condense", data=data_json, headers=headers)
print response.text
