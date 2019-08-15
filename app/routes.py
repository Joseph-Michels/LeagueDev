from app import app

# from app import riot_requester
# requester = riot_requester.get(trace=False, email='bobelement4181@gmail.com', password='testtest')

from app import riot_requester_util

from flask import render_template

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/test")
def test():
    return riot_requester_util.summary()
    # return requester.request("summoner_info", summoner_name='tsimplet')
