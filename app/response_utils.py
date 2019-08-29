from datetime import datetime
from collections import defaultdict
import game_constants as consts
from time import time as get_time

class MatchUtil:
	def __init__(self, match:dict, summoner_names:[str]):
		self.match = match
		self.names = summoner_names

	def result_summary(self):
		print(self.match['gameId'])

		partic_ids = [self.participant_id(name) for name in self.names]
		print(partic_ids)

		if any(p_id is not None for p_id in partic_ids):
			sides = {p_id:self.side(p_id) for p_id in partic_ids if p_id is not None}
			print(sides)
			_sides_arr = list(sides.values())
			print(_sides_arr)
			side = _sides_arr[0] if all(_sides_arr[i] == _sides_arr[i+1] for i in range(len(_sides_arr)-1)) else _get_greatest_frequency(_sides_arr)
			team_dict = self.team_dict(side)
			champs = {}

			return {
				"queue": consts.QUEUES(self.match['queueId']),
				"map": consts.MAPS(self.match['mapId']),
				"result": self.win_str(team_dict['win']),
				"length": self.match['gameDuration'],
				"timestamp": self.match['gameCreation'],
				"length_str": f"{self.match['gameDuration']//60}:{self.match['gameDuration']%60}",
				"get_timestamp_str": lambda : _get_time_since_str(self.match['gameCreation']//1000),
				"champions": [champs['top'], champs['jg'], champs['mid']]
			}	
			

	def participant_id(self, summoner:str):
		for participant_id_dict in self.match['participantIdentities']:
			if ''.join(s for s in participant_id_dict['player']['summonerName'].lower().split(' ')) == summoner.lower():
				return participant_id_dict['participantId']
	
	# 100 blue, 200 red
	def side(self, arg):
		idx = self.participant_id(arg) if type(arg) is str else arg
		for participant_dict in self.match['participants']:
			if participant_dict['participantId'] == idx:
				return participant_dict['teamId']

	def team_dict(self, side:int):
		for team_dict in self.match['teams']:
			if team_dict['teamId'] == side:
				return team_dict
	
	# past_tense: "Won"/"Lost"
	# not past_tense: "Win"/"Loss"
	def win_str(self, val:str, past_tense=False):
		return ("Lost" if val == "Fail" else "Won") if past_tense else ("Loss" if val == "Fail" else val)

	def player_match_stats(self, summoner:str):
		idx = self.participant_id(summoner)
		for participant_dict in self.match['participants']:
			if participant_dict['participantId'] == idx:
				return participant_dict['stats']

# input seconds
def _get_time_since_str(n:int):
	seconds = int(get_time()) - n
	
	n = seconds // 31536000
	if n > 1:
		return f"{n} years"
	else:
		n = seconds // 2592000
		if n > 1:
			return f"{n} months"
		else:
			n = seconds // 86400
			if n > 1:
				return f"{n} days"
			else:
				n = seconds // 3600
				if n > 1:
					return f"{n} hours"
				else:
					n = seconds // 60
					if n > 1:
						return f"{n} minutes"
					else:
						return f"{seconds} seconds"

def _get_greatest_frequency(arr:[]):
	d = defaultdict(int)
	max_key = arr[0]
	max_count = 1
	for e in arr:
		d[e] += 1
		if d[e] > max_count:
			max_key = e
			max_count = d[e]
	return max_key