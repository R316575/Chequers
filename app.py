from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit, join_room
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ==========================================
#         YOUR CORRECTED GAME LOGIC
# ==========================================

class multiplayer:
    def __init__(self):
        self.active_games = []

class game:
    def __init__(self):
        self.game_code = "game_code"
        self.current_turn = "R"
        self.player1 = "R" 
        self.player2 = "W" 
        self.players = [self.player1, self.player2]
        self.board = board()

    def start_game(self):
        self.board.initialise_board()

    def switch_turn(self):
        if self.current_turn == "R":
            self.current_turn = "W"
        else:
            self.current_turn = "R"

    def check_winner(self):
        # Fixed: Checking instance values instead of static class variables
        if self.board.w_score == 12:
            return "White wins"
        elif self.board.r_score == 12:
            return "Red wins"
        return None

    def check_no_possible_moves_white(self):
        # Your exact logic preserved, updated to reference self.board
        for col in range(2,6):
           for row in range(0,6):
                if self.board.board[row][col] in "Ww":
                    if self.board.board[row+1][col+1] in "Rr" and self.board.board[row+2][col+2] == " ": return False
                    if self.board.board[row+1][col-1] in "Rr" and self.board.board[row+2][col-2] == " ": return False
        # ... (keeping your checking boundaries)
        for col in range(1,7):
            for row in range(0,7):
                if self.board.board[row][col] in "Ww" and (self.board.board[row+1][col+1] == " " or self.board.board[row+1][col-1] == " "): return False
        return True # White is blocked

    def check_no_possible_moves_red(self):
        # Your exact logic preserved, updated to reference self.board
        for col in range(2,6):
            for row in range(2,8):
                if self.board.board[row][col] in "Rr":
                    if self.board.board[row-1][col+1] in "Ww" and self.board.board[row-2][col-2] == " ": return False
                    if self.board.board[row-1][col-1] in "Ww" and self.board.board[row-2][col-2] == " ": return False
        return True # Red is blocked

class board:
    def __init__(self):
        self.board = []
        self.w_score = 0  
        self.r_score = 0  

    def initialise_board(self):
        self.board = [[" " for _ in range(8)] for _ in range(8)]
        for x in range(8):
            if (x % 2) == 0:  
                if x < 3:  
                    self.board[x][1] = "w"; self.board[x][3] = "w"; self.board[x][5] = "w"; self.board[x][7] = "w"
                elif x > 4:  
                    self.board[x][1] = "r"; self.board[x][3] = "r"; self.board[x][5] = "r"; self.board[x][7] = "r"
            else:  
                if x < 3:  
                    self.board[x][0] = "w"; self.board[x][2] = "w"; self.board[x][4] = "w"; self.board[x][6] = "w"
                elif x > 4:  
                    self.board[x][0] = "r"; self.board[x][2] = "r"; self.board[x][4] = "r"; self.board[x][6] = "r"

    def move_piece(self, r, c, nr, nc, player, game_instance):
        if self.board[r][c] == " ": return False, "There is no piece here."
        if self.board[r][c] not in "Rr" and player == "R": return False, "That is not your piece."
        if self.board[r][c] not in "Ww" and player == "W": return False, "That is not your piece."
        if self.board[nr][nc] != " ": return False, "The target position is occupied."
        
        # Simple movement engine based on your rules script
        # Validates regular piece forward diagonal movement
        if player == "R" and self.board[r][c] == "r":
            if (r - nr == 1) and (abs(nc - c) == 1):
                self.board[nr][nc] = "r"
                self.board[r][c] = " "
                if nr == 0: self.board[nr][nc] = "R" # King promotion
                return True, "Success"
            # Capture logic
            if (r - nr == 2) and (abs(nc - c) == 2):
                mid_r, mid_c = (r + nr) // 2, (c + nc) // 2
                if self.board[mid_r][mid_c] in "Ww":
                    self.board[nr][nc] = "r"
                    self.board[r][c] = " "
                    self.board[mid_r][mid_c] = " "
                    self.r_score += 1
                    if nr == 0: self.board[nr][nc] = "R"
                    return True, "Success"
                    
        if player == "W" and self.board[r][c] == "w":
            if (nr - r == 1) and (abs(nc - c) == 1):
                self.board[nr][nc] = "w"
                self.board[r][c] = " "
                if nr == 7: self.board[nr][nc] = "W" # King promotion
                return True, "Success"
            # Capture logic
            if (nr - r == 2) and (abs(nc - c) == 2):
                mid_r, mid_c = (r + nr) // 2, (c + nc) // 2
                if self.board[mid_r][mid_c] in "Rr":
                    self.board[nr][nc] = "w"
                    self.board[r][c] = " "
                    self.board[mid_r][mid_c] = " "
                    self.w_score += 1
                    if nr == 7: self.board[nr][nc] = "W"
                    return True, "Success"

        return False, "Invalid movement alignment."

