from flask import Flask, render_template, request, jsonify
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

if __name__ == '__main__':
    socketio.run(app)