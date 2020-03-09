from datetime import datetime
from collections import defaultdict
import game_constants as consts
from time import time as get_time
from app.ddragon_requester import get_champion

class MatchUtil:
	def __init__(self, match:dict, summoner_names:[str]):
		# self.match = match
		# self.names = summoner_names

		self.gameId = match['gameId']
		self.queue = consts.QUEUES(match['queueId'])
		self.map = consts.MAPS(match['mapId'])
		self.link = f"https://matchhistory.na.leagueoflegends.com/en/#match-details/{match['platformId']}/{self.gameId}]"
		self.duration = match['gameDuration']
		self.duration_str = (f"{self.duration//3600}:" if self.duration > 3600 else "") + f"{self.duration//60}:{self.duration%60}"
		self.timestamp = match['gameCreation']

		print(f"Generating result summary for gameId: {self.gameId}")
		print(f"  queue: {self.queue}, map: {self.map}")

		self.searched_participant_ids = [MatchUtil.participant_id(name, match) for name in summoner_names]
		print(f"  searched_partic_ids in this game: {self.searched_participant_ids}")

		assert any(p_id is not None for p_id in self.searched_participant_ids), f"No searched summoners in gameId {self.gameId}"

		sides_dict = {p_id:MatchUtil.get_side(p_id, match) for p_id in self.searched_participant_ids if p_id is not None}
		print(f"  sides_dict: {sides_dict}")
		sides_arr = list(sides_dict.values())
		print(f"  sides_arr: {sides_arr}")
		self.side = sides_arr[0] if all(sides_arr[i] == sides_arr[i+1] for i in range(len(sides_arr)-1)) else MatchUtil._get_greatest_frequency(sides_arr)
		team_dict = MatchUtil.team_dict(self.side, match)

		self.result = MatchUtil.win_str(team_dict['win'])

		partic_dict = MatchUtil.participants_dict(self.side, match)
		print(f"  partic_dict keys: {partic_dict.keys()}")

		self.participants = partic_dict


	def get_timestamp_str(self):
		seconds = int(get_time()) - self.timestamp//1000

		n = seconds // 31536000
		if n >= 1:
			return f"{n} year" + ('s' if n > 1 else '')
		else:
			n = seconds // 2592000
			if n >= 1:
				return f"{n} month" + ('s' if n > 1 else '')
			else:
				n = seconds // 86400
				if n >= 1:
					return f"{n} day" + ('s' if n > 1 else '')
				else:
					n = seconds // 3600
					if n >= 1:
						return f"{n} hour" + ('s' if n > 1 else '')
					else:
						n = seconds // 60
						if n >= 1:
							return f"{n} minute" + ('s' if n > 1 else '')
						else:
							return f"{seconds} second" + ('s' if seconds > 1 else '')

	@staticmethod
	def summoners_match(summ1, summ2):
		return MatchUtil.simple_summoner_name(summ1) == MatchUtil.simple_summoner_name(summ2)

	@staticmethod
	def simple_summoner_name(summoner:str):
		return ''.join(s for s in summoner.lower().split(' '))

	@staticmethod
	def participant_id(summoner:str, match:{}):
		for participant_id_dict in match['participantIdentities']:
			if MatchUtil.summoners_match(participant_id_dict['player']['summonerName'], summoner):
				return participant_id_dict['participantId']

	# 100 blue, 200 red
	@staticmethod
	def get_side(summoner_or_partic_id, match:{}):
		idx = MatchUtil.participant_id(summoner_or_partic_id, match) if type(summoner_or_partic_id) is str else summoner_or_partic_id
		for participant_dict in match['participants']:
			if participant_dict['participantId'] == idx:
				return participant_dict['teamId']

	@staticmethod
	def team_dict(side:int, match:{}):
		for team_dict in match['teams']:
			if team_dict['teamId'] == side:
				return team_dict

	@staticmethod
	def participants_dict(side:int, match:{}):
		d = {}
		repeated_participants = []
		print(f"compiling partic_dict for {side}")
		for partic in match['participants']:
			if partic['teamId'] == side:
				print(partic['timeline']['lane'], partic['timeline']['role'])
				role = MatchUtil.get_raw_role(partic)
				if role not in d:
					d[role] = partic
				else:
					repeated_participants.append(partic)
		# TODO: correct to actual roles
		remaining_roles = [role for role in MatchUtil._ROLES if role not in d]
		while len(repeated_participants) > 0:
			d[remaining_roles.pop()] = repeated_participants.pop()
		return d

	_ROLES = ['TOP', 'JG', 'MID', 'BOT', 'SUP']
	_ROLE_DICT = {
		'JUNGLE': 'JG',
		'MIDDLE': 'MID',
		'DUO_CARRY': 'BOT',
		'DUO_SUPPORT': 'SUP',
		'SOLO': 'BOT', # cheesey solution for BOT/SOLO
		'TOP': 'TOP',
		'DUO': 'BOT'
	}
	@staticmethod
	def get_raw_role(partic:{}):
		lane = partic['timeline']['lane']
		return MatchUtil._ROLE_DICT[lane if lane in MatchUtil._ROLE_DICT else partic['timeline']['role']]

	# past_tense: "Won"/"Lost"
	# not past_tense: "Win"/"Loss"
	@staticmethod
	def win_str(val:str, past_tense=False):
		return ("Lost" if val == "Fail" else "Won") if past_tense else ("Loss" if val == "Fail" else val)

	# def player_match_stats(self, summoner:str):
	# 	idx = self.participant_id(summoner)
	# 	for participant_dict in self.match['participants']:
	# 		if participant_dict['participantId'] == idx:
	# 			return participant_dict['stats']

	@staticmethod
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