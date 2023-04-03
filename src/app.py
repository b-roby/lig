import os

from flask import Flask, request, render_template, redirect, url_for
from summoner import Summoner
from live_summoner import LiveSummoner
from game import Game

app = Flask(__name__)
game = None

@app.route('/', methods=["GET", "POST"])
def show():
    if request.method == "GET":
        return render_template('base.html')

    if request.method == "POST":
        summoner_name = request.form.get("summoner_name")
        region = request.form.get("region")
        player = Summoner(summoner_name, region)
        players = []
        players.append(player)
        return redirect(url_for(".lookup", summoner = summoner_name, region=region))

@app.route("/lookup", methods=["GET", "POST"])
def lookup():
    summoner_name = request.args.get("summoner")
    region = request.args.get("region")

    player = Summoner(summoner_name, region)
    return render_template("lookup.html", player=player)

@app.route("/livegame", methods=["GET", "POST"])
def livegame():
    players = []
    if request.method == "GET":
        game = None
        players.clear()
        return render_template("base.html")
    
    if request.method == "POST":
        summoner_name = request.form.get("summoner_name")
        region = request.form.get("region")
        invoker = Summoner(summoner_name, region)
        game = Game(invoker)
        del invoker
        players = game.players

        return render_template("livegame.html", players=players)
