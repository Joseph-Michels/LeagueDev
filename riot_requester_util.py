import riot_requester
from ddragon_requester import request as ddragon_request

requester = riot_requester.get(trace=False)
CHAMPION_KEYS = {int(champ_dict['key']):champ for champ,champ_dict in ddragon_request("champions")["data"].items()}

def get_champion(id:int) -> str:
	return CHAMPION_KEYS[id]
def get_ranks(league_info:dict):
	return (f"{l['queueType']}: {l['tier']} {l['rank']} ({l['wins']}-{l['losses']})" for l in league_info)


if __name__ == "__main__":	
	#SUMMONERS = ['jamerr102030', 'TsimpleT', 'Takaharu', 'Neo Star', 'Tzuyu Fanboy']
	SUMMONERS = ['coIder']

	league_responses = []
	champion_mastery_responses = []
	for summoner in SUMMONERS:
		summoner_response = requester.request("summoner_info", summoner_name=summoner)

		summoner_id_kargs = {'encrypted_summoner_id': summoner_response['id']}
		league_responses.append(requester.request("league_info", **summoner_id_kargs))
		champion_mastery_responses.append(requester.request("champion_mastery", **summoner_id_kargs))

	for i in range(len(SUMMONERS)):
		print(f'Information for "{SUMMONERS[i]}":')
		print("  Ranks:")
		print('\n'.join(f"    {rank}" for rank in get_ranks(league_responses[i])))
		print("  Champions")
		print('\n'.join(f"    {get_champion(info['championId'])} Level {info['championLevel']} ({info['championPoints']})" for info in champion_mastery_responses[i][:10]))