import requests
import pyrebase
from time import time as get_long_time
get_time = lambda : get_long_time() - 1500000000

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
	Calls pprint on iterables (for pretty print) and print on other objects.
	"""
	if Requester.trace:
		if len(kargs) == 0 and len(args) == 1 and type(args[0]) is not str:
			try:
				iterable = iter(args[0])
				pprint(args[0]) # pretty print iterables
				return
			except:
				pass
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


	def request(self, req_type:str):# -> requests.Response:
		"""
		Requests information from the Riot Games API. Checks and updates rate limits.
		"""
		msg = f'Attempting to Request "{req_type}"'
		trace('-'*len(msg))
		trace(msg)

		self._remove_old_timestamps(req_type)
		if self._can_request(req_type):
			url = _get_url(req_type)
			response = self._get_handle_response(url)
			if response is not None:
				self._add_timestamps(response.headers, req_type)

			return response
		else:
			print(f'Cannot request "{req_type}" due to rate limits.')
			return None


	def _remove_old_timestamps(self, req_type:str):
		time = get_time()

		app_data = self.get_timestamps('app').get(self.user['idToken']).val()
		if type(app_data) is dict:
			for duration, limit_timestamp_dict in app_data.items():
				if 'timestamps' in limit_timestamp_dict:
					for key, timestamp in limit_timestamp_dict['timestamps'].items():
						if time > timestamp + int(duration):
							self.get_timestamps('app').child(f"{duration}/timestamps/{key}").remove(self.user['idToken'])

		method_data = self.get_timestamps('method').child(req_type).get(self.user['idToken']).val()
		if type(method_data) is dict:
			for duration, limit_timestamp_dict in method_data.items():
				if 'timestamps' in limit_timestamp_dict:
					for key, timestamp in limit_timestamp_dict['timestamps'].items():
						if time > timestamp + int(duration):
							self.get_timestamps('method').child(f"{req_type}/{duration}/timestamps/{key}").remove(self.user['idToken'])


	def _can_request(self, req_type:str):# -> bool:
		app_data = self.get_timestamps('app').get(self.user['idToken']).val()
		if type(app_data) is dict:
			for duration, limit_timestamp_dict in app_data.items():
				if 'timestamps' in limit_timestamp_dict and len(limit_timestamp_dict['timestamps']) >= int(limit_timestamp_dict['limit']):
					trace(f"App: Called {len(limit_timestamp_dict['timestamps'])}/{limit_timestamp_dict['limit']} in {duration}s")
					return False

		method_data = self.get_timestamps('method').child(req_type).get(self.user['idToken']).val()
		if type(method_data) is dict:
			for duration, limit_timestamp_dict in method_data.items():
				if 'timestamps' in limit_timestamp_dict and len(limit_timestamp_dict['timestamps']) >= int(limit_timestamp_dict['limit']):
					trace(f"Method: Called {len(limit_timestamp_dict['timestamps'])}/{limit_timestamp_dict['limit']} in {duration}s")
					return False

		return True


	def _get_handle_response(self, url:str):# -> requests.Response:
		response = requests.get("https://na1.api.riotgames.com/lol/" + url + "?api_key="+KEY)

		if response.status_code == 200:
			trace(response.json())
			return response
		elif response.status_code == 429:
			time = get_time()
			if 'X-Rate-Limit-Type' in response.headers:
				rate_limit_type = response.headers['X-Rate-Limit-Type']
				retry_after = response.headers['Retry-After']
				trace(f"EXCEEDED RATE LIMIT: {rate_limit_type}, retry after {retry_after}s")
				if rate_limit_type == 'application':
					pass
				elif rate_limit_type == 'method':
					pass
				elif rate_limit_type == 'service':
					pass
				else:
					raise Error(f"Unexpected rate_limit_type {rate_limit_type}")
			else:
				trace(f"EXCEEDED RATE LIMIT: back off exponentially until we receive a 200 response")
				pass

			return None
		else:
			raise Error(f"Request failed with code {response.status_code}")


	def _add_timestamps(self, resp_headers:dict, req_type:str):
		trace("  Adding Timestamps For Response")

		time = get_time()

		trace(f"    time: {time}")
		trace(f"    headers: {[key for key in resp_headers]}")

		# gets rate limits in array of "max_calls:duration"
		app_limits_arr = resp_headers['X-App-Rate-Limit'].split(',')
		app_limits_dict = {}
		method_limits_arr = resp_headers['X-Method-Rate-Limit'].split(',')
		method_limits_dict = {}

		# parses this array of strings
		for ratio_str in app_limits_arr:
			colon_idx = ratio_str.index(':')

			max_calls = int(ratio_str[:colon_idx])
			duration = int(ratio_str[colon_idx+1:])

			d = {"limit": max_calls, "timestamps/"+self.firebase.database().generate_key():time}
			app_limits_dict[duration] = d
			result = self.get_timestamps('app').child(duration).update(d, self.user['idToken'])
		for ratio_str in method_limits_arr:
			colon_idx = ratio_str.index(':')

			max_calls = int(ratio_str[:colon_idx])
			duration = int(ratio_str[colon_idx+1:])

			d = {"limit": max_calls, "timestamps/"+self.firebase.database().generate_key():time}
			method_limits_dict[duration] = d
			result = self.get_timestamps('method').child(f"{req_type}/{duration}").update(d, self.user['idToken'])

		# debug
		trace("    app: (", " | ".join(f"{d['limit']} in {duration}s" for duration, d in app_limits_dict.items()), ")")
		trace(f'    method "{req_type}": (', " | ".join(f"{d['limit']} in {duration}s" for duration, d in method_limits_dict.items()), ")")


	def get_timestamps(self, timestamp_type:str = None):
		assert timestamp_type in (None, 'Method', 'method', 'App', 'app')
		return self.firebase.database().child(f"timestamps{'' if timestamp_type==None else f'/{timestamp_type.lower()}'}")
	
	

	def update_trace(self, new_trace):
		Requester.trace = new_trace


class UrlBuilder:
	def __init__(self, url:str):
		self.url = url
		self.prompts = set()
		last_idx = 0
		for i in range(url.count("{")):
			open_idx, close_idx = url.find("{", last_idx), url.find("}", last_idx)
			self.prompts.add(url[open_idx+1:close_idx])
			last_idx = open_idx

	def prompt(self, *args):
		print(f'Constructing URL "{self.url}"')
		params = {}
		for prompt in self.prompts:
			params[prompt] = input(f'    Enter "{prompt}": ')
		s = self.url.format(**params)
		return s

REQ_DICT = {
	"summoner_info": UrlBuilder("summoner/v4/summoners/by-name/{summoner_name}")
}

def _get_url(req_type:str):
	assert req_type in REQ_DICT

#	url = REQ_DICT[req_type].prompt()
	url = REQ_DICT[req_type].url.format(summoner_name='TsimpleT')
	params = {}

	trace(url)
	return url


def get(trace:bool = False):# -> Requester
	if Requester.instance == None:
		print("CREATED NEW SINGLETON REQUESTER INSTANCE\n")
		Requester.instance = Requester()
	Requester.instance.update_trace(trace)
	return Requester.instance