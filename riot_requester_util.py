import riot_requester
from ddragon_requester import request as ddragon_request
from datetime import datetime

requester = riot_requester.get(trace=False)
CHAMPION_KEYS = {int(champ_dict['key']):champ for champ,champ_dict in ddragon_request("champions")["data"].items()}

def get_champion(id:int) -> str:
	return CHAMPION_KEYS[id]
def get_ranks(league_info:dict):
	return (f"{l['queueType']}: {l['tier']} {l['rank']} ({l['wins']}-{l['losses']})" for l in league_info)


if __name__ == "__main__":	
	#SUMMONERS = ['jamerr102030', 'TsimpleT', 'Takaharu', 'Neo Star', 'Tzuyu Fanboy']
	SUMMONERS = ['TsimpleT']

	league_responses = []
	champion_mastery_responses = []
	matchlist_responses = []
	for summoner in SUMMONERS:
		summoner_response = requester.request("summoner_info", summoner_name=summoner)

		summoner_id_kargs = {'encrypted_summoner_id': summoner_response['id']}
		league_responses.append(requester.request("league_info", **summoner_id_kargs))
		champion_mastery_responses.append(requester.request("champion_mastery", **summoner_id_kargs))

		account_id_kargs = {'encrypted_account_id': summoner_response['accountId']}
		matchlist_responses.append(requester.request("matchlist", **account_id_kargs, beginIndex=0, endIndex=3))

	for i in range(len(SUMMONERS)):
		print(f'Information for "{SUMMONERS[i]}":')
		print("  Ranks:")
		print('\n'.join(f"    {rank}" for rank in get_ranks(league_responses[i])))
		print("  Champions")
		print('\n'.join(f"    {get_champion(info['championId'])} Level {info['championLevel']} ({info['championPoints']})" for info in champion_mastery_responses[i][:10]))
		print("  Matches")
		ml = matchlist_responses[i]
		print('\n'.join(f"    Played {get_champion(m['champion'])} in gameId {m['gameId']} on {datetime.fromtimestamp(int(m['timestamp'])/1000).strftime('%m-%d-%y %I:%M%p')}" for m in ml['matches']))