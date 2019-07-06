import riot_requester

requester = riot_requester.get(trace=True)

resp = requester.request("summoner_info")
print(resp)