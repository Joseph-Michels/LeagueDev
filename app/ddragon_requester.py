import requests
from app.url_builder import UrlBuilder

PATCH = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
DDRAGON_URL = f"https://ddragon.leagueoflegends.com/cdn/{PATCH}/"

DDRAGON_DICT = {
	"champions": UrlBuilder("data/en_US/champion.json"),
	"champion": UrlBuilder("data/en_US/champion/{champion}.json")
}

def request(req_type:str, **req_params_kargs):
	return requests.get(f"{DDRAGON_URL}{DDRAGON_DICT[req_type].build(**req_params_kargs)}").json()

CHAMPION_KEYS = {int(champ_dict['key']):champ for champ,champ_dict in request("champions")["data"].items()}

def get_champion(id:int) -> str:
	return CHAMPION_KEYS[id]