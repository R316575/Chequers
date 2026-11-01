import os
import uuid
import threading
import time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__, static_folder='static', template_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chequers-secret-key-12345')
socketio = SocketIO(app, cors_allowed_origins="*")

# --- MEMORY DATABASE FOR ACTIVE GAMES ---
ACTIVE_GAMES = {} # room_code: { 'board': board_obj, 'players': {sid: 'R'}, 'started': False, 'disconnect_timer': None }

class Board:
    def __init__(self):
        self.board = [[" " for _ in range(8)] for _ in range(8)]
        self.w_score = 0
        self.r_score = 0
        self.current_turn = "R"
        self.initialise_board()

    def initialise_board(self):
        for x in range(8):
            if (x % 2) == 0:
                if x < 3:
                    self.board[x][1], self.board[x][3], self.board[x][5], self.board[x][7] = "w", "w", "w", "w"
                elif x > 4:
                    self.board[x][1], self.board[x][3], self.board[x][5], self.board[x][7] = "r", "r", "r", "r"
            else:
                if x < 3:
                    self.board[x][0], self.board[x][2], self.board[x][4], self.board[x][6] = "w", "w", "w", "w"
                elif x > 4:
                    self.board[x][0], self.board[x][2], self.board[x][4], self.board[x][6] = "r", "r", "r", "r"

    def switch_turn(self):
        self.current_turn = "W" if self.current_turn == "R" else "R"

    def check_forced_capture(self, player):
        # Ported logic directly from your algorithm rules specification
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if player == "R" and piece in "Rr":
                    if piece == "r": # regular red moves up (decreasing row index)
                        if row >= 2:
                            if col <= 5 and self.board[row-1][col+1] in "Ww" and self.board[row-2][col+2] == " ": return True
                            if col >= 2 and self.board[row-1][col-1] in "Ww" and self.board[row-2][col-2] == " ": return True
                    if piece == "R": # red king can move anywhere
                        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                            if 0 <= row+2*dr < 8 and 0 <= col+2*dc < 8:
                                if self.board[row+dr][col+dc] in "Ww" and self.board[row+2*dr][col+2*dc] == " ": return True
                elif player == "W" and piece in "Ww":
                    if piece == "w": # regular white moves down (increasing row index)
                        if row <= 5:
                            if col <= 5 and self.board[row+1][col+1] in "Rr" and self.board[row+2][col+2] == " ": return True
                            if col >= 2 and self.board[row+1][col-1] in "Rr" and self.board[row+2][col-2] == " ": return True
                    if piece == "W": # white king
                        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                            if 0 <= row+2*dr < 8 and 0 <= col+2*dc < 8:
                                if self.board[row+dr][col+dc] in "Rr" and self.board[row+2*dr][col+2*dc] == " ": return True
        return False

    def validate_and_move(self, r, c, nr, nc, player):
        if self.board[r][c] == " " or self.board[r][c].upper() != player:
            return False, "That is not your piece!"
        if self.board[nr][nc] != " ":
            return False, "Target space is already occupied."

        piece = self.board[r][c]
        dr, dc = nr - r, nc - c
        is_capture = abs(dr) == 2 and abs(dc) == 2
        is_step = abs(dr) == 1 and abs(dc) == 1
        has_forced = self.check_forced_capture(player)

        if has_forced and not is_capture:
            return False, "Invalid Move! A forced capture option is available."

        # Directional validation based on Piece Rules
        if piece == "r" and dr >= 0: return False, "Normal Red pieces can only move forwards."
        if piece == "w" and dr <= 0: return False, "Normal White pieces can only move forwards."

        if is_step:
            self.board[nr][nc] = piece
            self.board[r][c] = " "
        elif is_capture:
            mid_r, mid_c = r + dr // 2, c + dc // 2
            enemy_piece = self.board[mid_r][mid_c]
            if enemy_piece == " " or enemy_piece.upper() == player:
                return False, "You cannot jump your own pieces or empty tiles."
            
            self.board[nr][nc] = piece
            self.board[r][c] = " "
            self.board[mid_r][mid_c] = " "
            if player == "R": self.r_score += 1
            else: self.w_score += 1
        else:
            return False, "Pieces can only move diagonally 1 or 2 squares."

        # Crown evaluations at opposite rows
        if player == "R" and nr == 0: self.board[nr][nc] = "R"
        if player == "W" and nr == 7: self.board[nr][nc] = "W"

        self.switch_turn()
        return True, "Success"

    def check_no_moves(self, player):
        # Simplified terminal validator checking simple shifts or jumps
        for r in range(8):
            for r in range(8):
                for c in range(8):
                    if self.board[r][c].upper() == player:
                        for dr in [-2, -1, 1, 2]:
                            for dc in [-2, -1, 1, 2]:
                                nr, nc = r + dr, c + dc
                                if 0 <= nr < 8 and 0 <= nc < 8:
                                    # Temporarily check if valid without affecting states
                                    if abs(dr) == 1 and self.board[nr][nc] == " ":
                                        if (player == "R" and self.board[r][c] == "r" and dr < 0) or (player == "W" and self.board[r][c] == "w" and dr > 0) or self.board[r][c].isupper():
                                            return False
        return True

