// 1. GLOBAL VARIABLES & STATE
let roomCode = null;
let myColor = null;
let selectedTile = null;
let boardState = [];
let pollingInterval = null;
let lastSeenEventId = 0;

// 2. INITIALIZATION
document.addEventListener("DOMContentLoaded", () => {
    setupUserInterface();
});

// 3. AUTOMATIC SYNC POLLING LOOP
function startGameStatePolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    
    pollingInterval = setInterval(() => {
        if (!roomCode) return;
        
        fetch(`/api/get_game_state?room_code=${roomCode}&color=${myColor || ''}`)
        .then(response => {
            if (!response.ok) throw new Error("Sync failed");
            return response.json();
        })
        .then(data => {
            updateSelfOfflineBanner(false);
            renderBoard(data.board);
            updateCaptureZones(data.r_score || 0, data.w_score || 0);
            document.getElementById('turn-indicator').innerText = `Turn: ${data.turn === 'R' ? 'Red' : 'White'}`;
            
            const codeHeader = document.getElementById('display-code');
            if (codeHeader) { codeHeader.innerText = roomCode; }

             if (data.started) {
                const lobby = document.getElementById('lobby-modal');
                if (lobby && !lobby.classList.contains('hidden')) {
                    document.getElementById('alert-overlay').classList.add('hidden');
                    lobby.classList.add('hidden');
                    document.getElementById('game-container').classList.remove('hidden');
                }
                
                // Top label ('opponent-lbl' position) always matches the White pieces at the top
                const topLabel = document.getElementById('opponent-lbl');
                topLabel.innerText = `${myColor === 'W' ? 'You' : 'Opponent'}: ${data.w_name} (White)`;
                topLabel.classList.toggle('active-turn', data.turn === 'W');

                // Bottom label ('user-lbl' position) always matches the Red pieces at the bottom
                const bottomLabel = document.getElementById('user-lbl');
                bottomLabel.innerText = `${myColor === 'R' ? 'You' : 'Opponent'}: ${data.r_name} (Red)`;
                bottomLabel.classList.toggle('active-turn', data.turn === 'R');

                // ADD THESE 4 LINES:
                if (data.event_id && data.event_id > lastSeenEventId) {
                    lastSeenEventId = data.event_id;
                    showEventToast(data.last_event);
                }

                updateDisconnectBanner(data.disconnected_name, data.disconnect_remaining);

                if (data.winner) {
                    updateDisconnectBanner(null, null);
                    const winMsg = data.winner.startsWith("Draw")
                        ? data.winner
                        : `${data.winner} Wins the Match!${data.forfeited ? ' (Opponent Forfeited)' : ''}`;
                    showAlert("Game Over!", winMsg);
                    clearInterval(pollingInterval);
                }
            }
        })
            .catch(err => {
            console.error("Sync error logs:", err);
            updateSelfOfflineBanner(true);
        });
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

// Dynamically add Quit / Forfeit button inside the game container
    const gameContainer = document.getElementById('game-container');
    if (gameContainer && !document.getElementById('btn-quit')) {
        const quitBtn = document.createElement('button');
        quitBtn.id = 'btn-quit';
        quitBtn.className = 'quit-btn';
        quitBtn.innerText = 'Quit Game';
        quitBtn.addEventListener('click', () => {
            if (!roomCode || !myColor) return;
            fetch('/api/quit_game', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ room_code: roomCode, color: myColor })
            })
            .then(res => res.json())
            .then(() => {
                const winnerName = myColor === 'R' ? 'White' : 'Red';
                showAlert("Game Over!", `${winnerName} Wins the Match! (Opponent Forfeited)`);
                clearInterval(pollingInterval);
            });
        });
        gameContainer.appendChild(quitBtn);
    }

    // Dynamically add How to Play button above the Quit button
    if (gameContainer && !document.getElementById('btn-rules')) {
        const rulesBtn = document.createElement('button');
        rulesBtn.id = 'btn-rules';
        rulesBtn.className = 'rules-btn';
        rulesBtn.innerText = 'How to Play';
        rulesBtn.addEventListener('click', showRulesModal);
        gameContainer.appendChild(rulesBtn);
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
                if (val === "R" || val === "W") p.innerHTML = '<span class="king-crown">&#x2654;</span>';
                
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
    
    // Clear zones cleanly before rendering fresh states
    if (redZone) redZone.innerHTML = '';
    if (whiteZone) whiteZone.innerHTML = '';

    // Increased size to 18px for better visibility
    const miniatureWhitePiece = '<span style="display:inline-block; width:18px; height:18px; background:#ffffff; border:2px solid #a8a8a8; border-radius:50%; margin:2px; box-shadow: 1px 1px 3px rgba(0,0,0,0.3);"></span>';
    const miniatureRedPiece = '<span style="display:inline-block; width:18px; height:18px; background:#b01b1b; border:2px solid #540606; border-radius:50%; margin:2px; box-shadow: 1px 1px 3px rgba(0,0,0,0.3);"></span>';

    if (myColor === 'R') {
        // Bottom side (Your side): Show the White pieces you captured
        if (redZone) {
            for (let i = 0; i < rScore; i++) {
                redZone.innerHTML += miniatureWhitePiece;
            }
        }
        // Top side (Opponent side): Show the Red pieces they captured from you
        if (whiteZone) {
            for (let i = 0; i < wScore; i++) {
                whiteZone.innerHTML += miniatureRedPiece;
            }
        }
    } else {
        // Bottom side (Your side): Show the Red pieces you captured
        if (redZone) {
            for (let i = 0; i < wScore; i++) {
                redZone.innerHTML += miniatureRedPiece;
            }
        }
        // Top side (Opponent side): Show the White pieces they captured from you
        if (whiteZone) {
            for (let i = 0; i < rScore; i++) {
                whiteZone.innerHTML += miniatureWhitePiece;
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


// Non-blocking pop-up banner for captures and king promotions
function showEventToast(message) {
    let toast = document.getElementById('event-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'event-toast';
        toast.className = 'event-toast';
        document.body.appendChild(toast);
    }
    toast.innerText = message;
    toast.classList.remove('hidden');

    // Automatically hide after 2.5 seconds
    clearTimeout(toast.hideTimer);
    toast.hideTimer = setTimeout(() => {
        toast.classList.add('hidden');
    }, 2500);
}

// Pop-up modal displaying Chequers / Draughts rules
function showRulesModal() {
    let overlay = document.getElementById('rules-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'rules-overlay';
        overlay.className = 'rules-overlay';
        overlay.innerHTML = `
            <div class="rules-box">
                <h2>How to Play Chequers</h2>
                <ul>
                    <li><strong>Turns:</strong> Red always moves first, followed by White.</li>
                    <li><strong>Movement:</strong> Regular pieces move diagonally forward by 1 dark square.</li>
                    <li><strong>Captures:</strong> Jump diagonally over an adjacent opponent piece into an empty square beyond it.</li>
                    <li><strong>Forced Captures:</strong> If a capture is available on your turn, you <em>must</em> take it.</li>
                    <li><strong>Kings:</strong> Reaching the far edge crowns your piece as a <strong>King (♔)</strong>, allowing it to move and capture both forwards and backwards.</li>
                    <li><strong>Winning:</strong> Win by capturing all 12 opponent pieces or blocking them from making any legal moves.</li>
                </ul>
                <button id="close-rules-btn" class="rules-close-btn">Got It</button>
            </div>
        `;
        document.body.appendChild(overlay);

        document.getElementById('close-rules-btn').addEventListener('click', () => {
            overlay.classList.add('hidden');
        });
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.classList.add('hidden');
        });
    }
    overlay.classList.remove('hidden');
}



// Non-blocking banner showing 30s reconnection timer when opponent drops
function updateDisconnectBanner(playerName, secondsLeft) {
    let banner = document.getElementById('disconnect-banner');
    if (!playerName || secondsLeft === null || secondsLeft === undefined) {
        if (banner) banner.classList.add('hidden');
        return;
    }

    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'disconnect-banner';
        banner.className = 'disconnect-banner';
        document.body.appendChild(banner);
    }

    banner.innerText = `⚠️ ${playerName}'s connection dropped. Attempting to re-establish... (${secondsLeft}s)`;
    banner.classList.remove('hidden');
}

// Local client-side banner when THIS player's own internet drops
function updateSelfOfflineBanner(isOffline) {
    let banner = document.getElementById('self-offline-banner');
    if (!isOffline) {
        if (banner) banner.classList.add('hidden');
        return;
    }

    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'self-offline-banner';
        banner.className = 'disconnect-banner';
        document.body.appendChild(banner);
    }

    banner.innerText = "⚠️ Your connection dropped. Attempting to reconnect...";
    banner.classList.remove('hidden');
}
