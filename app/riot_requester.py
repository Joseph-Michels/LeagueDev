import requests
import pyrebase
import time
get_time = time.time
from functools import wraps
from pprint import pprint
from sys import stdout
from datetime import datetime

from app.url_builder import UrlBuilder
from app.ddragon_requester import request as ddragon_request

'''
TODO:
UPDATE DOCUMENTATION
TEST SERVICE EXPO SOMEHOW
'''

class OneAtATime:
    lock_dict = {}

    def __init__(self, key):
        self.key = key
        if key not in OneAtATime.lock_dict:
            self._unlock()
        
    def _unlock(self):
        OneAtATime.lock_dict[self.key] = False
    def _lock(self):
        OneAtATime.lock_dict[self.key] = True
    def is_locked(self):
        return OneAtATime.lock_dict[self.key]

    def __call__(self, fxn):
        @wraps(fxn)
        def wrapper_function(*args, **kargs):
            while True:
                if not self.is_locked():
                    self._lock()
                    val = fxn(*args, **kargs)
                    self._unlock()
                    return val
        return wrapper_function

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
		"matchlist":		UrlBuilder("lol/match/v4/matchlists/by-account/{encrypted_account_id}"),
		"match":			UrlBuilder("lol/match/v4/matches/{match_id}"),
		"match_timeline":	UrlBuilder("lol/match/v4/timelines/by-match/{match_id}")
	}
    REGION_CODES = {
		"BR":'BR1',		"EUNE":'EUN1',	"EUW":'EUW1',	"JP":'JP1',
		"KR":'KR',		"LAN":'LA1',	"LAS":'LA2',	"NA":'NA1',
		"OCE":'OC1',	"TR":'TR1',		"RU":'RU',		"PBE":'PBE1'
	}

    


    def __init__(self, region:str, trace:bool=False, log:bool=True):
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
        #self._queued_requests = []
        #self._thread = Thread(target=RiotRequester._request_queued, args=())
        #self._reserve_lock = Lock()
        #self._responses = {}
        #self._to_publish = {}

        # initialize region
        region = region.upper()
        if region in RiotRequester.REGION_CODES.keys():
            region = RiotRequester.REGION_CODES[region]
        else:
            assert region in RiotRequester.REGION_CODES.values(), f'Region "{region}" not found.'
        self.region = region

        # initialize debug tools
        self._to_trace = trace
        self._to_log = log
        if log:
            self._log_id = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')


    def _open_log_streams_dict(self):
        if not self._to_trace and not self._to_log:
            return None
        else:
            streams_dict = {'system':[], 'to_close':[]}
            if self._to_trace:
                streams_dict['system'].append(stdout)
            if self._to_log:
                streams_dict['to_close'].append(open(f'logs/log-{self._log_id}.txt', 'a'))
            return streams_dict
    def log(self, *args, **kargs):
        """
		Takes an object or objects and prints it or them if the Requester is tracing.
		Calls pprint on iterables (for pretty print) and print on other objects.
		"""
        streams_dict = self._open_log_streams_dict()

        if streams_dict is not None:
            streams = [stream for arr in streams_dict.values() for stream in arr]
            if len(kargs) == 0 and len(args) == 1 and type(args[0]) is not str:
                # if iterable, pprint the iterable that is the first/only arg
                try:
                    iter(args[0])
                    for stream in streams:
                        pprint(args[0], stream=stream)
                    return
                except:
                    pass
            # otherwise regular print
            for stream in streams:
                print(*args, **kargs, file=stream)
        
        # close applicable streams
        for stream in streams_dict['to_close']:
            stream.close()
        
    
    def _request(self, req_type:str, **req_params_kargs) -> dict:
        assert req_type in RiotRequester.REQ_URL_BUILDER, f'Request Type "{req_type} undefined.'
        url_end = RiotRequester.REQ_URL_BUILDER[req_type].build(**req_params_kargs)
        
        self.log(f'Requesting "{req_type}": "{url_end}"')
        '''
        self._remove_old_timestamps(req_type)
        if self._can_request(req_type):
            response = self._get_handle_response(req_type, **req_params_kargs)
            if response is not None:
                self._add_timestamps(response.headers, req_type)
                return response.json()
        else:
            print(f'Cannot request "{req_type}" due to rate limits.')
        '''

        return requests.get(f"https://{self.region}.{RiotRequester.URL}/{url_end}", headers=RiotRequester.REQ_HEADER)

    def _get_timestamps(self):
        pass


    @OneAtATime(key='RiotRequester')
    def safe_request(self, req_type:str, **req_params_kargs) -> requests.Response:
        return self._request(req_type, **req_params_kargs)
    
    
    def get_user(self) -> dict:
        if get_time() > self._user_init_time + float(self._user['expiresIn']):
            self._user_init_time = get_time()
            self._user = self.firebase.auth().refresh(self._user['refreshToken'])
        return self._user
    def get_user_id_token(self) -> str:
        return self.get_user()['idToken']


    def _get_req_url(self, req_type:str, **req_params_kargs):
        assert req_type in RiotRequester.REQ_URL_BUILDER, f'Request Type "{req_type} undefined.'
        return RiotRequester.REQ_URL_BUILDER[req_type].build(**req_params_kargs)


    @OneAtATime(key='RiotRequester')
    def get_summoners_rundown(self, *summoners):
        if len(summoners) == 1 and type(summoners[0]) == list:
            summoners = summoners[0]
        
        summoner_responses = [self._request("summoner_info", summoner_name=summoner) for summoner in summoners]

        time.sleep(5)
        return summoner_responses