'''
import requests
from Requester import Requester
from pathlib import Path
from firebase import firebase

SUMMONERS = ["jamerr102030", "tsimplet", "superfranky", "capengyuyan", "frosthook"]

p = Path()

print([o.name for o in p.iterdir()])


requester = Requester()

ids = []
responses = []

for summoner in SUMMONERS:
	resp = requester.request("summoner/v4/summoners/by-name/" + summoner)
	if resp is not None:
		responses.append(resp)

print(ids)

for rq in responses:
	print(rq.status_code)
'''