from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_socketio import SocketIO, emit
import secrets
import json
import numpy as np
import sys

# Starting the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key+6561€=<3'
socketio = SocketIO(app)

# Security 
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)


# Variables
app.shared_variable = {'song_idx':0, 'indices': [], 'start': [],  'song': None, 'players':{}, 'hasStarted':False}
HOST_TOKEN = secrets.token_hex(16)
NB_SONGS = 30 
SONG_DURATION = 10
SONG_INF = 0
SONG_SUP = max(90 - SONG_DURATION, SONG_INF + SONG_DURATION)
SONG_START = 30
TIME_GUESS = 30
TIME_PENALTY = 4
LST_SONG = {}
with open('./static/songs/songs.json', 'r', encoding='utf-8') as file:
    LST_SONG = json.load(file)['songs']
print(f"You have {len(LST_SONG)} songs.")

# Routes
@app.route('/')
def index():
    player_id = request.cookies.get("player_id")
    if not player_id:
        player_id = secrets.token_hex(16)
    resp = make_response(render_template('index.html'))
    resp.set_cookie("player_id", player_id)
    return resp

@app.route('/room/')
def room():
    if len(app.shared_variable["players"]) == 0:
        token = HOST_TOKEN
    else:
        token = ''
    return render_template('room.html', token=token)

@app.route('/game/', methods=['POST', 'GET'])
def game():
    if request.method == 'POST': 
        token = request.form['token']
        return render_template('game.html', showPlayBtn= token == HOST_TOKEN)
    return render_template('game.html', showPlayBtn=False)

# Socket for the connexion to the room
@socketio.on('register')
def on_register(data):
    username = data['username']
    token = data['token']
    user = {"username":username, "score":0, "status": "", "timer": TIME_GUESS, 'hasJoined':False}
    app.shared_variable["players"][request.cookies.get('player_id')] = user
    print(f'{username} has joined the game.')
    emit('user_joined', {'username':username, 'key':request.cookies.get('player_id')})
    if token == HOST_TOKEN:
        emit('show_start_button')
    emit('participants', app.shared_variable["players"], broadcast=True)
    if app.shared_variable['hasStarted']:
        emit('game_started', url_for("game"))

# Socket to launch the game
@socketio.on('start_game')
def on_start_game():
    app.shared_variable['song_idx'] = 0
    app.shared_variable['start'] = np.random.randint(SONG_INF, SONG_SUP, len(LST_SONG)).tolist()
    for idx, song in enumerate(LST_SONG):
        song['start'] = app.shared_variable['start'][idx]
    app.shared_variable['indices'] = np.random.choice(len(LST_SONG), size=NB_SONGS, replace=False).tolist()
    app.shared_variable['song'] = LST_SONG[app.shared_variable['indices'][app.shared_variable['song_idx']]]
    for player in app.shared_variable["players"]:
        app.shared_variable["players"][player]["score"] = 0
    emit('participants', app.shared_variable["players"], broadcast=True)
    emit('game_started', {'route':url_for("game"), 'game_started':app.shared_variable['hasStarted']} , broadcast=True, include_self=False)
    app.shared_variable['hasStarted'] = True

# Socket for initial connection to the server 
@socketio.on('connect')
def on_connect():
    player = app.shared_variable["players"].get(request.cookies.get('player_id'))
    if (player is not None) and (not player['hasJoined']):
        app.shared_variable["players"][request.cookies.get('player_id')]['hasJoined'] = True
    emit('participants', app.shared_variable["players"])

# # Socket for disconnection
# @socketio.on('disconnect')
# def on_disconnect():
#     player = request.cookies.get('player_id')
#     print(f"{player} left the room")
#     if (app.shared_variable["players"].get(player) is not None) and (app.shared_variable["players"][player]['hasJoined']):
#         app.shared_variable['players'].pop(player)
#     if len(app.shared_variable['players']) == 0:
#         app.shared_variable['hasStarted'] = False
#     emit('participants', app.shared_variable["players"], broadcast=True)

# Socket to play songs
@socketio.on('play_song')
def on_play_song():
    emit('song_playing', {  'src': app.shared_variable['song']['src'],
                            'start': app.shared_variable['song']['start'],
                            'duration': SONG_DURATION
                            },
                            broadcast=True)

# Socket to check the answer
@socketio.on('check_answer')
def on_check_answer(data):
    answer = data['answer'].lower().strip()
    if answer in list(map(lambda x: x.lower().strip(), app.shared_variable['song']['answer'])):
        app.shared_variable["players"][request.cookies.get('player_id')]["score"] += 1
        app.shared_variable["players"][request.cookies.get('player_id')]["status"] ="has found"
        emit('correct_answer')
    else:
        app.shared_variable["players"][request.cookies.get('player_id')]["status"] ="has not found"
        emit('wrong_answer')
    emit('participants', app.shared_variable["players"], broadcast=True)

# Socket for the reveal of the song
@socketio.on('reveal_song')
def on_reveal_song():
    emit('song_revealed', { 'src': app.shared_variable['song']['src'],
                            'start': app.shared_variable['song']['start'],
                            'duration': 1.5*SONG_DURATION,
                            'name': " / ".join(app.shared_variable['song']['answer'])
                            },
                            broadcast=True)

# Socket to load the next song
@socketio.on('load_next_song')
def on_load_next_song():
    if app.shared_variable['song_idx'] + 1 < NB_SONGS:
        app.shared_variable['song_idx'] +=1
        app.shared_variable['song'] = LST_SONG[app.shared_variable['indices'][app.shared_variable['song_idx']]]
        emit('next_song_loaded', {'current_song':app.shared_variable['song_idx']+1, 'nb_songs':NB_SONGS }, broadcast=True)
    else:
        emit('game_ended', broadcast=True)
        app.shared_variable['song_idx'] = 0
    for player in app.shared_variable["players"]:
        app.shared_variable["players"][player]["status"] = ""
        app.shared_variable["players"][player]["timer"] = TIME_GUESS
    emit('participants', app.shared_variable["players"], broadcast=True)


# Socket for time decreasing
@socketio.on('time_decreasing')
def on_time_decreasing(data):
    if data["time"] == "TIME_PENALTY":
        app.shared_variable["players"][data["key"]]["timer"] = max(0, app.shared_variable["players"][data["key"]]["timer"] - TIME_PENALTY)
    else:
        app.shared_variable["players"][data["key"]]["timer"] = max(0, app.shared_variable["players"][data["key"]]["timer"] - int(data["time"]))
    emit('participants', app.shared_variable["players"], broadcast=True)

if __name__ == '__main__':
    if len(sys.argv) == 1 or len(sys.argv) > 2:
        print("You need to enter the port number where to run the app. Run main.py -h for more details")

    if len(sys.argv) == 2:
        if sys.argv[1] in ['-h', '--help']:
            print('To launch the app, run: \t main.py <port> \n where <port> is the number of the port where you want to launch the server')
        else:
            app.run(host='0.0.0.0', port=int(sys.argv[1]), debug=True)
