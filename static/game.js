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
            renderBoard(data.board);
            updateCaptureZones(data.r_score || 0, data.w_score || 0);
            document.getElementById('turn-indicator').innerText = `Turn: ${data.turn === 'R' ? 'Red' : 'White'}`;
            
            const codeHeader = document.getElementById('display-code');
            if (codeHeader) { codeHeader.innerText = roomCode; }

            if (data.started) {
                document.getElementById('alert-overlay').classList.add('hidden');
                document.getElementById('lobby-modal').classList.add('hidden');
                document.getElementById('game-container').classList.remove('hidden');
                
                document.getElementById('user-lbl').innerText = `You: ${myColor === 'R' ? data.r_name : data.w_name} (${myColor})`;
                document.getElementById('opponent-lbl').innerText = `Opponent: ${myColor === 'R' ? data.w_name : data.r_name} (${myColor === 'R' ? 'W' : 'R'})`;
                
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
            .catch(err => showAlert("Connection Error", "Could not create room."));
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
                startGameStatePolling();
            })
            .catch(err => showAlert("Lobby Join Error", err.message));
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
        
        if (document.getElementById('hints-toggle') && document.getElementById('hints-toggle').checked) {
            calculateHints(r, c);
        }
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
            document.querySelectorAll('.hint-highlight').forEach(el => el.classList.remove('hint-highlight'));
            document.querySelectorAll('.selected-piece').forEach(el => el.classList.remove('selected-piece'));
        });
    }
}

// 7. COMPREHENSIVE HINT & FORCED CAPTURE COMPUTATION ENGINE
function findAllAvailableJumps() {
    let availableJumps = [];
    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            const piece = boardState[r] ? boardState[r][c] : " ";
            if (piece !== " " && piece.toUpperCase() === myColor) {
                const isKing = piece === piece.toUpperCase();
                const directions = isKing ? [[-1,-1],[-1,1],[1,-1],[1,1]] : (myColor === 'R' ? [[-1,-1],[-1,1]] : [[1,-1],[1,1]]);
                
                directions.forEach(([dr, dc]) => {
                    const opponentRow = r + dr;
                    const opponentCol = c + dc;
                    const landingRow = r + (dr * 2);
                    const landingCol = c + (dc * 2);
                    
                    if (landingRow >= 0 && landingRow < 8 && landingCol >= 0 && landingCol < 8) {
                        const targetPiece = boardState[opponentRow][opponentCol];
                        const landingSquare = boardState[landingRow][landingCol];
                        
                        if (targetPiece !== " " && targetPiece.toUpperCase() !== myColor && landingSquare === " ") {
                            availableJumps.push({
                                from: { r, c },
                                to: { r: landingRow, c: landingCol }
                            });
                        }
                    }
                });
            }
        }
    }
    return availableJumps;
}

function calculateHints(r, c) {
    if (!boardState[r] || !boardState[r][c]) return;
    document.querySelectorAll('.hint-highlight').forEach(el => el.classList.remove('hint-highlight'));

    const allBoardJumps = findAllAvailableJumps();
    if (allBoardJumps.length > 0) {
        const specificPieceJumps = allBoardJumps.filter(jump => jump.from.r === r && jump.from.c === c);
        specificPieceJumps.forEach(jump => {
            const targetedTile = document.querySelector(`[data-row="${jump.to.r}"][data-col="${jump.to.c}"]`);
            if (targetedTile) targetedTile.classList.add('hint-highlight');
        });
        return; 
    }

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
    
    // Clear zones cleanly to handle fresh states
    if (redZone) redZone.innerHTML = '';
    if (whiteZone) whiteZone.innerHTML = '';

    // Determine perspective-based styling for the miniatures
    const miniatureWhitePiece = '<span style="display:inline-block; width:12px; height:12px; background:#ffffff; border:1px solid #a8a8a8; border-radius:50%; margin:2px; box-shadow: 1px 1px 3px rgba(0,0,0,0.2);"></span>';
    const miniatureRedPiece = '<span style="display:inline-block; width:12px; height:12px; background:#b01b1b; border:1px solid #540606; border-radius:50%; margin:2px; box-shadow: 1px 1px 3px rgba(0,0,0,0.2);"></span>';

    if (myColor === 'R') {
        // Red Player Perspective:
        // 'captured-by-red' is YOUR zone -> should display the miniature WHITE pieces you won.
        if (redZone) {
            for (let i = 0; i < rScore; i++) {
                redZone.innerHTML += miniatureWhitePiece;
            }
        }
        // 'captured-by-white' is OPPONENT'S zone -> should display the miniature RED pieces they won from you.
        if (whiteZone) {
            for (let i = 0; i < wScore; i++) {
                whiteZone.innerHTML += miniatureRedPiece;
            }
        }
    } else {
        // White Player Perspective (Opposite Layout mapping):
        // 'captured-by-white' is YOUR zone -> should display the miniature RED pieces you won.
        if (whiteZone) {
            for (let i = 0; i < wScore; i++) {
                whiteZone.innerHTML += miniatureRedPiece;
            }
        }
        // 'captured-by-red' is OPPONENT'S zone -> should display the miniature WHITE pieces they won from you.
        if (redZone) {
            for (let i = 0; i < rScore; i++) {
                redZone.innerHTML += miniatureWhitePiece;
            }
        }
    }
}
// Global Custom Alert Dialogue Engine
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
