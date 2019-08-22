'''
TODO: make it actual util
these tests moved to html
'''
from app import riot_requester
from app.ddragon_requester import request as ddragon_request
from datetime import datetime

requester = riot_requester.get(trace=True, email='bobelement4181@gmail.com', password='testtest')
CHAMPION_KEYS = {int(champ_dict['key']):champ for champ,champ_dict in ddragon_request("champions")["data"].items()}

def get_champion(id:int) -> str:
	return CHAMPION_KEYS[id]
def get_ranks(league_info:dict):
	return (f"{l['queueType']}: {l['tier']} {l['rank']} ({l['wins']}-{l['losses']})" for l in league_info)

def participant_id(summoner:str, match:dict):
	for participant_id_dict in match['participantIdentities']:
		if participant_id_dict['player']['summonerName'] == summoner:
			return participant_id_dict['participantId']

# 100 blue, 200 red
def side(summoner:str, match:dict):
	idx = participant_id(summoner, match)
	for participant_dict in match['participants']:
		if participant_dict['participantId'] == idx:
			return participant_dict['teamId']

# past_tense: "Won"/"Lost"
# not past_tense: "Win"/"Loss"
def match_result(summoner:str, match:dict, past_tense=False):
	s = side(summoner, match)
	for team_dict in match['teams']:
		if team_dict['teamId'] == s:
			val = team_dict['win']
			return ("Lost" if val == "Fail" else "Won") if past_tense else ("Loss" if val == "Fail" else val)

def player_match_score(summoner:str, match:dict):
	idx = participant_id(summoner, match)
	for participant_dict in match['participants']:
		if participant_dict['participantId'] == idx:
			d = participant_dict['stats']
			return f"{d['kills']}/{d['deaths']}/{d['assists']}"


def summary():
	s = ""

	SUMMONERS = ['jamerr102030', 'TsimpleT', 'SuperFranky', 'JDG Yagao', 'Takaharu', 'A Little Cat']
	# SUMMONERS = ['TsimpleT']

	league_responses = []
	champion_mastery_responses = []
	matchlist_responses = []
	match_ids = set()
	for summoner in SUMMONERS:
		summoner_response = requester.request("summoner_info", summoner_name=summoner)

		summoner_id_kargs = {'encrypted_summoner_id': summoner_response['id']}
		league_responses.append(requester.request("league_info", **summoner_id_kargs))
		champion_mastery_responses.append(requester.request("champion_mastery", **summoner_id_kargs))

		account_id_kargs = {'encrypted_account_id': summoner_response['accountId']}
		this_matchlist_response = requester.request("matchlist", **account_id_kargs, beginIndex=0, endIndex=5)
		matchlist_responses.append(this_matchlist_response)
		for m in this_matchlist_response['matches']:
			match_ids.add(m['gameId'])

	matches = {}
	for match_id in match_ids:
		matches[match_id] = requester.request("match", match_id=match_id)

	for i in range(len(SUMMONERS)):
		summ = SUMMONERS[i]
		s += (f'Information for "{summ}":') + '\n'
		s += ("    Ranks:") + '\n'
		s += ('\n'.join(f"        {rank}" for rank in get_ranks(league_responses[i]))) + '\n'
		s += ("    Champions")
		s += ('\n'.join(f"        {get_champion(info['championId'])} Level {info['championLevel']} ({info['championPoints']})" for info in champion_mastery_responses[i][:10]))
		s += ("    Recent Matches")
		s += ('\n'.join(
			f"        {match_result(summ, matches[m['gameId']], past_tense=True)} a {get_champion(m['champion'])} game #{m['gameId']} with a score of {player_match_score(summ, matches[m['gameId']])} on {datetime.fromtimestamp(int(m['timestamp'])/1000).strftime('%m-%d-%y %I:%M%p')}" for m in matchlist_responses[i]['matches']
			))

	return s