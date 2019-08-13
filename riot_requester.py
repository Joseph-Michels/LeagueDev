import requests
import pyrebase
from collections import OrderedDict
from time import time as _time
get_time = lambda : _time() - 1500000000
from pprint import pprint

'''
TODO:
TEST SERVICE EXPO SOMEHOW
'''

KEY = ""
CONFIG = ""

with open("keys/riot.txt", 'r') as f:
	KEY = f.readline().rstrip()
with open("keys/firebase.txt", 'r') as f:
	CONFIG = eval(f.read())

RIOT_URL = "https://na1.api.riotgames.com/"
PATCH = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
DDRAGON_URL = f"https://ddragon.leagueoflegends.com/cdn/{PATCH}/"

def trace(*args, **kargs):
	"""
	Takes an object or objects and prints it or them if the Requester is tracing.
	Calls pprint on iterables (for pretty print) and print on other objects.
	"""
	if Requester.trace:
		if len(kargs) == 0 and len(args) == 1 and type(args[0]) is not str:
			try:
				iter(args[0])
				pprint(args[0]) # pretty print iterables
				return
			except:
				pass
		print(*args, **kargs)

def _login_get_user(firebase:pyrebase.pyrebase.Firebase):# -> dict
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
		self._user_init_time = get_time()
		self._user = _login_get_user(self.firebase)

	def get_user(self):
		if get_time() > self._user_init_time + float(self._user['expiresIn']):
			self._user_init_time = get_time()
			self._user = self._firebase.auth().refresh(self._user['refreshToken'])
		return self._user

	def get_user_id_token(self):
		return self.get_user()['idToken']

	def request(self, req_type:str, **req_params_kargs):# -> requests.Response:
		"""
		Requests information from the Riot Games API. Checks and updates rate limits.
		Returns None if cannot request.
		"""
		msg = f'Attempting to Request "{req_type}"'
		trace('-'*len(msg))
		trace(msg)

		self._remove_old_timestamps(req_type)
		if self._can_request(req_type):
			response = self._get_handle_response(req_type, **req_params_kargs)
			if response is not None:
				self._add_timestamps(response.headers, req_type)
				return response.json()
		else:
			print(f'Cannot request "{req_type}" due to rate limits.')
		
		return None


	def _remove_old_timestamps(self, req_type:str):
		"""
		Removes old timestamps from firebase.
		"""
		time = get_time()

		# Remove old timestamps for calls to the app
		app_data = self.get_timestamps('app').get(self.get_user_id_token()).val()
		if type(app_data) is OrderedDict:
			for duration, limit_timestamp_dict in app_data.items():
				if 'timestamps' in limit_timestamp_dict:
					for key, timestamp in limit_timestamp_dict['timestamps'].items():
						if time > timestamp + int(duration):
							self.get_timestamps('app').child(f"{duration}/timestamps/{key}").remove(self.get_user_id_token())

		# Remove old timestamps for calls to this method
		method_data = self.get_timestamps('method').child(req_type).get(self.get_user_id_token()).val()
		if type(method_data) is OrderedDict:
			for duration, limit_timestamp_dict in method_data.items():
				if 'timestamps' in limit_timestamp_dict:
					for key, timestamp in limit_timestamp_dict['timestamps'].items():
						if time > timestamp + int(duration):
							self.get_timestamps('method').child(f"{req_type}/{duration}/timestamps/{key}").remove(self.get_user_id_token())


	def _can_request(self, req_type:str):# -> bool:
		"""
		Can request only when there are no current retry_after messages, and
		when the app/method have already been called too many times.
		"""

		'''check rate_limits retry_after timestamps'''
		time = get_time()
		
		app_rate_limit_data = self.get_rate_limits('app').get(self.get_user_id_token()).val()
		if type(app_rate_limit_data) is OrderedDict:
			for key, retry_after_timestamp in app_rate_limit_data.items():
				if time > retry_after_timestamp: # passed retry after mark, remove rate_limit
					self.get_rate_limits('app').child(key).remove(self.get_user_id_token())
				else:
					return False

		method_rate_limit_data = self.get_rate_limits('method').child(req_type).get(self.get_user_id_token()).val()
		if type(method_rate_limit_data) is OrderedDict:
			for key, retry_after_timestamp in method_rate_limit_data.items():
				if time > retry_after_timestamp: # passed retry after mark, remove rate_limit
					self.get_rate_limits('method').child(f"{req_type}/{key}").remove(self.get_user_id_token())
				else:
					return False

		service_rate_limit_data = self.get_rate_limits('service').get(self.get_user_id_token()).val()
		if type(service_rate_limit_data) is OrderedDict:
			for key, retry_after_timestamp in service_rate_limit_data.items():
				if time > retry_after_timestamp: # passed retry after mark, remove rate_limit
					self.get_rate_limits('service').child(key).remove(self.get_user_id_token())
				else:
					return False

		# for service_expo, dont remove because the retry_after is handled
		# exponentially and needs to be referred back to
		service_expo_rate_limit_data = self.get_rate_limits('service_expo').get(self.get_user_id_token()).val()
		if type(service_expo_rate_limit_data) is OrderedDict:
			for key, retry_timestamp_dict in service_expo_rate_limit_data.items():
				if time <= retry_timestamp_dict['timestamp'] + retry_timestamp_dict['retry_after']:
					return False
					
		'''check number of previous calls'''
		app_timestamp_data = self.get_timestamps('app').get(self.get_user_id_token()).val()
		if type(app_timestamp_data) is OrderedDict:
			for duration, limit_timestamp_dict in app_timestamp_data.items():
				if 'timestamps' in limit_timestamp_dict and len(limit_timestamp_dict['timestamps']) >= int(limit_timestamp_dict['limit']):
					trace(f"App: Called {len(limit_timestamp_dict['timestamps'])}/{limit_timestamp_dict['limit']} in {duration}s")
					return False

		method_timestamp_data = self.get_timestamps('method').child(req_type).get(self.get_user_id_token()).val()
		if type(method_timestamp_data) is OrderedDict:
			for duration, limit_timestamp_dict in method_timestamp_data.items():
				if 'timestamps' in limit_timestamp_dict and len(limit_timestamp_dict['timestamps']) >= int(limit_timestamp_dict['limit']):
					trace(f"Method: Called {len(limit_timestamp_dict['timestamps'])}/{limit_timestamp_dict['limit']} in {duration}s")
					return False

		return True


	def _get_handle_response(self, req_type:str, **req_params_kargs):# -> requests.Response:
		"""
		Uses the requests api to make the request. Handles rate limits and adds
		retry_after messages to firebase.
		"""
		url = _get_req_url(req_type, **req_params_kargs)
		response = requests.get(f"{RIOT_URL}{url}?api_key={KEY}")

		if response.status_code == 200: # return if ok (200)
			trace(response.json())
			return response
		elif response.status_code == 429: # got rate limited, add retry_after
			time = get_time()
			if 'X-Rate-Limit-Type' in response.headers:
				retry_after = response.headers['Retry-After']
				retry_after_timestamp = retry_after + time
				rate_limit_type = response.headers['X-Rate-Limit-Type']
				trace(f"EXCEEDED RATE LIMIT: {rate_limit_type}, retry after {retry_after}s")
				
				if rate_limit_type == 'application':
					self.get_rate_limits('app').push(retry_after_timestamp, self.get_user_id_token())
				elif rate_limit_type == 'method':
					self.get_rate_limits('method').child(req_type).push(retry_after_timestamp, self.get_user_id_token())
				elif rate_limit_type == 'service':
					self.get_rate_limits('service').push(retry_after_timestamp, self.get_user_id_token())
				else:
					raise Error(f"Unexpected rate_limit_type {rate_limit_type}")
			else:
				def get_retry_after_timestamp(d):
					return d['timestamp'] + d['retry_after']
				trace(f"EXCEEDED RATE LIMIT: back off exponentially until we receive a 200 response")
				prev_rate_limits = self.get_rate_limits('service_expo').get(self.get_user_id_token()).val()
				highest_retry_after = 1
				if type(prev_rate_limits) is OrderedDict:
					for key, retry_timestamp_dict in prev_rate_limits.items():
						# if timestamp passed
						if time > get_retry_after_timestamp(retry_timestamp_dict):
							# remove all passed timestamps
							self.get_rate_limits('service_expo').child(key).remove(self.get_user_id_token())
							this_retry_after = retry_timestamp_dict['retry_after']
							if this_retry_after > highest_retry_after:
								highest_retry_after = this_retry_after
						else:
							# no need to add a new timestamp if one has not been passed yet
							return None
						
				print(prev_rate_limits)
				# add timestamp with doubled retry_after
				self.get_rate_limits('service_expo').push({'timestamp': time, 'retry_after': 2*highest_retry_after}, self.get_user_id_token())

			return None
		else:
			raise Error(f"Request failed with unexpected response code {response.status_code}")


	def _add_timestamps(self, resp_headers:dict, req_type:str):
		"""
		Add timestamps of calls to the app and this method to firebase.
		"""
		trace("  Adding Timestamps For Response")

		time = get_time()

		trace(f"    time: {time}")
		trace(f"    headers: {[key for key in resp_headers]}")

		# get rate limits in array of "max_calls:duration"
		# parses this array of strings
		if 'X-App-Rate-Limit' in resp_headers:
			app_limits_arr = resp_headers['X-App-Rate-Limit'].split(',')
			app_limits_dict = {}

			for ratio_str in app_limits_arr:
				colon_idx = ratio_str.index(':')

				max_calls = int(ratio_str[:colon_idx])
				duration = int(ratio_str[colon_idx+1:])

				d = {"limit": max_calls, "timestamps/"+self.firebase.database().generate_key():time}
				app_limits_dict[duration] = d
				result = self.get_timestamps('app').child(duration).update(d, self.get_user_id_token())

			trace("    app: (", " | ".join(f"{d['limit']} in {duration}s" for duration, d in app_limits_dict.items()), ")")

		if 'X-Method-Rate-Limit' in resp_headers:
			method_limits_arr = resp_headers['X-Method-Rate-Limit'].split(',')
			method_limits_dict = {}

			for ratio_str in method_limits_arr:
				colon_idx = ratio_str.index(':')

				max_calls = int(ratio_str[:colon_idx])
				duration = int(ratio_str[colon_idx+1:])

				d = {"limit": max_calls, "timestamps/"+self.firebase.database().generate_key():time}
				method_limits_dict[duration] = d
				result = self.get_timestamps('method').child(f"{req_type}/{duration}").update(d, self.get_user_id_token())

			trace(f'    method "{req_type}": (', " | ".join(f"{d['limit']} in {duration}s" for duration, d in method_limits_dict.items()), ")")


	def get_timestamps(self, timestamp_type:str = None):
		"""Get firebase child for timestamps."""
		assert timestamp_type in (None, 'method', 'app')
		return self.firebase.database().child(f"timestamps{'' if timestamp_type==None else f'/{timestamp_type}'}")
	
	def get_rate_limits(self, rate_limit_type:str = None):
		"""Get firebase child for rate_limits."""
		assert rate_limit_type in (None, 'method', 'app', 'service', 'service_expo')
		return self.firebase.database().child(f"rate_limits{'' if rate_limit_type==None else f'/{rate_limit_type}'}")

	def update_trace(self, new_trace):
		Requester.trace = new_trace

	def ddragon_request(self, req_type:str, **req_params_kargs):
		return requests.get(f"{DDRAGON_URL}{DDRAGON_DICT[req_type].prompt(**req_params_kargs)}").json()


