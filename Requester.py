import requests
import time
from pprint import pprint

KEY = "RGAPI-c40eda3c-45e1-4705-9dac-173ee2c4e14c"
DEBUG = True

def dprint(*args):
	if DEBUG:
		print(*args)

def dpprint(arg):
	if DEBUG:
		pprint(arg)

class Requester:
	def __init__(self):
		self._rateMap = {}
		self.state = 0
		self.time_limit_reached = 0

	def request(self, reqStr: str) -> requests.Response:
		dprint("\nRequesting", reqStr)

		response = requests.get("https://na1.api.riotgames.com/lol/" + reqStr + "?api_key="+KEY)
		if response.status_code != 200:
			print(f"request {reqStr} returned code {response.status_code}")
			return None

		dprint("date:", response.headers["Date"])
		dprint("app: ", response.headers["X-App-Rate-Limit-Count"], "/", response.headers["X-App-Rate-Limit"])
		dprint("method: ", response.headers["X-Method-Rate-Limit-Count"], "/", response.headers["X-Method-Rate-Limit"])
		dprint([key for key in response.headers])
		dpprint(response.json())

		return response

	def is_ready(self):
		return not self.state # state is 0