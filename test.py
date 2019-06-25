import requests
from Requester import Requester
from pathlib import Path

SUMMONERS = ["Jible", "blackcat1", "SirMcDerpington", "Shinsei", "who dis fool"]

p = Path()

print([o.name for o in p.iterdir()])


requester = Requester()


ids = []
responses = []

for summoner in SUMMONERS:
	resp = requester.request("summoner/v4/summoners/by-name/" + summoner)
	if resp.status_code == 200:
		responses.append(resp)

print(ids)

for rq in responses:
	print(rq.status_code)
