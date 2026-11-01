// 1. GLOBAL VARIABLES & STATE
let socket;
let roomCode = null;
let myColor = null;
let selectedTile = null;
let boardState = [];

// 2. INITIALIZATION
document.addEventListener("DOMContentLoaded", () => {
    socket = io();
    setupSocketListeners();
    setupUserInterface();
});

// 3. NETWORK LISTENERS
function setupSocketListeners() {
    socket.on('room_created', (data) => {
        roomCode = data.room_code;
        myColor = data.color;
        document.getElementById('display-code').innerText = roomCode;
        showAlert("Room Created", `Share Code: ${roomCode}. Waiting for your opponent.`);
    });

    socket.on('game_ready', (data) => {
        console.log("Global game packet detected:", data);
        
        // Match filtering check: Only trigger layout change if this notification matches our active room
        if (data.room_code === roomCode) {
            console.log("Match verified! Synchronizing board screens...");
            
            // Close the alert popup notice if it's currently blocking the interface view
            document.getElementById('alert-overlay').classList.add('hidden');
            
            // Swap display states to uncover the board layout
            document.getElementById('lobby-modal').classList.add('hidden');
            document.getElementById('game-container').classList.remove('hidden');
            
            // Set user metrics
            document.getElementById('user-lbl').innerText = `You: ${myColor === 'R' ? data.r_name : data.w_name} (${myColor})`;
            document.getElementById('opponent-lbl').innerText = `Opponent: ${myColor === 'R' ? data.w_name : data.r_name} (${myColor === 'R' ? 'W' : 'R'})`;
            renderBoard(data.board);
        }
    });

    socket.on('update_board', (data) => {
        renderBoard(data.board);
        document.getElementById('turn-indicator').innerText = `Turn: ${data.turn === 'R' ? 'Red' : 'White'}`;
        if (data.winner) showAlert("Game Over!", `${data.winner} Wins the match!`);
    });

    socket.on('error_msg', (msg) => showAlert("Move Validation Error", msg));
    socket.on('connection_lost', () => showAlert("Connection Dropped", "Opponent disconnected. Room will terminate in 30s."));
}

// 4. BUTTON CLICK HANDLERS
function setupUserInterface() {
    const createBtn = document.getElementById('btn-create');
    console.log("Checking create button element:", createBtn);

    if (createBtn) {
        createBtn.addEventListener('click', () => {
            console.log("Create Private Room button successfully clicked!");
            const user = document.getElementById('username-input').value || "Player 1";
            
            fetch('/api/create_room', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: user })
            })
            .then(response => {
                console.log("Server responded with HTTP status:", response.status);
                return response.json();
            })
            .then(data => {
                console.log("Room payload received from API:", data);
                roomCode = data.room_code;
                myColor = data.color;
                document.getElementById('display-code').innerText = roomCode;
                showAlert("Room Created", `Share Code: ${roomCode}. Waiting for your opponent.`);
                
                socket.emit('join_game', { username: user, room_code: roomCode });
            })
            .catch(err => {
                console.error("Server API mismatch error logs:", err);
                showAlert("Connection Error", "Could not create a private room on the server.");
            });
        });
    }

    const joinBtn = document.getElementById('btn-join');
    if (joinBtn) {
        joinBtn.addEventListener('click', () => {
            const user = document.getElementById('username-input').value || "Player 2";
            const code = document.getElementById('join-code-input').value.toUpperCase();
            console.log(`Attempting to join room: ${code} via HTTP API as user: ${user}`);
            
            fetch('/api/join_room', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: user, room_code: code })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw new Error(err.error); });
                }
                return response.json();
            })
            .then(data => {
                console.log("Successfully joined room! Payload:", data);
                roomCode = data.room_code;
                myColor = data.color;
                
                document.getElementById('lobby-modal').classList.add('hidden');
                document.getElementById('game-container').classList.remove('hidden');
                
                document.getElementById('user-lbl').innerText = `You: ${data.w_name} (W)`;
                document.getElementById('opponent-lbl').innerText = `Opponent: ${data.r_name} (R)`;
                renderBoard(data.board);
            })
            .catch(err => {
                console.error("Join room error:", err);
                showAlert("Lobby Join Error", err.message || "Could not connect to the match room.");
            });
        });
    }
}

// 5. CHEQUERS RENDERING ENGINE
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
                tile.appendChild(p);
            }

            tile.addEventListener('click', () => handleTileClick(r, c));
            boardDiv.appendChild(tile);
        }
    }
}

// 6. PIECE MOVEMENT SELECTION MATRIX
function handleTileClick(r, c) {
    const clickedVal = boardState[r][c];
    
    if (selectedTile === null) {
        if (clickedVal !== " " && clickedVal.toUpperCase() === myColor) {
            selectedTile = { r, c };
            document.querySelector(`[data-row="${r}"][data-col="${c}"] .piece`).classList.add('selected-piece');
            if (document.getElementById('hints-toggle').checked) calculateHints(r, c);
        }
    } else {
        socket.emit('make_move', {
            room_code: roomCode,
            r: selectedTile.r, c: selectedTile.c,
            nr: r, nc: c
        });
        selectedTile = null;
        renderBoard(boardState); 
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
