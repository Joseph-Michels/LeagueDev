from app import app
from app import riot_requester

from flask import render_template

requester = riot_requester.get(trace=False, email='bobelement4181@gmail.com', password='testtest')

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/test")
def test():
    return requester.request("summoner_info", summoner_name='tsimplet')