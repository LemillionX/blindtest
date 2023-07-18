from flask import Flask, render_template, request, jsonify, redirect, url_for, make_response
from flask_socketio import SocketIO, emit
from waitress import serve
import secrets
import json
import numpy as np

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
app.shared_variable = {'song_idx':0, 'indices': [], 'start': [],  'song': None, 'players':{}}
HOST_TOKEN = secrets.token_hex(16)
NB_SONGS = 5 
SONG_DURATION = 10
SONG_INF = 0
SONG_SUP = max(90 - SONG_DURATION, SONG_INF + SONG_DURATION)
SONG_START = 30
LST_SONG = {}
with open('./static/songs/songs.json', 'r', encoding='utf-8') as file:
    LST_SONG = json.load(file)['songs']

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
    if len(app.shared_variable["players"]) == 0 or app.shared_variable['song_idx'] == NB_SONGS-1:
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
    user = {"username":username, "score":0}
    app.shared_variable["players"][request.cookies.get('player_id')] = user
    emit('message', f'{username} has joined the game.')
    emit('user_joined', {'username':username}, broadcast=True)
    if token == HOST_TOKEN:
        emit('show_start_button')
    emit('participants', app.shared_variable["players"], broadcast=True)

# Socket to launch the game
@socketio.on('start_game')
def on_start_game():
    print("Starting the game...")
    app.shared_variable['song_idx'] = 0
    app.shared_variable['start'] = np.random.randint(SONG_INF, SONG_SUP, len(LST_SONG)).tolist()
    for idx, song in enumerate(LST_SONG):
        song['start'] = app.shared_variable['start'][idx]
    app.shared_variable['indices'] = np.random.choice(np.arange(len(LST_SONG)), size=NB_SONGS, replace=False).tolist()
    app.shared_variable['song'] = LST_SONG[app.shared_variable['indices'][app.shared_variable['song_idx']]]
    for player in app.shared_variable["players"]:
        app.shared_variable["players"][player]["score"] = 0
    emit('participants', app.shared_variable["players"], broadcast=True)
    emit('game_started', url_for("game") , broadcast=True, include_self=False)

# Socket for initial connection to the server 
@socketio.on('connect')
def on_connect():
    emit('message', 'You are connected')
    emit('participants', app.shared_variable["players"])

# Socket to play songs
@socketio.on('play_song')
def on_play_song():
    print(f"Now playing : {app.shared_variable['song']}")
    emit('song_playing', {  'src': app.shared_variable['song']['src'],
                            'start': app.shared_variable['song']['start'],
                            'duration': SONG_DURATION
                            },
                            broadcast=True)

# Socket to check the answer
@socketio.on('check_answer')
def on_check_answer(data):
    answer = data['answer'].lower()
    if answer in list(map(lambda x: x.lower(), app.shared_variable['song']['answer'])):
        app.shared_variable["players"][request.cookies.get('player_id')]["score"] += 1
        emit('participants', app.shared_variable["players"], broadcast=True) 

# Socket for the reveal of the song
@socketio.on('reveal_song')
def on_reveal_song():
    emit('song_revealed', { 'src': app.shared_variable['song']['src'],
                            'start': app.shared_variable['song']['start'],
                            'duration': 1.5*SONG_DURATION,
                            'name': app.shared_variable['song']['answer']
                            },
                            broadcast=True)

# Socket to load the next song
@socketio.on('load_next_song')
def on_load_next_song():
    if app.shared_variable['song_idx'] + 1 < NB_SONGS:
        app.shared_variable['song_idx'] +=1
        app.shared_variable['song'] = LST_SONG[app.shared_variable['indices'][app.shared_variable['song_idx']]]
        emit('next_song_loaded', broadcast=True)
    else:
        emit('game_ended', broadcast=True)

if __name__ == '__main__':
    # socketio.run(app)
    # Development server
    # app.run(host='0.0.0.0', port=4397, ssl_context='adhoc')

    # Deployment server
    serve(app, host='0.0.0.0', port=4397)