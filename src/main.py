from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import pygame
import secrets

# Starting the app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key+6561€=<3'
socketio = SocketIO(app)

# Variables
participants = []
host_token = secrets.token_hex(16)
song = {
    "src": "../static/songs/oshi-no-ko-opening01.mp3",
    "start": 30,
}
duration = 10

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/room/')
def room():
    if len(participants) == 0:
        token = host_token
    else:
        token = ''
    return render_template('room.html', token=token)

@app.route('/game/', methods=['POST'])
def game():
    token = request.form['token']
    print(token)
    print(f"Am I an host ? {token == host_token}")
    return render_template('game.html', style= token == host_token)

# Socket for the connexion to the room
@socketio.on('register')
def on_register(data):
    username = data['username']
    token = data['token']
    participants.append(username)
    emit('message', f'{username} has joined the game.')
    emit('user_joined', {'username':username}, broadcast=True)
    if token == host_token:
        emit('show_start_button')

# Socket for initial connection to the server 
@socketio.on('connect')
def on_connect():
    emit('message', 'You are connected')
    emit('participants', {'participants':participants})

# Socket to play songs
@socketio.on('play_song')
def on_play_song():
    emit('song_playing', {'src': song['src'], 'start': song['start'] , 'duration': duration}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)