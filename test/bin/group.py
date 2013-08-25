import sys
import requests

file_text = sys.stdin.read()
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post("http://localhost:8080/group", data=file_text, headers=headers)
print response.text
