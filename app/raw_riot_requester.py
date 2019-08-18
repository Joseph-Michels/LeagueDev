import requests

from collections import OrderedDict
from pprint import pprint

from app.url_builder import UrlBuilder

'''
TODO:
UPDATE DOCUMENTATION
TEST SERVICE EXPO SOMEHOW
'''

class RawRiotRequester:
	HEADER = ""
	try:
		with open("keys/riot.txt", 'r') as f:
			HEADER = {"X-Riot-Token":f.readline().rstrip()}
	except FileNotFoundError:
		raise FileNotFoundError('Missing firebase config in "credentials/firebase_config.txt"')

	URL = "api.riotgames.com"

	REQ_URLS = {
		"summoner_info":	UrlBuilder("lol/summoner/v4/summoners/by-name/{summoner_name}"),
		"league_info":		UrlBuilder("lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"),
		"champion_mastery":	UrlBuilder("lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}"),
		"status":			UrlBuilder("lol/status/v3/shard-data"),
		"matchlist":		UrlBuilder("lol/match/v4/matchlists/by-account/{encrypted_account_id}",
								set(('champion', 'queue', 'season', 'endTime', 'beginTime', 'endIndex', 'beginIndex'))
							),
		"match":			UrlBuilder("lol/match/v4/matches/{match_id}"),
		"match_timeline":	UrlBuilder("lol/match/v4/timelines/by-match/{match_id}")
	}

	REGION_CODES = {
		"BR":'BR1',		"EUNE":'EUN1',	"EUW":'EUW1',	"JP":'JP1',
		"KR":'KR',		"LAN":'LA1',	"LAS":'LA2',	"NA":'NA1',
		"OCE":'OC1',	"TR":'TR1',		"RU":'RU',		"PBE":'PBE1'
	}

	def __init__(self, region:str, to_trace:bool=False):
		region = region.upper()

		if region in RawRiotRequester.REGION_CODES.keys():
			region = RawRiotRequester.REGION_CODES[region]
		else:
			assert region in RawRiotRequester.REGION_CODES.values(), f'Region "{region}" not found.'

		self.region = region
		self.to_trace = to_trace
	

	def trace(self, *args, **kargs):
		"""
		Takes an object or objects and prints it or them if the Requester is tracing.
		Calls pprint on iterables (for pretty print) and print on other objects.
		"""
		if self.to_trace:
			if len(kargs) == 0 and len(args) == 1 and type(args[0]) is not str:
				try:
					iter(args[0])
					pprint(args[0]) # pretty print iterables
					return
				except:
					pass
			print(*args, **kargs)


	def request(self, req_type:str, **req_params_kargs) -> requests.Response:
		assert req_type in RawRiotRequester.REQ_URLS, f'Request Type "{req_type} undefined.'

		url_end = RawRiotRequester.REQ_URLS[req_type].build(**req_params_kargs)

		msg = f'Requesting "{req_type}": "{url_end}"'
		self.trace('-'*len(msg))
		self.trace(msg)

		return requests.get(f"https://{self.region}.{RawRiotRequester.URL}/{url_end}", headers=RawRiotRequester.HEADER)


	def update_trace(self, new_trace):
		self.to_trace = new_trace