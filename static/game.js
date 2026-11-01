// 1. GLOBAL VARIABLES & STATE
let roomCode = null;
let myColor = null;
let selectedTile = null;
let boardState = [];
let pollingInterval = null;

// 2. INITIALIZATION
document.addEventListener("DOMContentLoaded", () => {
    setupUserInterface();
});

// 3. AUTOMATIC SYNC POLLING LOOP
function startGameStatePolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    
    // Check the server every 1500 milliseconds for changes
    pollingInterval = setInterval(() => {
        if (!roomCode) return;
        
        fetch(`/api/get_game_state?room_code=${roomCode}`)
        .then(response => {
            if (!response.ok) throw new Error("Sync failed");
            return response.json();
        })
        .then(data => {
            // If the opponent joined, clear any waiting popups and uncover the board layout
            if (data.started) {
                document.getElementById('alert-overlay').classList.add('hidden');
                document.getElementById('lobby-modal').classList.add('hidden');
                document.getElementById('game-container').classList.remove('hidden');
                
                document.getElementById('user-lbl').innerText = `You: ${myColor === 'R' ? data.r_name : data.w_name} (${myColor})`;
                document.getElementById('opponent-lbl').innerText = `Opponent: ${myColor === 'R' ? data.w_name : data.r_name} (${myColor === 'R' ? 'W' : 'R'})`;
                
                document.getElementById('turn-indicator').innerText = `Turn: ${data.turn === 'R' ? 'Red' : 'White'}`;
                renderBoard(data.board);
                
                if (data.winner) {
                    showAlert("Game Over!", `${data.winner} Wins the match!`);
                    clearInterval(pollingInterval);
                }
            }
        })
        .catch(err => console.error("Sync error logs:", err));
    }, 1500);
}

// 4. BUTTON CLICK HANDLERS
function setupUserInterface() {
    // Create Room
    document.getElementById('btn-create').addEventListener('click', () => {
        const user = document.getElementById('username-input').value || "Player 1";
        
        fetch('/api/create_room', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user })
        })
        .then(response => response.json())
        .then(data => {
            roomCode = data.room_code;
            myColor = data.color;
            document.getElementById('display-code').innerText = roomCode;
            showAlert("Room Created", `Share Code: ${roomCode}. Waiting for your opponent.`);
            
            // Instantly start checking for the second player
            startGameStatePolling();
        })
        .catch(err => showAlert("Connection Error", "Could not create room."));
    });

    // Join Room
    document.getElementById('btn-join').addEventListener('click', () => {
        const user = document.getElementById('username-input').value || "Player 2";
        const code = document.getElementById('join-code-input').value.toUpperCase();
        
        fetch('/api/join_room', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: user, room_code: code })
        })
        .then(response => {
            if (!response.ok) return response.json().then(err => { throw new Error(err.error); });
            return response.json();
        })
        .then(data => {
            roomCode = data.room_code;
            myColor = data.color;
            
            document.getElementById('lobby-modal').classList.add('hidden');
            document.getElementById('game-container').classList.remove('hidden');
            
            // Instantly start polling to track piece moves made by the opponent
            startGameStatePolling();
        })
        .catch(err => showAlert("Lobby Join Error", err.message));
    });
}

// 5. CHEQUERS RENDERING ENGINE (With state-preserving highlights)
function renderBoard(board) {
    boardState = board;
    const boardDiv = document.getElementById('checkers-board');
    boardDiv.innerHTML = '';
    
    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            const tile = document.createElement('div');
            tile.className = (r + c) % 2 === 0 ? 'cream-tile' : 'green-tile';
            tile.dataset.row = r;
            tile.dataset.col = c;

            const val = board[r][c];
            if (val !== " ") {
                const p = document.createElement('div');
                p.className = `piece ${val.toUpperCase() === 'R' ? 'red-p' : 'white-p'}`;
                if (val === "R" || val === "W") p.innerHTML = "&#x2654;";
                
                // RESTORE SELECTION CLASS: If this piece was previously selected, keep it lit
                if (selectedTile && selectedTile.r === r && selectedTile.c === c) {
                    p.classList.add('selected-piece');
                }
                
                tile.appendChild(p);
            }

            tile.addEventListener('click', () => handleTileClick(r, c));
            boardDiv.appendChild(tile);
        }
    }

    // RESTORE HINT HIGHLIGHTS: If a piece is selected and hints are enabled, re-calculate them instantly
    if (selectedTile && document.getElementById('hints-toggle').checked) {
        calculateHints(selectedTile.r, selectedTile.c);
    }
}

// 6. MOVE DISPATCH MECHANISM
function handleTileClick(r, c) {
    if (boardState[r] && boardState[r][c] !== " " && boardState[r][c].toUpperCase() === myColor) {
        // Clear previous selections
        document.querySelectorAll('.selected-piece').forEach(el => el.classList.remove('selected-piece'));
        document.querySelectorAll('.hint-highlight').forEach(el => el.classList.remove('hint-highlight'));
        
        selectedTile = { r, c };
        const pieceEl = document.querySelector(`[data-row="${r}"][data-col="${c}"] .piece`);
        if (pieceEl) pieceEl.classList.add('selected-piece');
        if (document.getElementById('hints-toggle').checked) calculateHints(r, c);
    } else if (selectedTile !== null) {
        // Submit move directly via a clean HTTP route instead of WebSocket emits
        fetch('/api/make_move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ room_code: roomCode, color: myColor, r: selectedTile.r, c: selectedTile.c, nr: r, nc: c })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) showAlert("Move Validation Warning", data.error);
            selectedTile = null;
        });
    }
}

function calculateHints(r, c) {
    const isKing = boardState[r][c] === boardState[r][c].toUpperCase();
    const directions = isKing ? [[-1,-1],[-1,1],[1,-1],[1,1]] : (myColor === 'R' ? [[-1,-1],[-1,1]] : [[1,-1],[1,1]]);
    directions.forEach(([dr, dc]) => {
        let nr = r + dr, nc = c + dc;
        if (0 <= nr && nr < 8 && 0 <= nc && nc < 8 && boardState[nr][nc] === " ") {
            const targetedTile = document.querySelector(`[data-row="${nr}"][data-col="${nc}"]`);
            if (targetedTile) targetedTile.classList.add('hint-highlight');
        }
    });
}

function showAlert(title, text) {
    document.getElementById('alert-title').innerText = title;
    document.getElementById('alert-text').innerText = text;
    document.getElementById('alert-overlay').classList.remove('hidden');
}
