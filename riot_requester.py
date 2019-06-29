import requests
import pyrebase
import time
from pprint import pprint

KEY = "RGAPI-c40eda3c-45e1-4705-9dac-173ee2c4e14c"
CONFIG = {
	'apiKey': "AIzaSyBkiDeRm6ZKergpdVH_zSBceTLNsLCrMLQ",
	'authDomain': "leaguedev-57c5d.firebaseapp.com",
	'databaseURL': "https://leaguedev-57c5d.firebaseio.com",
	'projectId': "leaguedev-57c5d",
	'storageBucket': "leaguedev-57c5d.appspot.com",
	'messagingSenderId': "44032877576",
	'appId': "1:44032877576:web:df52a4cd48875ecd"
}

def trace(*args, **kargs):
	"""
	Takes an object or objects and prints it or them if the Requester is tracing.
	Calls pprint on iterables and print on other objects.
	"""
	if Requester.trace:
		if len(kargs) == 0 and len(args) == 1 and '__dict__' in args[0] and '__iter__' in args[0].__dict__:
			pprint(args[0]) # pretty print iterables
		else:
			print(*args, **kargs)

def get_user(firebase:pyrebase.pyrebase.Firebase):# -> dict
	"""
	Returns a dict representing a firebase user (containing the idToken).
	Currently uses a default test account for two empty strings as inputs.
	"""
	print("SIGN IN TO FIREBASE")
	email = input("enter your email: ")
	passw = input("enter your password: ")
	if email == '' and passw == '':
		return firebase.auth().sign_in_with_email_and_password('bobelement4181@gmail.com', 'testtest')
	else:
		return firebase.auth().sign_in_with_email_and_password(email, passw)

class Requester:
	"""
	A class that handles requests of information about League of Legends from the Riot Games API.
	Uses firebase to respect the rate limits, and in the future to store data.
	"""
	instance = None
	trace = False

	def __init__(self):
		"""
		Creates a Requester object with firebase initialized. Also prompts the user for login to firebase.
		"""
		self.firebase = pyrebase.initialize_app(CONFIG)
		self.user = get_user(self.firebase)

	def request(self, url:str):# -> requests.Response:
		"""
		Requests information from the Riot Games API. Checks and updates rate limits.
		"""
		msg = f'Attempting to Request "{url}"'
		trace('-'*len(msg))
		trace(msg)

		if self._can_request(url):
			response = self._get_response(url)
			self._update_rate_limit(response, url)

			return response
		else:
			print(f"Cannot request {url}")
			return None

	def _can_request(self, url:str):# -> bool:
		return True

	def _get_response(self, url:str):# -> requests.Response:
		response = requests.get("https://na1.api.riotgames.com/lol/" + url + "?api_key="+KEY)

		if response.status_code != 200:
			raise Error(f"***Request failed with code {response.status_code}***")
			return None
		else:
			trace(response.json())
			return response

	def _update_rate_limit(self, response:requests.Response, url:str):
		trace("  Updating Rate Limit")
		trace(f"    date: {response.headers['Date']}")
		trace(f"    headers: {[key for key in response.headers]}")

		# gets rate limits and their counts in arrays of "n:duration" where n is max_calls for limits and count for counts
		app_limits = response.headers['X-App-Rate-Limit'].split(',')
		app_counts = response.headers['X-App-Rate-Limit-Count'].split(',')
		app_rate_limits = {}

		# parses this array of strings
		for i in range(len(app_limits)): # relies on correlated limit and count strings
			limit_ratio, count_ratio = app_limits[i], app_counts[i]
			limit_colon = limit_ratio.index(':')
			max_rate = int(limit_ratio[:limit_colon])
			duration = int(limit_ratio[limit_colon+1:])
			count = int(count_ratio[:count_ratio.index(':')])
			app_rate_limits[duration] = {'count':count, 'max':max_rate}
		trace("    app: (", " | ".join(f"{d['count']}/{d['max']} in {duration}s" for duration,d in app_rate_limits.items()), ")")

		method_limits = response.headers['X-Method-Rate-Limit'].split(',')
		method_counts = response.headers['X-Method-Rate-Limit-Count'].split(',')
		method_rate_limits = {}
		for i in range(len(method_limits)): # relies on correlated limit and count strings
			limit_ratio, count_ratio = method_limits[i], method_counts[i]
			limit_colon = limit_ratio.index(':')
			max_rate = int(limit_ratio[:limit_colon])
			duration = int(limit_ratio[limit_colon+1:])
			count = int(count_ratio[:count_ratio.index(':')])
			method_rate_limits[duration] = {'count':count, 'max':max_rate}
		trace(f'    method "{url}": (', " | ".join(f"{d['count']}/{d['max']} in {duration}s" for duration,d in method_rate_limits.items()), ")")

		app_result = self.firebase.database().child("rate_limits/app").set(app_rate_limits, self.user['idToken'])

	def update_trace(self, new_trace):
		Requester.trace = new_trace


def get(trace:bool = False):# -> Requester
	if Requester.instance == None:
		print("CREATED NEW SINGLETON REQUESTER INSTANCE\n")
		Requester.instance = Requester()
	Requester.instance.update_trace(trace)
	return Requester.instance