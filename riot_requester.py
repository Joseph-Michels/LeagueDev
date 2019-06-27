import requests
import time
import pprint as pprint_module
import builtins

KEY = "RGAPI-c40eda3c-45e1-4705-9dac-173ee2c4e14c"

trace = True

def tprint(*args):
	if trace:
		builtins.print(*args)
print = tprint

def tpprint(arg):
	if trace:
		pprint_module.pprint(arg)
pprint = tpprint

class Requester:
	requester = None

	def __init__(self):
		self._rateMap = {}
		self.state = 0
		self.time_limit_reached = 0

	def request(self, url:str) -> requests.Response:
		print(f'Attempting to Request "{url}"')

		response = requests.get("https://na1.api.riotgames.com/lol/" + url + "?api_key="+KEY)
		if response.status_code != 200:
			print(f"request {url} returned code {response.status_code}")
			return None

		print(f"  date: {response.headers['Date']}")
		print(f"  app: {response.headers['X-App-Rate-Limit-Count']} / {response.headers['X-App-Rate-Limit']}")
		print(f"  method: {response.headers['X-Method-Rate-Limit-Count']} / {response.headers['X-Method-Rate-Limit']}")
		print(f"  {[key for key in response.headers]}")
		pprint(response.json())
		print("")

		return response

	def is_ready(self):
		return not self.state # state is 0

def get(trace:bool = False):
	if Requester.requester == None:
		Requester.requester = Requester()
	return Requester.requester