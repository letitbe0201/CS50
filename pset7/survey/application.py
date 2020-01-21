import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

# Configure application
app = Flask(__name__)

# Reload templates when they are changed
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


# my code start from here


@app.route("/form", methods=["POST"])
def post_form():
    # handle idiots at the server side
    if not request.form.get("name") or not request.form.get("team") or not request.form.get("bet"):
        return render_template("error.html", message="Please enter your name, the team you choose and your bet!")
    # write the data to a csv file
    with open("survey.csv", "a") as file:
        writer = csv.writer(file)
        writer.writerow((request.form.get("name"), request.form.get("team"), request.form.get("bet")))
    # redirect to the sheet.html
    return redirect("/sheet")


@app.route("/sheet")
def get_sheet():
    # read the data in the csv and pass it to the sheet.html
    with open("survey.csv", "r") as file:
        reader = csv.reader(file)
        players = list(reader)
    return render_template("sheet.html", players=players)