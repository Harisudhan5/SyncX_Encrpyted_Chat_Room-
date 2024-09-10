from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = {}

def generate_secret_key(length=32):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    data = request.json
    user_name = data.get('user_name')
    if not user_name:
        return jsonify({'status': 'error', 'message': 'User name is required'})
    
    room_name = generate_secret_key()
    secret_key = generate_secret_key()
    rooms[room_name] = secret_key
    return jsonify({'room_name': room_name, 'secret_key': secret_key})

@app.route('/join_room', methods=['POST'])
def join_room_route():
    data = request.json
    room_name = data.get('room_name')
    secret_key = data.get('secret_key')
    user_name = data.get('user_name')
    if not user_name:
        return jsonify({'status': 'error', 'message': 'User name is required'})
    
    if rooms.get(room_name) == secret_key:
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Wrong credentials'})

@app.route('/chat')
def chat():
    return render_template('chat.html')

@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    user_name = data['user_name']
    emit('message', f'{user_name}: {message}', room=room)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    user_name = data['user_name']
    join_room(room)
    emit('message', f'{user_name} has joined the room {room}', room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    user_name = data['user_name']
    leave_room(room)
    emit('message', f'{user_name} has left the room {room}', room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
