import sys
import requests

file_text = sys.stdin.read()
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post("http://localhost:8080/transform/scale", data=file_text, headers=headers)
# response = requests.post("http://interact-data-analysis.appspot.com/condense", data=file_text, headers=headers)
print response.text
