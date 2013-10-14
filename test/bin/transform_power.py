import sys
import requests

power = 2.0
if len(sys.argv) > 1:
	power = float(sys.argv[1])

file_text = sys.stdin.read()
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

response = requests.post("http://localhost:8080/transform/power?power=" + str(power), data=file_text, headers=headers)
# response = requests.post("http://interact-data-analysis.appspot.com/condense", data=file_text, headers=headers)
print response.text
