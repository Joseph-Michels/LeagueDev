import requests
import os
from flask import render_template, redirect, url_for, flash, send_from_directory

from app import app
import app.riot_requester_util as req_util

req_util_dict = {}

@app.route("/")
def root():
	return redirect(url_for("home"))

@app.route("/home")
@app.route("/home/<req>", methods=['GET','POST'])
def home(req=""):
	print(f'home: "{req}"')
	if req == "":
		return render_template("home.html", page_name="Scout Five")
	else:
		try:
			arr = req.split(',')
			print(arr)
			req_util_dict[req] = req_util.get_summoners_rundown('NA', *arr)
			return redirect(f"/results/{req}")
		except requests.exceptions.RequestException as e:
			e_dict = eval(str(e))
			flash(f'Error {e_dict["status_code"]} requesting "{e_dict["url"]}": "{e_dict["message"]}""')
			return redirect(url_for('home'))


@app.route("/results/<req>", methods=['GET', 'POST'])
def results(req):
	if req in req_util_dict:
		return render_template("results.html", page_name="Search Results", results=req_util_dict[req])
	else:
		return redirect(f"/home/{req}")

@app.route("/favicon.ico")
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')



# keep at bottom
@app.route("/<path:path>")
def error_page(path):
	flash(f'url "/{path}"" not found.')
	return redirect(url_for('home'))