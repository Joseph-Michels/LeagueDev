from app import app

from app.riot_requester import RiotRequester
requester = RiotRequester('NA', trace=False)

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
    
    return str(requester.get_summoners_rundown('tsimplet'))

@app.route("/test2")
def test2():
    return str(requester.safe_request("summoner_info", summoner_name='tsimplet'))
