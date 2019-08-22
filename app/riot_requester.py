import requests
import pyrebase
import time
get_time = time.time
from threading import Thread

from app.url_builder import UrlBuilder
from app.ddragon_requester import request as ddragon_request

'''
TODO:
UPDATE DOCUMENTATION
TEST SERVICE EXPO SOMEHOW
'''

class RiotRequester:
    """
    """

    REQ_HEADER = ""
    try:
        with open("credentials/riot.txt", 'r') as f:
            REQ_HEADER = {"X-Riot-Token":f.readline().rstrip()}
    except FileNotFoundError:
        raise FileNotFoundError('Missing firebase config in "credentials/firebase_config.txt"')

    URL = "api.riotgames.com"
    
    REQ_URL_BUILDER = {
		"summoner_info":	UrlBuilder("lol/summoner/v4/summoners/by-name/{summoner_name}"),
		"league_info":		UrlBuilder("lol/league/v4/entries/by-summoner/{encrypted_summoner_id}"),
		"champion_mastery":	UrlBuilder("lol/champion-mastery/v4/champion-masteries/by-summoner/{encrypted_summoner_id}"),
		"status":			UrlBuilder("lol/status/v3/shard-data"),
		"matchlist":		UrlBuilder("lol/match/v4/matchlists/by-account/{encrypted_account_id}",
								set(('champion', 'queue', 'season', 'endTime', 'beginTime', 'endIndex', 'beginIndex'))
							),
		"match":			UrlBuilder("lol/match/v4/matches/{match_id}"),
		"match_timeline":	UrlBuilder("lol/match/v4/timelines/by-match/{match_id}")
	}
    REGION_CODES = {
		"BR":'BR1',		"EUNE":'EUN1',	"EUW":'EUW1',	"JP":'JP1',
		"KR":'KR',		"LAN":'LA1',	"LAS":'LA2',	"NA":'NA1',
		"OCE":'OC1',	"TR":'TR1',		"RU":'RU',		"PBE":'PBE1'
	}

    def __init__(self, region:str, to_trace:bool=False):
        # initialize firebase
        try:
            with open("credentials/firebase_config.txt", 'r') as f:
                self.firebase = pyrebase.initialize_app(eval(f.read()))
        except FileNotFoundError:
            raise FileNotFoundError('Missing firebase config in "credentials/firebase_config.txt"')

        # initialize firebase user credentials
        self._user_init_time = get_time()
        try:
            with open("credentials/firebase_login.txt", 'r') as f:
                self._user = self.firebase.auth().sign_in_with_email_and_password(f.readline().rstrip(), f.readline().rstrip())
        except FileNotFoundError:
            raise FileNotFoundError('Missing firebase login in "credentials/firebase_login.txt"')

        # requesting + thread
        self._queued_requests = []
        self._thread = Thread(target=RiotRequester._request_queued, args=())
        self._responses = {}
        self._to_publish = {}

        # parameter initializations
        if region in RiotRequester.REGION_CODES.keys():
            region = RiotRequester.REGION_CODES[region]
        else:
            assert region in RiotRequester.REGION_CODES.values(), f'Region "{region}" not found.'
        self.region = region
        self.to_trace = to_trace

    
    def _raw_request(self, req_type:str, **req_params_kargs) -> requests.Response:
        assert req_type in RiotRequester.REQ_URL_BUILDER, f'Request Type "{req_type} undefined.'
        
        url_end = RiotRequester.REQ_URL_BUILDER[req_type].build(**req_params_kargs)
        
        msg = f'Requesting "{req_type}": "{url_end}"'
        self.trace('-'*len(msg))
        self.trace(msg)
        
        return requests.get(f"https://{self.region}.{RiotRequester.URL}/{url_end}", headers=RiotRequester.REQ_HEADER)

    
    def _request_queued(self):
        pass


    def synch_get_response(self, req_url:str):
        while True:
            if req_url in self._responses:
                return self._responses[req_url]
            time.sleep(3)

    
    def trace(self, *args, **kargs):
        """
		Takes an object or objects and prints it or them if the Requester is tracing.
		Calls pprint on iterables (for pretty print) and print on other objects.
		"""
        if self.to_trace:
            if len(kargs) == 0 and len(args) == 1 and type(args[0]) is not str:
                try:
                    iter(args[0])
                    pprint(args[0]) # pretty print iterables
                    return
                except:
                    pass
            print(*args, **kargs)

    
    def get_user(self) -> dict:
        if get_time() > self._user_init_time + float(self._user['expiresIn']):
            self._user_init_time = get_time()
            self._user = self.firebase.auth().refresh(self._user['refreshToken'])
        return self._user
    

    def get_user_id_token(self) -> str:
        return self.get_user()['idToken']


    def _queue_request(self, req_url:str):
        self._queued_requests += req_url


    def _get_req_url(self, req_type:str, **req_params_kargs):
        assert req_type in RiotRequester.REQ_URL_BUILDER, f'Request Type "{req_type} undefined.'
        return RiotRequester.REQ_URL_BUILDER[req_type].build(**req_params_kargs)


    def _store_timestamps(self, resp_headers:dict, req_type:str):
        """
        Stores timestamps of calls to the app and this method.
        """
        self.trace("  Adding Timestamps For Response")

        time = get_time()

        self.trace(f"    time: {time}")
        self.trace(f"    headers: {[key for key in resp_headers]}")

		# get rate limits in array of "max_calls:duration"
		# parses this array of strings
        if 'X-App-Rate-Limit' in resp_headers:
            app_limits_arr = resp_headers['X-App-Rate-Limit'].split(',')
            app_limits_dict = {}
            
            for ratio_str in app_limits_arr:
                colon_idx = ratio_str.index(':')
                
                max_calls = int(ratio_str[:colon_idx])
                duration = int(ratio_str[colon_idx+1:])
                
                app_limits_dict[duration] = max_calls

                base = f'timestamps/app/{duration}'
                self._to_publish[base+'/limit'] = max_calls
                self._to_publish[f'{base}/timestamps/{self.firebase.database().generate_key()}'] = time
                
            self.trace("    app: (", " | ".join(f"{limit} in {duration}s" for duration, limit in app_limits_dict.items()), ")")
        
        if 'X-Method-Rate-Limit' in resp_headers:
            method_limits_arr = resp_headers['X-Method-Rate-Limit'].split(',')
            method_limits_dict = {}
            
            for ratio_str in method_limits_arr:
                colon_idx = ratio_str.index(':')
                
                max_calls = int(ratio_str[:colon_idx])
                duration = int(ratio_str[colon_idx+1:])

                method_limits_dict[duration] = max_calls
                
                base = f'timestamps/method/{req_type}/{duration}'
                self._to_publish[base+'/limit'] = max_calls
                self._to_publish[f'{base}/timestamps/{self.firebase.database().generate_key()}'] = time
                
                
            self.trace(f'    method "{req_type}": (', " | ".join(f"{limit} in {duration}s" for duration, limit in method_limits_dict.items()), ")")

    
    def get_summoner_rundown(self, summoners:[str]):
        summoner_req_urls = []
        for summoner in summoners:
            url = self._get_req_url("summoner_info", summoner_name=summoner)
            summoner_req_urls.append(url)
            self._queue_request(url)

        summoner_responses = []
        for url in summoner_req_urls:
            summoner_responses.append(self.synch_get_response(url))