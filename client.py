import socketio

# 1. CONNECT TO YOUR RENDER SERVER
# Replace this URL with the exact live URL Render gave you!
RENDER_URL = "https://onrender.com"

sio = socketio.Client()

print("Connecting to Chequers Server...")
try:
    sio.connect(RENDER_URL)
    print("Connected successfully!")
except Exception as e:
    print(f"Connection failed: {e}")
    exit()

# 2. MATCHMAKING
game_code = input("Enter a Game Code to join or create a match: ").strip()
player_color = input("Are you playing as Red (R) or White (W)? ").upper().strip()

# Tell the server we are joining this room
sio.emit('join_match', {'game_code': game_code})

# 3. INTERNET EVENTS (Listening to the server)
@sio.on('board_update')
def on_board_update(data):
    board_data = data['board']
    current_turn = data['turn']
    
    # This prints out the board received over the internet
    print("\n" * 2)
    print("  A B C D E F G H")
    for i, row in enumerate(board_data):
        print(f"{8-i} " + " ".join(row))
        
    print(f"\nCurrent Turn: {current_turn}")
    
    # If it is your turn, ask for moves and send them back to Render
    if current_turn == player_color:
        print("\n--- YOUR TURN ---")
        pos = input("Which counter do you want to move? (e.g., B3): ").upper().strip()
        new_pos = input("Where do you want to move it to? (e.g., A4): ").upper().strip()
        
        # Simple local conversion of letters to board grid coordinates
        try:
            c = "ABCDEFGH".find(pos[0])
            r = 8 - int(pos[1])
            nc = "ABCDEFGH".find(new_pos[0])
            nr = 8 - int(new_pos[1])
            
            # Send the coordinates up to your Render server!
            sio.emit('submit_move', {
                'game_code': game_code,
                'player_color': player_color,
                'r': r, 'c': c, 'nr': nr, 'nc': nc
            })
        except Exception:
            print("Invalid input format. Wait for the board to refresh and try again.")

@sio.on('error_message')
def on_error(data):
    print(f"\nError: {data['message']}")
    # Trigger a refresh query so the player can re-enter their move
    sio.emit('join_match', {'game_code': game_code})

# Keep the client program running to listen for moves
sio.wait()
