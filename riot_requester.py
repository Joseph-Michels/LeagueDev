import requests
import time
from pprint import pprint as pprint_function
import builtins

KEY = "RGAPI-c40eda3c-45e1-4705-9dac-173ee2c4e14c"

def tprint(*args):
	if Requester.trace:
		builtins.print(*args)
print = tprint

def tpprint(arg):
	if Requester.trace:
		pprint_function(arg)
pprint = tpprint

class Requester:
	requester = None
	trace = False

	def __init__(self):
		self._rateMap = {}
		self.state = 0
		self.time_limit_reached = 0

	def request(self, url:str) -> requests.Response:
		print(f'Attempting to Request "{url}"')

		response = requests.get("https://na1.api.riotgames.com/lol/" + url + "?api_key="+KEY)
		if response.status_code != 200:
			print(f"request returned code {response.status_code}")
			return None

		print(f"  date: {response.headers['Date']}")

		app_limits = response.headers['X-App-Rate-Limit'].split(',')
		app_counts = response.headers['X-App-Rate-Limit-Count'].split(',')
		app_rate_limits = []
		for i in range(len(app_limits)): # relies on correlated limit and count strings
			limit_ratio, count_ratio = app_limits[i], app_counts[i]
			limit_colon = limit_ratio.index(':')
			max_rate = int(limit_ratio[:limit_colon])
			duration = int(limit_ratio[limit_colon+1:])
			count = int(count_ratio[:count_ratio.index(':')])
			app_rate_limits.append((count, max_rate, duration))
		print(f"  app: ({' | '.join(f'{count}/{max} in {duration}s' for count, max, duration in app_rate_limits)})")

		method_limits = response.headers['X-Method-Rate-Limit'].split(',')
		method_counts = response.headers['X-Method-Rate-Limit-Count'].split(',')
		method_rate_limits = []
		for i in range(len(method_limits)): # relies on correlated limit and count strings
			limit_ratio, count_ratio = method_limits[i], method_counts[i]
			limit_colon = limit_ratio.index(':')
			max_rate = int(limit_ratio[:limit_colon])
			duration = int(limit_ratio[limit_colon+1:])
			count = int(count_ratio[:count_ratio.index(':')])
			method_rate_limits.append((count, max_rate, duration))
		print(f"  method: ({' | '.join(f'{count}/{max} in {duration}s' for count, max, duration in method_rate_limits)})")
		
		print(f"  headers {[key for key in response.headers]}")
		
		pprint(response.json())
		
		print("")

		return response

	def is_ready(self):
		return not self.state # state is 0

def get(trace:bool = False):
	Requester.trace = trace
	if Requester.requester == None:
		Requester.requester = Requester()
	return Requester.requester