# ==========================================
#        NETWORKING AND MATCHMAKING
# ==========================================

ACTIVE_GAMES = {}

@app.route('/')
def home():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Online Multiplayer Chequers</title>
    <script src="/socket.io/socket.io.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e24; color: #fff; text-align: center; padding: 20px; }
        .setup-box { background: #2a2a35; padding: 20px; max-width: 400px; margin: 40px auto; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
        input, select, button { width: 90%; padding: 10px; margin: 10px 0; border: none; border-radius: 4px; font-size: 16px; }
        button { background-color: #4CAF50; color: white; font-weight: bold; cursor: pointer; }
        button:hover { background-color: #45a049; }
        #game-container { display: none; margin-top: 20px; }
        #board-display { font-family: monospace; background: #000; padding: 15px; border-radius: 6px; display: inline-block; white-space: pre; font-size: 20px; line-height: 1.2; text-align: left; border: 3px solid #444; }
        .status { margin: 15px; font-size: 18px; font-weight: bold; color: #00E676; }
    </style>
</head>
<body>

    <h1>🏆 Online Chequers 🏆</h1>

    <div id="setup-panel" class="setup-box">
        <h3>Match Setup</h3>
        <input type="text" id="gameCode" placeholder="Enter Match Room Code">
        <select id="playerColor">
            <option value="R">Play as Red (R)</option>
            <option value="W">Play as White (W)</option>
        </select>
        <button onclick="connectToMatch()">Join Game Room</button>
        <p id="conn-status" style="color: #FFA726;"></p>
    </div>

    <div id="game-container">
        <div class="status" id="turn-indicator">Waiting for move...</div>
        <div id="board-display">Loading board layout...</div>
        
        <div class="setup-box" style="margin-top: 20px;">
            <h4>Submit a Move</h4>
            <input type="text" id="currentPos" placeholder="Current Piece (e.g. B3)" maxlength="2">
            <input type="text" id="targetPos" placeholder="Target Slot (e.g. A4)" maxlength="2">
            <button onclick="sendMove()">Send Move Over Internet</button>
        </div>
    </div>

<script>
    let socket;
    let myColor = "R";
    let activeRoom = "";

    function connectToMatch() {
        const room = document.getElementById('gameCode').value.trim();
        myColor = document.getElementById('playerColor').value;
        activeRoom = room;

        if(!room) { alert("Please enter a room code!"); return; }
        document.getElementById('conn-status').innerText = "Connecting...";

        socket = io();

        socket.on('connect', function() {
            document.getElementById('setup-panel').style.display = 'none';
            document.getElementById('game-container').style.display = 'block';
            socket.emit('join_match', { game_code: activeRoom });
        });

        socket.on('board_update', function(data) {
            document.getElementById('turn-indicator').innerText = "Current Turn: " + data.turn + (data.turn === myColor ? ' (YOUR TURN)' : ' (Waiting for opponent)');
            let boardText = "   A B C D E F G H\\n";
            data.board.forEach(function(row, index) {
                boardText += (8 - index) + "  " + row.join(' ') + "\\n";
            });
            document.getElementById('board-display').innerText = boardText;
        });

        socket.on('error_message', function(data) { alert("Error: " + data.message); });
        socket.on('game_over', function(data) { alert("Game Over! " + data.message); });
    }

    function sendMove() {
        const pos = document.getElementById('currentPos').value.toUpperCase().trim();
        const newPos = document.getElementById('targetPos').value.toUpperCase().trim();
        
        if(pos.length !== 2 || newPos.length !== 2) { alert("Use format like B3 and A4!"); return; }

        const columns = "ABCDEFGH";
        const c = columns.indexOf(pos[0]);
        const r = 8 - parseInt(pos[1]);
        const nc = columns.indexOf(newPos[0]);
        const nr = 8 - parseInt(newPos[1]);

        if (isNaN(r) || isNaN(nr) || c === -1 || nc === -1) { alert("Invalid Coordinates!"); return; }

        socket.emit('submit_move', {
            game_code: activeRoom,
            player_color: myColor,
            r: r, c: c, nr: nr, nc: nc
        });

        document.getElementById('currentPos').value = "";
        document.getElementById('targetPos').value = "";
    }
</script>
</body>
</html>
    ''')

# ==========================================
#        NETWORKING NET HANDSHAKES
# ==========================================

ACTIVE_GAMES = {}

@socketio.on('join_match')
def on_join(data):
    room = data['game_code']
    join_room(room)
    if room not in ACTIVE_GAMES:
        ACTIVE_GAMES[room] = game()
        ACTIVE_GAMES[room].start_game()
    
    current_game = ACTIVE_GAMES[room]
    emit('board_update', {
        'board': current_game.board.board, 
        'turn': current_game.current_turn
    })

@socketio.on('submit_move')
def on_move(data):
    room = data['game_code']
    player_color = data['player_color']
    current_game = ACTIVE_GAMES.get(room)
    
    if not current_game: return
    if current_game.current_turn != player_color:
        emit('error_message', {'message': "It is not your turn yet!"})
        return

    # This routes into your original move piece logic
    success = current_game.board.move_piece(data['r'], data['c'], data['nr'], data['nc'], player_color)
    
    if success:
        current_game.switch_turn()
        emit('board_update', {
            'board': current_game.board.board, 
            'turn': current_game.current_turn
        }, to=room)
    else:
        emit('error_message', {'message': "Invalid move alignment!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)

@socketio.on('join_match')
def on_join(data):
    room = data['game_code']
    join_room(room)
    if room not in ACTIVE_GAMES:
        ACTIVE_GAMES[room] = game()
        ACTIVE_GAMES[room].start_game()
    
    current_game = ACTIVE_GAMES[room]
    emit('board_update', {
        'board': current_game.board.board, 
        'turn': current_game.current_turn,
        'r_score': current_game.board.r_score,
        'w_score': current_game.board.w_score
    })

@socketio.on('submit_move')
def on_move(data):
    room = data['game_code']
    player_color = data['player_color']
    current_game = ACTIVE_GAMES.get(room)
    
    if not current_game: return
    if current_game.current_turn != player_color:
        emit('error_message', {'message': "It is not your turn yet!"})
        return

    success, msg = current_game.board.move_piece(data['r'], data['c'], data['nr'], data['nc'], player_color, current_game)
    
    if success:
        winner = current_game.check_winner()
        if winner:
            emit('game_over', {'message': winner}, to=room)
            return
        
        current_game.switch_turn()
        emit('board_update', {
            'board': current_game.board.board, 
            'turn': current_game.current_turn,
            'r_score': current_game.board.r_score,
            'w_score': current_game.board.w_score
        }, to=room)
    else:
        emit('error_message', {'message': msg})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
