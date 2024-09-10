from flask import Flask, request, Response, jsonify, abort, render_template, flash, redirect, url_for
import requests
import MySQLdb
import logging
import json
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
    app.config['SECRET_KEY'] = os.environ.get('secret_key')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

### ROUTES ###

# home page
@app.route("/", methods=["GET"])
def index():
    conn = MySQLdb.connect(
        host=os.environ.get('db_host'),
        user=os.environ.get('db_user'),
        passwd=os.environ.get('db_pass'),
        db=os.environ.get('db_database'),
        port=int(os.environ.get('db_port'))
    )
    return render_template("index.html", players=get_all_players(conn))

# add a new player
@app.route('/addPlayer', methods=["GET", "POST"])
def addPlayer():
    if request.method == "POST":
        try:
            name = request.form['player_name']
            age = request.form['player_age']
            height = request.form['player_height']
            team = request.form['player_team']
            position = request.form['player_position']
            jersey_number = request.form['player_jersey_num']
            if not validate_form(age, height, jersey_number):
                flash("Invalid player data.", category="error")
            else:
                conn = MySQLdb.connect(
                    host=os.environ.get('db_host'),
                    user=os.environ.get('db_user'),
                    passwd=os.environ.get('db_pass'),
                    db=os.environ.get('db_database'),
                    port=int(os.environ.get('db_port'))
                )
                cursor = conn.cursor()
                query = f'''INSERT INTO players (name, age, height, team, `position`, jersey_number)
                            VALUES ("{name}", {age}, {height}, "{team}", "{position}", {jersey_number});'''
                cursor.execute(query)
                conn.commit()
                cursor.close()
                conn.close()
                flash(f'Successfully added player: "{name}"', category="info")
                return redirect(url_for('index'))
        except:
            app.logger.error("Could not parse form.")
            flash("Invalid player data.", category="error")
    return render_template('addPlayer.html')

# pull information about an existing player
@app.route("/player/<id>", methods=["GET", "DELETE"])
def getPlayer(id):
    conn = MySQLdb.connect(
        host=os.environ.get('db_host'),
        user=os.environ.get('db_user'),
        passwd=os.environ.get('db_pass'),
        db=os.environ.get('db_database'),
        port=int(os.environ.get('db_port'))
    )
    if request.method == "GET":
        player = lookup_player(conn, id)
        conn.close()
        return render_template("player.html", player=player)
    if request.method == "DELETE":
        return jsonify(delete_player(conn, id))

# update an existing player
@app.route("/player/<id>/update", methods=["GET", "POST"])
def updatePlayer(id):
    conn = MySQLdb.connect(
        host=os.environ.get('db_host'),
        user=os.environ.get('db_user'),
        passwd=os.environ.get('db_pass'),
        db=os.environ.get('db_database'),
        port=int(os.environ.get('db_port'))
    )
    player = lookup_player(conn, id)
    if request.method == "POST":
        player_data = {}
        try:
            player_data["name"] = request.form['player_name']
            player_data["age"] = request.form['player_age']
            player_data["height"] = request.form['player_height']
            player_data["team"] = request.form['player_team']
            player_data["position"] = request.form['player_position']
            player_data["jersey_number"] = request.form['player_jersey_num']
            if not validate_form(player_data["age"], player_data["height"], player_data["jersey_number"]):
                flash("Invalid player data.")
            else:
                update_player(conn, id, updates=player_data)
                flash(f'Successfully updated player: "{player_data["name"]}"', category="info")
                return redirect(url_for('index'))
        except:
            app.logger.error("Could not parse form.")
            flash("Invalid player data.", category="error")
    return render_template('updatePlayer.html', player=player)

# delete an existing player
@app.route("/player/<id>/delete", methods=["POST"])
def deletePlayer(id):
    conn = MySQLdb.connect(
        host=os.environ.get('db_host'),
        user=os.environ.get('db_user'),
        passwd=os.environ.get('db_pass'),
        db=os.environ.get('db_database'),
        port=int(os.environ.get('db_port'))
    )
    player_name = lookup_player(conn, id)["name"]
    delete_player(conn, id)
    flash(f'Successfully deleted player: "{player_name}"', category="info")
    return redirect(url_for('index'))


### FUNCTIONS ###

def validate_form(age, height, jersey_number):
    try:
        a = int(age)
        h = float(height)
        j = int(jersey_number)
        if (a <= 0) or (h <= 0) or (j not in range(0,100)):
            return False
    except:
        return False
    return True

def get_all_players(conn):
    players = []
    cursor = conn.cursor()
    query = "SELECT * FROM players;"
    cursor.execute(query)
    records = cursor.fetchall()
    fields = [column[0] for column in cursor.description]
    for record in records:
        player_data = {}
        for i in range(0,len(fields)):
            player_data[fields[i]] = record[i]
        players.append(player_data)
    cursor.close()
    conn.close()
    return players  

def lookup_player(conn, id):
    data = {}
    cursor = conn.cursor()
    query = f"SELECT * FROM players p WHERE p.id = {id};"
    cursor.execute(query)
    record = cursor.fetchone()
    fields = [column[0] for column in cursor.description]
    cursor.close()
    # importantly, we don't close conn here, since we sometimes need to use this function as an intermediate step
    for i in range(0,len(fields)):
        data[fields[i]] = record[i]
    return data

def update_player(conn, id, updates):
    cursor = conn.cursor()
    query = f'''UPDATE players
                SET name = "{updates["name"]}", age = {updates["age"]}, height = {updates["height"]},
                team = "{updates["team"]}", `position` = "{updates["position"]}", jersey_number = {updates["jersey_number"]}
                WHERE id = {id};'''
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    return f"Updated player ID: {id}."

def delete_player(conn, id):
    cursor = conn.cursor()
    query = f"DELETE FROM players p WHERE p.id = {id};"
    cursor.execute(query)
    conn.commit()
    cursor.close()
    conn.close()
    return f"Deleted player ID: {id}."
    