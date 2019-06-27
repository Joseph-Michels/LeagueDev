import riot_requester

requester = riot_requester.get(trace=True)

resp = requester.request("summoner/v4/summoners/by-name/tsimplet")
print(resp)