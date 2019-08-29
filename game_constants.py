# season X is year 2010+X
def SEASONS(i):
	return (("PRE" if i%2==0 else "")+"SEASON", 3+i//2)

_QUEUES = {
	0: "Custom",
	72: "1v1 Snowdown Showdown", 73: "2v2 Snowdown Showdown", 75: "6v6 Hexakill", 76: "URF", 78: "One For All: Mirror Mode",
	83: "Co-op vs AI URF",
	98: "6v6 Hexakill",
	100: "5v5 ARAM",
	310: "Nemesis Draft", 313: "Black Market Brawlers", 317: "Definitely Not Dominion", 325: "All Random",
	400: "5v5 Normal Draft", 420: "5v5 Ranked Solo/Duo", 430: "5v5 Blind Pick", 440: "5v5 Ranked Flex",
	450: "5v5 ARAM", 460: "3v3 Blind Pick", 470: "3v3 Ranked Flex",
	600: "Blood Hunt Assassin", 610: "Dark Star: Singularity",
	700: "Clash",
	800: "Co-op vs AI Intermediate Bot", 810: "Co-op vs AI Intro Bot", 820: "Co-op vs AI Beginner Bot",
	850: "Co-op vs AI Intermediate Bot", 840: "Co-op vs AI Intro Bot", 830: "Co-op vs AI Beginner Bot",
	900: "ARURF", 910: "Ascension", 920: "Legend of the Poro King", 940: "Nexus Siege",
	950: "Doom Bots Voting", 960: "Doom Bots Standard",
	980: "Star Guardian Invasion: Normal", 990: "Star Guardian Invasion: Onslaught",
	1000: "PROJECT: Hunters", 1010: "Snow ARURF", 1020: "One For All",
	1030: "Odyssey Extraction: Intro", 1040: "Odyssey Extraction: Cadet", 1050: "Odyssey Extraction: Crewmember", 
	1060: "Odyssey Extraction: Captain", 1070: "Odyssey Extraction: Onslaught",
	1090: "Teamfight Tactics", 1100: "Ranked Teamfight Tactics"
}

def QUEUES(i):
	return _QUEUES[i] if i in _QUEUES else "Unknown Queue"

_MAPS = {
	1: "Summoner's Rift", #Original Summer variant
	2: "Summoner's Rift", #Original Autumn variant
	3: "The Proving Grounds", #Tutorial map
	4: "Twisted Treeline", #Original version
	8: "The Crystal Scar", #Dominion map
	10: "Twisted Treeline", #Current version
	11: "Summoner's Rift", #Current version
	12: "Howling Abyss", #ARAM map
	14: "Butcher's Bridge", #ARAM map
	16: "Cosmic Ruins", #Dark Star: Singularity map
	18: "Valoran City Park", #Star Guardian Invasion map
	19: "Substructure 43", #PROJECT: Hunters map
	20: "Crash Site", #Odyssey: Extraction map
	21: "Nexus Blitz" #Nexus Blitz map
}

def MAPS(i):
	return _MAPS[i] if i in _MAPS else "Unknown Map"