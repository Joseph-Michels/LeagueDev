import requests
import pyrebase
import time
import json
get_time = time.time
from pprint import pprint
from sys import stdout
from datetime import datetime

from app.url_builder import UrlBuilder
from app.decarators import OneOfAKeyAtATime

'''
TODO:
UPDATE DOCUMENTATION
TEST SERVICE EXPO SOMEHOW
'''


class RiotRequester:
	"""
	"""
	REQ_HEADER = ""
	try:
		with open("credentials/riot.txt", 'r') as f:
			REQ_HEADER = {"X-Riot-Token":f.readline().rstrip()}
	except FileNotFoundError:
		raise FileNotFoundError('Missing firebase config in "credentials/firebase_config.txt"')

	URL = "api.riotgames.com"
	REQ_URL_BUILDER = {
		"summoner_info":	UrlBuilder("lol/summoner/v4/summoners/by-name/{summoner_name}"),
		"league_info":		UrlBuilder("lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"),
		"champion_mastery":	UrlBuilder("lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}"),
		"status":			UrlBuilder("lol/status/v3/shard-data"),
		"matchlist":		UrlBuilder("lol/match/v4/matchlists/by-account/{encrypted_account_id}"),
		"match":			UrlBuilder("lol/match/v4/matches/{match_id}"),
		"match_timeline":	UrlBuilder("lol/match/v4/timelines/by-match/{match_id}")
	}
	REGION_CODES = {
		"BR":'BR1',		"EUNE":'EUN1',	"EUW":'EUW1',	"JP":'JP1',
		"KR":'KR',		"LAN":'LA1',	"LAS":'LA2',	"NA":'NA1',
		"OCE":'OC1',	"TR":'TR1',		"RU":'RU',		"PBE":'PBE1'
	}



	def __init__(self, region:str, trace:bool=False, log:bool=True):
		'''initialize debug tools'''
		self._to_trace = trace
		self._to_log = log
		if log:
			self._log_id = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

		'''initialize firebase'''
		try:
			with open("credentials/firebase_config.txt", 'r') as f:
				self.firebase = pyrebase.initialize_app(eval(f.read()))
		except FileNotFoundError:
			raise FileNotFoundError('Missing firebase config in "credentials/firebase_config.txt"')

		'''initialize firebase user credentials'''
		self._user_init_time = get_time()
		try:
			with open("credentials/firebase_login.txt", 'r') as f:
				self._user = self.firebase.auth().sign_in_with_email_and_password(f.readline().rstrip(), f.readline().rstrip())
		except FileNotFoundError:
			raise FileNotFoundError('Missing firebase login in "credentials/firebase_login.txt"')

		'''initialize rate limits / timestamps'''
		self.read_rate_limits() # in self._rate_limits
		self.read_timestamps() # in self._timestamps

		'''initialize region'''
		region = region.upper()
		if region in RiotRequester.REGION_CODES.keys():
			region = RiotRequester.REGION_CODES[region]
		else:
			assert region in RiotRequester.REGION_CODES.values(), f'Region "{region}" not found.'
		self.region = region



	'''
	=================================================
	LOGGING METHODS
	=================================================
	'''
	def _open_log_streams_dict(self):
		if not self._to_trace and not self._to_log:
			return None
		else:
			streams_dict = {'system':[], 'to_close':[]}
			if self._to_trace:
				streams_dict['system'].append(stdout)
			if self._to_log:
				streams_dict['to_close'].append(open(f'logs/log-{self._log_id}.txt', 'a'))
			return streams_dict
	def log(self, *args, **kargs):
		"""
		Takes an object or objects and prints it or them if the Requester is tracing.
		Calls pprint on iterables (for pretty print) and print on other objects.
		"""
		streams_dict = self._open_log_streams_dict()

		if streams_dict is not None:
			streams = [stream for arr in streams_dict.values() for stream in arr]
			if len(kargs) == 0 and len(args) == 1 and type(args[0]) is not str:
				# if iterable, pprint the iterable that is the first/only arg
				try:
					iter(args[0])
					for stream in streams:
						pprint(args[0], stream=stream)
					return
				except:
					pass
			# otherwise regular print
			for stream in streams:
				print(*args, **kargs, file=stream)
		
		# close streams that need to be closed
		for stream in streams_dict['to_close']:
			stream.close()
		

	
	'''
	==================================================
	GENERAL REQUESTING METHODS
	==================================================
	'''
	def _request(self, req_type:str, **req_params_kargs) -> dict:
		"""
		Requests information from the Riot Games API. Checks and updates rate limits.
		Returns None if cannot request.
		"""
		assert req_type in RiotRequester.REQ_URL_BUILDER, f'Request Type "{req_type} undefined.'
		url_end = RiotRequester.REQ_URL_BUILDER[req_type].build(**req_params_kargs)
		
		self.log(f'Requesting "{url_end}"')

		while True:
			self._remove_old_timestamps(req_type)
			pre_delay = self._delay_before_request(req_type)
			if pre_delay == 0:
				response = self._get_handled_response(req_type, url_end)
				if response is not None:
					self._add_timestamps(response.headers, req_type)
					return response.json()
			else:
				self.log(f"  Waiting {pre_delay} seconds.")
				time.sleep(pre_delay)



	def _remove_old_timestamps(self, req_type:str):
		"""
		Removes old timestamps.
		"""
		time = get_time()

		# Remove old timestamps for calls to the app
		app_data = self.get_timestamps('app')
		if app_data is not None:
			for duration, limit_timestamp_dict in app_data.items():
				if 'timestamps' in limit_timestamp_dict:
					# remove expired timestamps from beginning until a still applicable one is reached
					# works because newer timestamps are added to the end
					while len(limit_timestamp_dict['timestamps']) > 0:
						if time > limit_timestamp_dict['timestamps'][0] + int(duration):
							limit_timestamp_dict['timestamps'].pop(0)
						else:
							break

		# Remove old timestamps for calls to this method
		method_data = self.get_timestamps(f'method/{req_type}')
		if method_data is not None:
			for duration, limit_timestamp_dict in method_data.items():
				if 'timestamps' in limit_timestamp_dict:
					# remove expired timestamps from beginning until a still applicable one is reached
					# works because newer timestamps are added to the end
					while len(limit_timestamp_dict['timestamps']) > 0:
						if time > limit_timestamp_dict['timestamps'][0] + int(duration):
							limit_timestamp_dict['timestamps'].pop(0)
						else:
							break



	def _delay_before_request(self, req_type:str) -> float:
		'''check rate_limits next_try timestamps'''
		time = get_time()
		
		app_next_try_timestamp = self.get_rate_limits('app')
		if app_next_try_timestamp is not None:
			if time > app_next_try_timestamp: # passed retry after mark, remove rate_limit
				self.get_rate_limits().pop('app')
			else:
				return app_next_try_timestamp-time

		method_next_try_timestamp = self.get_rate_limits(f'method/{req_type}')
		if method_next_try_timestamp is not None:
			if time > method_next_try_timestamp: # passed retry after mark, remove rate_limit
				self.get_rate_limits('method').pop(req_type)
			else:
				return method_next_try_timestamp-time

		service_next_try_timestamp = self.get_rate_limits('service')
		if service_next_try_timestamp is not None:
			if time > service_next_try_timestamp: # passed retry after mark, remove rate_limit
				self.get_rate_limits().pop('service')
			else:
				return service_next_try_timestamp-time

		service_expo_dict = self.get_rate_limits('service_expo')
		if service_expo_dict is not None:
			if time <= service_expo_dict['next_try_timestamp']: # service_expo needs to be kept to potentially try again
				return service_expo_dict['next_try_timestamp']-time

		'''check number of previous calls'''
		app_timestamps = self.get_timestamps('app')
		if app_timestamps is not None:
			for duration, limit_timestamp_dict in app_timestamps.items():
				if 'timestamps' in limit_timestamp_dict and len(limit_timestamp_dict['timestamps']) >= int(limit_timestamp_dict['limit']):
					self.log(f"  App: Called {len(limit_timestamp_dict['timestamps'])} of Limit {limit_timestamp_dict['limit']} in {duration}s")
					return limit_timestamp_dict['timestamps'][0]+int(duration)-time

		method_timestamps = self.get_timestamps(f'method/{req_type}')
		if method_timestamps is not None:
			for duration, limit_timestamp_dict in method_timestamps.items():
				if 'timestamps' in limit_timestamp_dict and len(limit_timestamp_dict['timestamps']) >= int(limit_timestamp_dict['limit']):
					self.log(f"  Method: Called {len(limit_timestamp_dict['timestamps'])} of Limit {limit_timestamp_dict['limit']} in {duration}s")
					return limit_timestamp_dict['timestamps'][0]+int(duration)-time
				
		return 0

	

	def _get_handled_response(self, req_type:str, url_end:str) -> requests.Response:
		"""
		Uses the requests api to make the request. Handles rate limits and adds
		retry_after messages.
		"""
		response = requests.get(f"https://{self.region}.{RiotRequester.URL}/{url_end}", headers=RiotRequester.REQ_HEADER)

		if response.status_code == 200: # return if ok (200)
			# remove all service_expo rate_limits after success
			if 'service_expo' in self._rate_limits:
				self._rate_limits.pop('service_expo')
			return response
		elif response.status_code == 429: # got rate limited, add retry_after
			time = get_time()
			if 'X-Rate-Limit-Type' in response.headers:
				retry_after = response.headers['Retry-After']
				next_try_timestamp = float(retry_after) + time
				rate_limit_type = response.headers['X-Rate-Limit-Type']
				self.log(f"  EXCEEDED RATE LIMIT: {rate_limit_type}, retry after {retry_after}s")

				if rate_limit_type == 'application':
					d = self.get_rate_limits('app')
					self._rate_limits['app'] = next_try_timestamp if d is None else max(d, next_try_timestamp)					
				elif rate_limit_type == 'method':
					d = self.get_rate_limits(f'method/{req_type}')
					if d is None:
						if 'method' not in self._rate_limits:
							self._rate_limits['method'] = {}
					self._rate_limits['method'][req_type] = next_try_timestamp if d is None else max(d, next_try_timestamp)	
				elif rate_limit_type == 'service':
					d = self.get_rate_limits('service')
					self._rate_limits['service'] = next_try_timestamp if d is None else max(d, next_try_timestamp)
				else:
					raise ValueError(f"Unexpected rate_limit_type {rate_limit_type}")
			else:
				self.log("  EXCEEDED RATE LIMIT: back off exponentially until we receive a 200 response")
				INITIAL_RETRY_AFTER = 1
				prev_rate_limit = self.get_rate_limits('service_expo')
				if prev_rate_limit is None:
					self._rate_limits['service_expo'] = {'retry_after':INITIAL_RETRY_AFTER, 'next_try_timestamp':time+INITIAL_RETRY_AFTER}
				else:
					self.log(f"    previous rate limit: {prev_rate_limit}")
					new_retry_after = 2*prev_rate_limit['retry_after']
					self._rate_limits['service_expo'] = {
						'retry_after': new_retry_after,
						'next_try_timestamp': time+new_retry_after
					}

			return None
		else:
			raise ValueError(f"Request failed with unexpected response code {response.status_code}")



	def _add_timestamps(self, resp_headers:dict, req_type:str):
		"""
		Add timestamps of calls to the app and this method.
		"""
		# self.log("  Adding Timestamps For Response")

		time = get_time()

		# self.log(f"    time: {time}")
		# self.log(f"    headers: {[key for key in resp_headers]}")

		# get rate limits in array of "max_calls:duration"
		# parses this array of strings
		if 'X-App-Rate-Limit' in resp_headers:
			for ratio_str in resp_headers['X-App-Rate-Limit'].split(','):
				colon_idx = ratio_str.index(':')

				max_calls = ratio_str[:colon_idx]
				duration = ratio_str[colon_idx+1:]

				if 'app' not in self._timestamps:
					self.log("app reset app")
					self._timestamps['app'] = {}
				if duration not in self._timestamps['app']:
					self.log("app reset timestamps")
					self._timestamps['app'][duration] = {'timestamps':[]}
				
				self._timestamps['app'][duration]['limit'] = max_calls
				self._timestamps['app'][duration]['timestamps'].append(time)

		if 'X-Method-Rate-Limit' in resp_headers:
			for ratio_str in resp_headers['X-Method-Rate-Limit'].split(','):
				colon_idx = ratio_str.index(':')

				max_calls = ratio_str[:colon_idx]
				duration = ratio_str[colon_idx+1:]

				if 'method' not in self._timestamps:
					self.log("method reset method")
					self._timestamps['method'] = {}
				if req_type not in self._timestamps['method']:
					self.log(f"method reset {req_type}")
					self._timestamps['method'][req_type] = {}
				if duration not in self._timestamps['method'][req_type]:
					self.log("method reset timestamps")
					self._timestamps['method'][req_type][duration] = {'timestamps':[]}
				
				self._timestamps['method'][req_type][duration]['limit'] = max_calls
				self._timestamps['method'][req_type][duration]['timestamps'].append(time)



	def read_rate_limits(self):
		with open('app/docs/rate_limits.json', 'r') as f:
			self._rate_limits = eval(f.read())

	def write_rate_limits(self):
		with open('app/docs/rate_limits.json', 'w') as f:
			json.dump(self._rate_limits, f, indent=4)

	def get_rate_limits(self, addr:str='') -> dict:
		arr = [] if addr=='' else addr.split('/')
		d = self._rate_limits
		while len(arr) > 0:
			next_item = arr.pop(0)
			if type(d) is dict and next_item in d:
				d = d[next_item]
			else:
				return None
		return d


	def read_timestamps(self):
		with open('app/docs/timestamps.json', 'r') as f:
			self._timestamps = eval(f.read())

	def write_timestamps(self):
		with open('app/docs/timestamps.json', 'w') as f:
			json.dump(self._timestamps, f, indent=4)

	def get_timestamps(self, addr:str) -> dict:
		arr = [] if addr=='' else addr.split('/')
		d = self._timestamps
		while len(arr) > 0:
			next_item = arr.pop(0)
			if type(d) is dict and next_item in d:
				d = d[next_item]
			else:
				return None
		return d

	
	'''
	==================================================
	FIREBASE METHODS
	==================================================
	'''
	def get_user(self) -> dict:
		if get_time() > self._user_init_time + float(self._user['expiresIn']):
			self._user_init_time = get_time()
			self._user = self.firebase.auth().refresh(self._user['refreshToken'])
		return self._user
	def get_user_id_token(self) -> str:
		return self.get_user()['idToken']
