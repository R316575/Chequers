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
    
    pollingInterval = setInterval(() => {
        if (!roomCode) return;
        
        fetch(`/api/get_game_state?room_code=${roomCode}`)
        .then(response => {
            if (!response.ok) throw new Error("Sync failed");
            return response.json();
        })
        .then(data => {
            if (data.started) {
                document.getElementById('alert-overlay').classList.add('hidden');
                document.getElementById('lobby-modal').classList.add('hidden');
                document.getElementById('game-container').classList.remove('hidden');
                
                document.getElementById('user-lbl').innerText = `You: ${myColor === 'R' ? data.r_name : data.w_name} (${myColor})`;
                document.getElementById('opponent-lbl').innerText = `Opponent: ${myColor === 'R' ? data.w_name : data.r_name} (${myColor === 'R' ? 'W' : 'R'})`;
                
                document.getElementById('turn-indicator').innerText = `Turn: ${data.turn === 'R' ? 'Red' : 'White'}`;
                
                // 1. Render the main 8x8 checkerboard grid layout
                renderBoard(data.board);
                
                // 2. RUN THE SIDE BAR CAPTURE HOOK: Pull scores and draw circles
                updateCaptureZones(data.r_score || 0, data.w_score || 0);
                
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

// 5. CHEQUERS RENDERING ENGINE (With state preservation and side panel capture tracking)
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
                
                if (selectedTile && selectedTile.r === r && selectedTile.c === c) {
                    p.classList.add('selected-piece');
                }
                
                tile.appendChild(p);
            }

            tile.addEventListener('click', () => handleTileClick(r, c));
            boardDiv.appendChild(tile);
        }
    }

    if (selectedTile && document.getElementById('hints-toggle').checked) {
        calculateHints(selectedTile.r, selectedTile.c);
    }
}

// NEW SIDE PANEL TRACKING FUNCTION: Renders circles representing captured game pieces
function updateCaptureZones(rScore, wScore) {
    const redZone = document.getElementById('captured-by-red');
    const whiteZone = document.getElementById('captured-by-white');
    
    if (redZone) {
        // Red score tracking counts how many White counters Red has jumped
        redZone.innerHTML = '';
        for (let i = 0; i < rScore; i++) {
            redZone.innerHTML += '<span style="display:inline-block; width:16px; height:16px; background:#ffffff; border:1px solid #a8a8a8; border-radius:50%; margin:2px;"></span>';
        }
    }
    
    if (whiteZone) {
        // White score tracking counts how many Red counters White has jumped
        whiteZone.innerHTML = '';
        for (let i = 0; i < wScore; i++) {
            whiteZone.innerHTML += '<span style="display:inline-block; width:16px; height:16px; background:#b01b1b; border:1px solid #540606; border-radius:50%; margin:2px;"></span>';
        }
    }
}

function updateCaptureZones(rScore, wScore) {
    // Select the physical UI zones: top panel vs. bottom panel on the current screen
    const topZone = document.getElementById('captured-by-white'); // Label references top panel location
    const bottomZone = document.getElementById('captured-by-red'); // Label references bottom panel location
    
    if (!topZone || !bottomZone) return;
    
    // Clear out both containers before redrawing
    topZone.innerHTML = '';
    bottomZone.innerHTML = '';
    
    // ADAPTIVE LAYOUT MATRIX RULES:
    if (myColor === 'R') {
        // --- SCREEN VIEW FOR PETE (RED PLAYER) ---
        // Top Zone (Opponent): Displays White pieces that Red has captured? No, displays Red pieces captured by White.
        // Let's make it intuitive: The person sitting at the bottom sees their own trophy captures at the bottom.
        
        // Bottom Zone (Pete's captures): Pete has captured White pieces.
        for (let i = 0; i < rScore; i++) {
            bottomZone.innerHTML += '<span style="display:inline-block; width:16px; height:16px; background:#ffffff; border:1px solid #a8a8a8; border-radius:50%; margin:2px;"></span>';
        }
        // Top Zone (Pat's captures): Pat has captured Red pieces.
        for (let i = 0; i < wScore; i++) {
            topZone.innerHTML += '<span style="display:inline-block; width:16px; height:16px; background:#b01b1b; border:1px solid #540606; border-radius:50%; margin:2px;"></span>';
        }
    } else {
        // --- SCREEN VIEW FOR PAT (WHITE PLAYER) ---
        // For White's window, positions must be inverted! White sits at the bottom now.
        
        // Bottom Zone (Pat's captures): Pat has captured Red pieces.
        for (let i = 0; i < wScore; i++) {
            bottomZone.innerHTML += '<span style="display:inline-block; width:16px; height:16px; background:#b01b1b; border:1px solid #540606; border-radius:50%; margin:2px;"></span>';
        }
        // Top Zone (Pete's captures): Pete has captured White pieces.
        for (let i = 0; i < rScore; i++) {
            topZone.innerHTML += '<span style="display:inline-block; width:16px; height:16px; background:#ffffff; border:1px solid #a8a8a8; border-radius:50%; margin:2px;"></span>';
        }
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
