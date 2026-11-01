import os
import uuid
import threading
import time
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__, static_folder='static', template_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chequers-secret-key-12345')
socketio = SocketIO(app, cors_allowed_origins="*")

# --- MEMORY DATABASE FOR ACTIVE GAMES ---
ACTIVE_GAMES = {} 

class Board:
    def __init__(self):
        self.board = [[" " for _ in range(8)] for _ in range(8)]
        self.w_score = 0
        self.r_score = 0
        self.current_turn = "R"
        self.initialise_board()

    def initialise_board(self):
        """Populates pieces on the correct dark squares."""
        for row in range(8):
            for col in range(8):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = "w"  
                    elif row > 4:
                        self.board[row][col] = "r"  

    def switch_turn(self):
        self.current_turn = "W" if self.current_turn == "R" else "R"

    def check_forced_capture(self, player):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if player == "R" and piece in "Rr":
                    if piece == "r" and row >= 2:
                        if col <= 5 and self.board[row-1][col+1] in "Ww" and self.board[row-2][col+2] == " ": return True
                        if col >= 2 and self.board[row-1][col-1] in "Ww" and self.board[row-2][col-2] == " ": return True
                    if piece == "R":
                        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                            if 0 <= row+2*dr < 8 and 0 <= col+2*dc < 8:
                                if self.board[row+dr][col+dc] in "Ww" and self.board[row+2*dr][col+2*dc] == " ": return True
                elif player == "W" and piece in "Ww":
                    if piece == "w" and row <= 5:
                        if col <= 5 and self.board[row+1][col+1] in "Rr" and self.board[row+2][col+2] == " ": return True
                        if col >= 2 and self.board[row+1][col-1] in "Rr" and self.board[row+2][col-2] == " ": return True
                    if piece == "W":
                        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                            if 0 <= row+2*dr < 8 and 0 <= col+2*dc < 8:
                                if self.board[row+dr][col+dc] in "Rr" and self.board[row+2*dr][col+2*dc] == " ": return True
        return False

    def validate_and_move(self, r, c, nr, nc, player):
        if self.board[r][c] == " " or self.board[r][c].upper() != player:
            return False, "That is not your piece!"
        if self.board[nr][nc] != " ":
            return False, "Target space is occupied."

        piece = self.board[r][c]
        dr, dc = nr - r, nc - c
        is_capture = abs(dr) == 2 and abs(dc) == 2
        is_step = abs(dr) == 1 and abs(dc) == 1
        has_forced = self.check_forced_capture(player)

        if has_forced and not is_capture:
            return False, "Invalid Move! A forced capture option is available."

        if piece == "r" and dr >= 0: return False, "Normal Red pieces can only move forwards."
        if piece == "w" and dr <= 0: return False, "Normal White pieces can only move forwards."

        if is_step:
            self.board[nr][nc] = piece
            self.board[r][c] = " "
        elif is_capture:
            mid_r, mid_c = r + dr // 2, c + dc // 2
            enemy_piece = self.board[mid_r][mid_c]
            if enemy_piece == " " or enemy_piece.upper() == player:
                return False, "Invalid jump selection."
            
            self.board[nr][nc] = piece
            self.board[r][c] = " "
            self.board[mid_r][mid_c] = " "
            if player == "R": self.r_score += 1
            else: self.w_score += 1
        else:
            return False, "Pieces can only move diagonally 1 or 2 squares."

        if player == "R" and nr == 0: self.board[nr][nc] = "R"
        if player == "W" and nr == 7: self.board[nr][nc] = "W"

        self.switch_turn()
        return True, "Success"

    def check_no_moves(self, player):
        for r in range(8):
            for c in range(8):
                if self.board[r][c].upper() == player:
                    for dr in [-2, -1, 1, 2]:
                        for dc in [-2, -1, 1, 2]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < 8 and 0 <= nc < 8:
                                if abs(dr) == 1 and self.board[nr][nc] == " ":
                                    if (player == "R" and self.board[r][c] == "r" and dr < 0) or (player == "W" and self.board[r][c] == "w" and dr > 0) or self.board[r][c].isupper():
                                        return False
        return True

# --- HTTP API ROUTE ENDPOINTS ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create_room', methods=['POST'])
def api_create_room():
    data = request.get_json() or {}
    username = data.get('username', 'Player 1')[:12]
    room = str(uuid.uuid4())[:5].upper()
    
    ACTIVE_GAMES[room] = {
        'board': Board(),
        'players': {'user_1': {'name': username, 'color': 'R'}},
        'started': False
    }
    return jsonify({'room_code': room, 'color': 'R'})

@app.route('/api/join_room', methods=['POST'])
def api_join_room():
    data = request.get_json() or {}
    username = data.get('username', 'Player 2')[:12]
    room = data.get('room_code', '').upper()
    
    if room in ACTIVE_GAMES:
        game_info = ACTIVE_GAMES[room]
        if len(game_info['players']) >= 2:
            return jsonify({'success': False, 'error': 'Room is full!'}), 400
            
        game_info['players']['user_2'] = {'name': username, 'color': 'W'}
        game_info['started'] = True
        return jsonify({'success': True, 'room_code': room, 'color': 'W'})
    return jsonify({'success': False, 'error': 'Invalid Room Code.'}), 400

@app.route('/api/get_game_state', methods=['GET'])
def api_get_game_state():
    room = request.args.get('room_code', '').upper()
    if room in ACTIVE_GAMES:
        game_info = ACTIVE_GAMES[room]
        board_obj = game_info['board']
        p_vals = list(game_info['players'].values())
        
        r_name = p_vals[0]['name'] if len(p_vals) > 0 else "Host"
        w_name = p_vals[1]['name'] if len(p_vals) > 1 else "Waiting..."
        
        winner = None
        if board_obj.r_score == 12 or board_obj.check_no_moves("W"): winner = "Red"
        elif board_obj.w_score == 12 or board_obj.check_no_moves("R"): winner = "White"
        
        return jsonify({
            'started': game_info['started'],
            'turn': board_obj.current_turn,
            'r_name': r_name,
            'w_name': w_name,
            'board': board_obj.board,
            'r_score': board_obj.r_score,
            'w_score': board_obj.w_score,
            'winner': winner
        })
    return jsonify({'error': 'Invalid Room Code'}), 404

@app.route('/api/make_move', methods=['POST'])
def api_make_move():
    data = request.get_json() or {}
    room = data.get('room_code', '').upper()
    player_color = data.get('color')
    
    if room not in ACTIVE_GAMES: return jsonify({'error': 'Room not found'}), 404
    game_info = ACTIVE_GAMES[room]
    board_obj = game_info['board']
    
    if board_obj.current_turn != player_color: return jsonify({'error': "It's not your turn!"})
        
    success, msg = board_obj.validate_and_move(data['r'], data['c'], data['nr'], data['nc'], player_color)
    if not success: return jsonify({'error': msg})
    return jsonify({'success': True})

# Fallback Websocket Stubs to handle library links safely
@socketio.on('join_game')
def on_join(data): pass
@socketio.on('make_move')
def on_move(data): pass
@socketio.on('disconnect')
def on_disconnect(): pass

if __name__ == '__main__':
    socketio.run(app, debug=True)
