from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
# This imports your original 'game' class from your checkers.py file
from checkers import game as CheckersGame 

app = Flask(__name__)
# SocketIO allows real-time communication between browsers and this server
socketio = SocketIO(app, cors_allowed_origins="*")

# This dictionary holds all active matches running on your website
# Structure will be: {"ROOM_CODE": CheckersGameInstance}
active_games = {}

@app.route('/')
def home():
    # Adding a cache-busting header directly from Flask to force browsers to reload
    response = app.make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    return response

@socketio.on('join_match')
def handle_join(data):
    room_code = data['room']
    join_room(room_code)
    
    # If this game room doesn't exist yet, create a fresh game instance for it
    if room_code not in active_games:
        new_game = CheckersGame()
        new_game.start_game() # This sets up your 8x8 matrix array
        active_games[room_code] = new_game
        
    # Send the current board array state back to the player who joined
    current_board = active_games[room_code].board.board
    emit('sync_board', {'board': current_board}, to=room_code)

@socketio.on('player_click_move')
def handle_move(data):
    room_code = data['room']
    player_color = data['player'] # "R" or "W"
    
    # The exact grid coordinates sent automatically by the browser click event
    r = data['r']
    c = data['c']
    nr = data['nr']
    nc = data['nc']
    
    current_game = active_games[room_code]
    
    # 1. Check if it is actually this player's turn
    if current_game.current_turn != player_color:
        emit('error_msg', {'message': "It is not your turn!"}, room=request.sid)
        return

    # 2. Run your existing game logic using the coordinates
    # Note: Ensure your move_piece method returns (True/False) or handles success cleanly
    success = current_game.board.move_piece(r, c, nr, nc, player_color)
    
    # 3. If the move worked, broadcast the updated board to BOTH players in the room
    # If your move_piece modifies the board array directly, we grab that updated array:
    emit('sync_board', {'board': current_game.board.board}, to=room_code)

if __name__ == '__main__':
    socketio.run(app, debug=True, port=8080)