from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import secrets
import json

# Starting the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key+6561€=<3'
socketio = SocketIO(app)

# Variables
app.shared_variable = {'song_idx':0, 'song': None}
PARTICIPANTS = []
HOST_TOKEN = secrets.token_hex(16)
NB_SONGS = 2 
SONG_DURATION = 10
SONG_INF = 0
SONG_SUP = 180 - SONG_DURATION
SONG_START = 30
LST_SONG = {}
with open('./static/songs/songs.json', 'r', encoding='utf-8') as file:
    LST_SONG = json.load(file)['songs']

# Initilisation of the seed
for idx, song in enumerate(LST_SONG):
    song['start'] = SONG_START

app.shared_variable['song'] = LST_SONG[app.shared_variable['song_idx']]


# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/')
def room():
    if len(PARTICIPANTS) == 0:
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
    PARTICIPANTS.append(username)
    emit('message', f'{username} has joined the game.')
    emit('user_joined', {'username':username}, broadcast=True)
    if token == HOST_TOKEN:
        emit('show_start_button')

# Socket to launch the game
@socketio.on('start_game')
def on_start_game():
    emit('game_started', url_for("game") , broadcast=True, include_self=False)

# Socket for initial connection to the server 
@socketio.on('connect')
def on_connect():
    emit('message', 'You are connected')
    emit('participants', {'participants':PARTICIPANTS})

# Socket to play songs
@socketio.on('play_song')
def on_play_song():
    emit('song_playing', {  'src': app.shared_variable['song']['src'],
                            'start': app.shared_variable['song']['start'],
                            'duration': SONG_DURATION},
                            broadcast=True)

# Socket to check the answer
@socketio.on('check_answer')
def on_check_answer(data):
    answer = data['answer'].lower()
    if answer in song['answer']:
        print("Correct !")
    else:
        print("Wrong !")

# Socket for the reveal of the song
@socketio.on('reveal_song')
def on_reveal_song():
    emit('song_revealed', { 'src': app.shared_variable['song']['src'],
                            'start': app.shared_variable['song']['start'],
                            'duration': 1.5*SONG_DURATION,
                            'name':app.shared_variable['song']['answer']},
                            broadcast=True)

# Socket to load the next song
@socketio.on('load_next_song')
def on_load_next_song():
    if app.shared_variable['song_idx'] + 1 < NB_SONGS:
        app.shared_variable['song_idx'] +=1
        app.shared_variable['song'] = LST_SONG[app.shared_variable['song_idx']]


if __name__ == '__main__':
    socketio.run(app)