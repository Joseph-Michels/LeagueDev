from functools import wraps

from app.riot_requester import RiotRequester
from app.ddragon_requester import request as ddragon_request
from app.decarators import OneOfAKeyAtATime

TRACE = False
LOG = True
REGIONS = frozenset(['NA'])

CHAMPION_KEYS = {int(champ_dict['key']):champ for champ,champ_dict in ddragon_request("champions")["data"].items()}

def get_champion(id:int) -> str:
	return CHAMPION_KEYS[id]

REQUESTERS = {region:RiotRequester(region, TRACE, LOG) for region in REGIONS}

class UpdateRateLimitsTimestamps:
	"""
	Can only decorate functions with the region as the first argument.
	"""
	def __call__(self, fxn):
		@wraps(fxn)
		def wrapper_function(*args, **kargs):
			requester = REQUESTERS[args[0].upper()] # args[0] is region string

			requester.read_rate_limits()
			requester.read_timestamps()

			val = fxn(*args, **kargs)

			requester.write_rate_limits()
			requester.write_timestamps()
			
			return val
		return wrapper_function

@OneOfAKeyAtATime(key='Requester')
@UpdateRateLimitsTimestamps()
def safe_request(region:str, req_type:str, **req_params_kargs) -> dict:
	return REQUESTERS[region.upper()]._request(req_type, **req_params_kargs)

@OneOfAKeyAtATime(key='Requester')
@UpdateRateLimitsTimestamps()
def get_summoners_rundown(region:str, *summoners):
	if len(summoners) == 1 and type(summoners[0]) == list:
		summoners = summoners[0]
	request = REQUESTERS[region.upper()]._request
	
	responses = {summoner:{} for summoner in summoners}
	responses['matches'] = {}
	match_ids = set()
	for summoner in summoners:
		summoner_response = request("summoner_info", summoner_name=summoner)

		summoner_id_kargs = {'encrypted_summoner_id': summoner_response['id']}
		responses[summoner]['league'] = request("league_info", **summoner_id_kargs)
		responses[summoner]['champion_mastery'] = request("champion_mastery", **summoner_id_kargs)

		account_id_kargs = {'encrypted_account_id': summoner_response['accountId']}
		this_matchlist_response = request("matchlist", **account_id_kargs, beginIndex=0, endIndex=10)
		responses[summoner]['matchlist'] = this_matchlist_response
		for m in this_matchlist_response['matches']:
			match_ids.add(m['gameId'])

	for match_id in match_ids:
		responses['matches'][match_id] = request("match", match_id=match_id)

	return responses