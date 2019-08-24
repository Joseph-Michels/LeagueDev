from datetime import datetime

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