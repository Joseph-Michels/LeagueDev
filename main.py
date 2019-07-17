import riot_requester
from pprint import pprint

requester = riot_requester.get(trace=False)

SUMMONERS = ['jamerr102030', 'TsimpleT', 'Takaharu', 'Neo Star', 'Tzuyu Fanboy']

league_responses = []
for summoner in SUMMONERS:
	summoner_response = requester.request("summoner_info", summoner_name=summoner)
	league_responses.append(requester.request("league_info", encrypted_summoner_id=summoner_response['id']))

pprint(league_responses)