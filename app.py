import os
import random
import string
from flask import Flask, render_init, render_template, request
from flask_socketio import SocketIO, emit, join_room
from game_logic import CheckersEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chequers_secret_key_12345!'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage matrices for active rooms
ACTIVE_ROOMS = {}

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('create_game')
def on_create(data):
    username = data.get('username', 'Player 1')[:12]
    room_code = generate_room_code()
    ACTIVE_ROOMS[room_code] = {
        "engine": CheckersEngine(),
        "players": {"R": {"username": username, "sid": request.sid}, "W": None},
        "timers": {"R": 180, "W": 180}
    }
    join_room(room_code)
    emit('room_created', {'room_code': room_code, 'color': 'R', 'username': username})

@socketio.on('join_game')
def on_join(data):
    username = data.get('username', 'Player 2')[:12]
    room_code = data.get('room_code', '').upper()
    
    if room_code in ACTIVE_ROOMS:
        room = ACTIVE_ROOMS[room_code]
        if room["players"]["W"] is None:
            room["players"]["W"] = {"username": username, "sid": request.sid}
            join_room(room_code)
            emit('game_started', {
                'board': room["engine"].board,
                'current_turn': room["engine"].current_turn,
                'r_user': room["players"]["R"]["username"],
                'w_user': username,
                'r_score': room["engine"].r_score,
                'w_score': room["engine"].w_score
            }, to=room_code)
        else:
            emit('error_message', {'msg': 'Room is completely full.'})
    else:
        emit('error_message', {'msg': 'Invalid room security token code.'})

@socketio.on('submit_move')
def on_move(data):
    room_code = data.get('room_code')
    player = data.get('color')
    r, c = data.get('r'), data.get('c')
    nr, nc = data.get('nr'), data.get('nc')
    
    room = ACTIVE_ROOMS.get(room_code)
    if room:
        engine = room["engine"]
        success, msg = engine.execute_move(r, c, nr, nc, player)
        if success:
            emit('update_state', {
                'board': engine.board,
                'current_turn': engine.current_turn,
                'r_score': engine.r_score,
                'w_score': engine.w_score,
                'status': engine.game_status
            }, to=room_code)
        else:
            emit('error_message', {'msg': msg}, to=request.sid)

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