class UrlBuilder:
	"""
	Stores a url, potentially with one or more {parameter_name}s in it.
	When prompted, fills the {parameter_name}s out.
	"""
	def __init__(self, url:str):
		self.url = url
		self.prompts = set()
		last_idx = 0
		for i in range(url.count("{")):
			open_idx, close_idx = url.find("{", last_idx), url.find("}", last_idx)
			self.prompts.add(url[open_idx+1:close_idx])
			last_idx = open_idx

	def prompt(self, **req_params_kargs):
		trace(f'Constructing URL "{self.url}"')
		for prompt in self.prompts:
			if prompt not in req_params_kargs:
				req_params_kargs[prompt] = input(f'    Enter "{prompt}": ')
		s = self.url.format(**req_params_kargs)
		return s

REQ_DICT = {
	"summoner_info": UrlBuilder("lol/summoner/v4/summoners/by-name/{summoner_name}"),
	"league_info": UrlBuilder("lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"),
	"champion_mastery": UrlBuilder("lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}"),
	"status": UrlBuilder("lol/status/v3/shard-data")
}

def _get_req_url(req_type:str, **req_params_kargs):
	assert req_type in REQ_DICT

	url = REQ_DICT[req_type].prompt(**req_params_kargs)

	trace(url)
	return url


DDRAGON_DICT = {
	"champions": UrlBuilder("data/en_US/champion.json"),
	"champion": UrlBuilder("data/en_US/champion/{champion}.json")
}


def get(trace:bool = False):# -> Requester
	if Requester.instance == None:
		print("CREATED NEW SINGLETON REQUESTER INSTANCE\n")
		Requester.instance = Requester()
	Requester.instance.update_trace(trace)
	return Requester.instance
