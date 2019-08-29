from functools import wraps

from app.riot_requester import RiotRequester
from app.ddragon_requester import request as ddragon_request
from app.decarators import OneOfAKeyAtATime
from app.response_utils import MatchUtil

TRACE = False
LOG = True
REGIONS = frozenset(['NA', 'EUW', 'KR'])

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

def insert_descending(element, arr:list):
	if len(arr) == 0:
		arr.append(element)
	else:
		start, end = -1, len(arr)
		mid = (start+end)//2
		while end-start > 1:
			mid_elem = arr[mid]
			if mid_elem > element:
				start = mid
			elif mid_elem < element:
				end = mid
			else:
				return # no duplicates
			mid = (start+end)//2

		if mid==-1 or end-start==1 and element<arr[mid]:
			arr.insert(mid+1, element)
		else:
			arr.insert(mid, element)
			

@OneOfAKeyAtATime(key='Requester')
@UpdateRateLimitsTimestamps()
def safe_request(region:str, req_type:str, **req_params_kargs) -> dict:
	return REQUESTERS[region.upper()]._request(req_type, **req_params_kargs)

@OneOfAKeyAtATime(key='Requester')
@UpdateRateLimitsTimestamps()
def get_summoners_rundown(region:str, *summoner_names):
	if len(summoner_names) == 1 and type(summoner_names[0]) == list:
		summoner_names = summoner_names[0]

	request = REQUESTERS[region.upper()]._request
	
	
	summoners = {name:{} for name in summoner_names}
	match_ids = []
	for summoner in summoners:
		summoner_response = request("summoner_info", summoner_name=summoner)

		summoner_id_kargs = {'encrypted_summoner_id': summoner_response['id']}
		summoners[summoner]['ranks'] = request("league_info", **summoner_id_kargs)
		summoners[summoner]['champion_mastery'] = request("champion_mastery", **summoner_id_kargs)

		account_id_kargs = {'encrypted_account_id': summoner_response['accountId']}
		this_matchlist_response = request("matchlist", **account_id_kargs, beginIndex=0, endIndex=10)
		summoners[summoner]['matchlist'] = this_matchlist_response
		for m in this_matchlist_response['matches']:
			insert_descending(m['gameId'], match_ids)
	
	for i in range(len(match_ids)-1):
		assert match_ids[i] > match_ids[i+1], f"Match IDs not descending at i = {i}"
	
	matches = [MatchUtil(request("match", match_id=match_id), summoner_names) for match_id in match_ids]
	REQUESTERS['NA'].log(matches[0].match)

	return {"summoners":summoners, "matches":matches}