# --- HTTP ROUTES ---
@app.route('/')
def index():
    # Serves the single page application HTML
    return render_template('index.html')

# NEW COMPATIBILITY ROUTE FOR PRIVATE ROOMS
@app.route('/api/create_room', methods=['POST'])
def api_create_room():
    data = request.get_json() or {}
    username = data.get('username', 'Player 1')[:12]
    room = str(uuid.uuid4())[:5].upper() # 5 character alphanumeric string
    
    ACTIVE_GAMES[room] = {
        'board': Board(),
        'players': {}, # Will map client sessions cleanly upon entrance socket connect strings
        'started': False,
        'disconnect_timer': None
    }
    return jsonify({'room_code': room, 'color': 'R'})


# --- SOCKET EVENTS ---
@socketio.on('create_game')
def on_create(data):
    """Fallback handler matching standard frontend initialization requests."""
    username = data.get('username', 'Player 1')[:12]
    room = str(uuid.uuid4())[:5].upper() # 5 character code
    join_room(room)
    ACTIVE_GAMES[room] = {
        'board': Board(),
        'players': {request.sid: {'name': username, 'color': 'R'}},
        'started': False,
        'disconnect_timer': None
    }
    emit('room_created', {'room_code': room, 'color': 'R'})


@socketio.on('join_game')
def on_join(data):
    username = data.get('username', 'Player')[:12]
    room = data.get('room_code', '').upper()
    
    if room in ACTIVE_GAMES:
        game_info = ACTIVE_GAMES[room]
        
        if len(game_info['players']) >= 2 and request.sid not in game_info['players']:
            emit('error_msg', 'Room is full!')
            return
            
        join_room(room)
        
        # Scenario A: Host joining
        if len(game_info['players']) == 0:
            game_info['players'][request.sid] = {'name': username, 'color': 'R'}
            emit('room_created', {'room_code': room, 'color': 'R'})
            
        # Scenario B: Second peer (Pat) joining
        elif len(game_info['players']) == 1 and request.sid not in game_info['players']:
            game_info['players'][request.sid] = {'name': username, 'color': 'W'}
            game_info['started'] = True
            
            p_list = list(game_info['players'].values())
            
            # FIXED INDICES: Pulling item 0 (Host) and item 1 (Pat) explicitly
            emit('game_ready', {
                'r_name': p_list[0]['name'], 
                'w_name': p_list[1]['name'], 
                'board': game_info['board'].board
            }, to=room)
    else:
        emit('error_msg', 'Invalid Room Code.')


@socketio.on('make_move')
def on_move(data):
    room = data.get('room_code')
    if room not in ACTIVE_GAMES: return
    game_info = ACTIVE_GAMES[room]
    board_obj = game_info['board']
    
    # Validation step to check if player session is actually registered in this room
    if request.sid not in game_info['players']:
        emit('error_msg', "Unauthorised session request.")
        return
        
    player_color = game_info['players'][request.sid]['color']
    if board_obj.current_turn != player_color:
        emit('error_msg', "It's not your turn yet!")
        return

    # Process and execute coordinates directly via your original game matrix calculations
    success, msg = board_obj.validate_and_move(data['r'], data['c'], data['nr'], data['nc'], player_color)
    if not success:
        emit('error_msg', msg)
        return

    # Check terminal win-loss conditions
    winner = None
    if board_obj.r_score == 12 or board_obj.check_no_moves("W"): 
        winner = "Red"
    elif board_obj.w_score == 12 or board_obj.check_no_moves("R"): 
        winner = "White"

    # Synchronise the updated map to both clients simultaneously in real-time
    emit('update_board', {
        'board': board_obj.board, 
        'turn': board_obj.current_turn, 
        'r_score': board_obj.r_score, 
        'w_score': board_obj.w_score,
        'winner': winner
    }, to=room)


@socketio.on('disconnect')
def on_disconnect():
    for room, game_info in list(ACTIVE_GAMES.items()):
        if request.sid in game_info['players']:
            # Alert the remaining peer that their opponent has temporarily dropped connection
            emit('connection_lost', to=room)
            
            # Start an isolated background tracking thread to handle a 30-second window for recovery
            def countdown(target_room):
                time.sleep(30)
                if target_room in ACTIVE_GAMES:
                    current_room_info = ACTIVE_GAMES[target_room]
                    # Terminate room permanently if the missing connection didn't rejoin in time
                    if len(current_room_info['players']) < 2:
                        socketio.emit('game_terminated', 'Opponent left permanently.', to=target_room)
                        del ACTIVE_GAMES[target_room]
                        
            threading.Thread(target=countdown, args=(room,)).start()


if __name__ == '__main__':
    socketio.run(app, debug=True)
