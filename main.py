import riot_requester
from pprint import pprint

requester = riot_requester.get(trace=False)

SUMMONERS = ['jamerr102030', 'TsimpleT', 'Takaharu', 'Neo Star', 'Tzuyu Fanboy']

league_responses = []
champion_mastery_responses = []
for summoner in SUMMONERS:
	summoner_response = requester.request("summoner_info", summoner_name=summoner)

	summoner_id_kargs = {'encrypted_summoner_id': summoner_response['id']}
	league_responses.append(requester.request("league_info", **summoner_id_kargs))
	champion_mastery_responses.append(requester.request("champion_mastery", **summoner_id_kargs))

pprint(league_responses)
#pprint(champion_mastery_responses)