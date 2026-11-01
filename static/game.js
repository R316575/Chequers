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
                
                const codeHeader = document.getElementById('display-code');
                if (codeHeader) {
                    codeHeader.innerText = roomCode;
                }
                
                renderBoard(data.board);
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
    const createBtn = document.getElementById('btn-create');
    if (createBtn) {
        createBtn.addEventListener('click', () => {
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
                
                startGameStatePolling();
            })
            .catch(err => {
                console.error("Create room error:", err);
                showAlert("Connection Error", "Could not create room.");
            });
        });
    }

    const joinBtn = document.getElementById('btn-join');
    if (joinBtn) {
        joinBtn.addEventListener('click', () => {
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
                roomCode = code;
                myColor = data.color;
                
                document.getElementById('lobby-modal').classList.add('hidden');
                document.getElementById('game-container').classList.remove('hidden');
                
                renderBoard(boardState);
                startGameStatePolling();
            })
            .catch(err => {
                console.error("Join room error:", err);
                showAlert("Lobby Join Error", err.message);
            });
        });
    }
}

// 5. CHEQUERS RENDERING ENGINE
function renderBoard(board) {
    boardState = board;
    const boardDiv = document.getElementById('checkers-board');
    if (!boardDiv) return;
    boardDiv.innerHTML = '';
    
    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            const tile = document.createElement('div');
            tile.className = (r + c) % 2 === 0 ? 'cream-tile' : 'green-tile';
            tile.dataset.row = r;
            tile.dataset.col = c;

            const val = board[r] ? board[r][c] : " ";
            if (val && val !== " ") {
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

    if (selectedTile && document.getElementById('hints-toggle') && document.getElementById('hints-toggle').checked) {
        calculateHints(selectedTile.r, selectedTile.c);
    }
}

// 6. MOVE DISPATCH MECHANISM
function handleTileClick(r, c) {
    if (boardState[r] && boardState[r][c] !== " " && boardState[r][c].toUpperCase() === myColor) {
        document.querySelectorAll('.selected-piece').forEach(el => el.classList.remove('selected-piece'));
        document.querySelectorAll('.hint-highlight').forEach(el => el.classList.remove('hint-highlight'));
        
        selectedTile = { r, c };
        const pieceEl = document.querySelector(`[data-row="${r}"][data-col="${c}"] .piece`);
        if (pieceEl) pieceEl.classList.add('selected-piece');
        if (document.getElementById('hints-toggle') && document.getElementById('hints-toggle').checked) calculateHints(r, c);
    } else if (selectedTile !== null) {
        fetch('/api/make_move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ room_code: roomCode, color: myColor, r: selectedTile.r, c: selectedTile.c, nr: r, nc: c })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) showAlert("Move Validation Warning", data.error);
            selectedTile = null;
        })
        .catch(err => console.error("Move error:", err));
    }
}

function calculateHints(r, c) {
    if (!boardState[r] || !boardState[r][c]) return;
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

function updateCaptureZones(rScore, wScore) {
    const redZone = document.getElementById('captured-by-red');
    const whiteZone = document.getElementById('captured-by-white');
    
    if (redZone) {
        redZone.innerHTML = '';
        for (let i = 0; i < rScore; i++) {
            redZone.innerHTML += '<span style="display:inline-block; width:16px; height:16px; background:#ffffff; border:1px solid #a8a8a8; border-radius:50%; margin:2px;"></span>';
        }
    }
    
    if (whiteZone) {
        whiteZone.innerHTML = '';
        for (let i = 0; i < wScore; i++) {
            whiteZone.innerHTML += '<span style="display:inline-block; width:16px; height:16px; background:#b01b1b; border:1px solid #540606; border-radius:50%; margin:2px;"></span>';
        }
    }
}

function showAlert(title, text) {
    const overlay = document.getElementById('alert-overlay');
    const titleEl = document.getElementById('alert-title');
    const textEl = document.getElementById('alert-text');
    if (overlay && titleEl && textEl) {
        titleEl.innerText = title;
        textEl.innerText = text;
        overlay.classList.remove('hidden');
    }
}
