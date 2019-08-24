from app import app

import app.riot_requester_util as req_util

#from app import riot_requester_util

from flask import render_template

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/test")
def test():
	# return riot_requester_util.summary()
	# return requester.request("summoner_info", summoner_name='tsimplet')
	
	return req_util.get_summoners_rundown('NA', 'jamerr102030', 'TsimpleT', 'SuperFranky', 'JDG Yagao', 'Takaharu', 'A Little Cat')
