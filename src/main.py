from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import secrets

# Starting the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key+6561€=<3'
socketio = SocketIO(app)

# Variables
PARTICIPANTS = []
HOST_TOKEN = secrets.token_hex(16)
NB_SONGS = 1 
SONG_DURATION = 10
SONG_INF = 0
SONG_SUP = 180 - SONG_DURATION
SONG_START = 30
song = {
    "src": "../static/songs/【推しの子】ノンクレジットオープニング｜YOASOBI「アイドル」.mp4",
    "start": 30,
    "answer": "oshi no ko"
}


# Initilisation of the seed

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
    emit('song_playing', {'src': song['src'], 'start': song['start'] , 'duration': SONG_DURATION}, broadcast=True)

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
    emit('song_revealed', {'src': song['src'], 'start': song['start'] , 'duration': 1.5*SONG_DURATION}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)