import requests
from app import app

import app.riot_requester_util as req_util

from flask import render_template, redirect, url_for, flash

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/results/<req>", methods=['GET', 'POST'])
def results(req=''):
	try:
		return render_template("results.html", result=req_util.get_summoners_rundown('NA', *req.split(',')))
	except requests.exceptions.RequestException as e:
		e_dict = eval(str(e))
		flash(f'Error {e_dict["status_code"]} requesting "{e_dict["url"]}": "{e_dict["message"]}""')
		return redirect(f"{url_for('home')}")


# keep at bottom
@app.route("/<path:path>")
def error_page(path):
	flash(f'url "/{path}"" not found.')
	return redirect(f"{url_for('home')}")