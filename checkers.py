class multiplayer:
    def __init__(self):
        self.active_games = []

    def join_game(self):
        pass

    def create_game(self):
        pass

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

    def handle_turn(self, position, new_position):
        pass

    def switch_turn(self, current_turn, players):
        if self.current_turn == "R":
            self.current_turn = "W"
        else:
            self.current_turn = "R"

    def check_winner(self, w_score, r_score):
        if self.board.w_score == 12:
            print("Game over. White wins.")
            return True, "White wins"
        elif self.board.r_score == 12:
            print("Game over. Red wins")
            return True, "Red wins"
        return False, ""

    def game_over(self):
        pass

    def check_no_possible_moves_white(self, board_obj):
        # Uses the passed object context cleanly
        for col in range (2,6):
           for row in range (0,6):
                if board_obj.board[row][col] in "Ww":
                    if board_obj.board[row+1][col+1] in "Rr" and board_obj.board[row+2][col+2] == " ":
                        return
                    if board_obj.board[row+1][col-1] in "Rr" and board_obj.board[row+2][col-2] == " ":
                        return
        for col in range (0,2):
            for row in range (0,6):
                if board_obj.board[row][col] in "Ww":
                    if board_obj.board[row+1][col+1] in "Rr" and board_obj.board[row+2][col+2] == " ":
                        return
        for col in range (6,8):
            for row in range (0,6):
                if board_obj.board[row][col] in "Ww":
                    if board_obj.board[row+1][col-1] in "Rr" and board_obj.board[row+2][col-2] == " ":
                        return
        # Complete fallback catch block
        return

    def check_no_possible_moves_red(self, board_obj):
        for col in range (2,6):
            for row in range (2,8):
                if board_obj.board[row][col] in "Rr":
                    if board_obj.board[row-1][col+1] in "Ww" and board_obj.board[row-2][col+2] == " ":
                        return
                    if board_obj.board[row-1][col-1] in "Ww" and board_obj.board[row-2][col-2] == " ":
                        return
        return

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
                    self.board[x][1] = "w"
                    self.board[x][3] = "w"
                    self.board[x][5] = "w"
                    self.board[x][7] = "w"
                elif x > 4:  
                    self.board[x][1] = "r"
                    self.board[x][3] = "r"
                    self.board[x][5] = "r"
                    self.board[x][7] = "r"
            else:  
                if x < 3:  
                    self.board[x][0] = "w"
                    self.board[x][2] = "w"
                    self.board[x][4] = "w"
                    self.board[x][6] = "w"
                elif x > 4:  
                    self.board[x][0] = "r"
                    self.board[x][2] = "r"
                    self.board[x][4] = "r"
                    self.board[x][6] = "r"

    def move_piece(self, r, c, nr, nc, player, game_instance):
        if self.board[r][c] == " ":
            return False, "There is no piece here."
        elif self.board[r][c] not in "Rr" and player == "R":
            return False, "That is not your piece."
        elif self.board[r][c] not in "Ww" and player == "W":
            return False, "That is not your piece."

        # Instantiate piece utility object locally to execute calculation safely
        p = piece()
        return p.movements(self, r, c, nr, nc, player, game_instance)

class piece:
    def __init__(self):
        self.colour = "colour" 
        self.position = "position" 

    def movements(self, board, r, c, nr, nc, player, game_instance):
        forced_capture = False
        
        if player == "R":
            if board.board[r][c] == "r": 
                if ((r - nr) == 1) and (((nc - c) == 1) or ((c - nc) == 1)): 
                    board.board[nr][nc] = board.board[r][c]
                    board.board[r][c] = " "
                    if nr == 0:
                        board.board[nr][nc] = "R"
                    game_instance.switch_turn(game_instance.current_turn, game_instance.players)
                    return True, "Move Complete"
                    
                elif ((r - nr) == 2) and ((nc - c) == 2): 
                    if board.board[r-1][nc-1] in "wW":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "                        
                        board.board[r-1][nc-1] = " "
                        board.r_score += 1
                        if nr == 0:
                            board.board[nr][nc] = "R"
                        game_instance.switch_turn(game_instance.current_turn, game_instance.players)
                        return True, "Capture Complete"
                        
                elif ((r - nr) == 2) and ((c - nc) == 2): 
                    if board.board[r-1][c-1] in "wW":                        
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r-1][c-1] = " "
                        board.r_score += 1
                        if nr == 0:
                            board.board[nr][nc] = "R"
                        game_instance.switch_turn(game_instance.current_turn, game_instance.players)
                        return True, "Capture Complete"
            
            elif board.board[r][c] == "R":
                kp = king_piece()
                return kp.movements_extra(board, r, c, nr, nc, player, game_instance)
                
        else: # White player logic tracking
            if board.board[r][c] == "w": 
                if ((nr - r) == 1) and (((nc - c) == 1) or ((c - nc) == 1)): 
                    board.board[nr][nc] = board.board[r][c]
                    board.board[r][c] = " "
                    if nr == 7:
                        board.board[nr][nc] = "W"
                    game_instance.switch_turn(game_instance.current_turn, game_instance.players)
                    return True, "Move Complete"
                    
                elif ((nr - r) == 2) and ((nc - c) == 2): 
                    if board.board[nr-1][nc-1] in "rR":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[nr-1][nc-1] = " "
                        board.w_score += 1
                        if nr == 7:
                            board.board[nr][nc] = "W"
                        game_instance.switch_turn(game_instance.current_turn, game_instance.players)
                        return True, "Capture Complete"
                        
                elif ((nr - r) == 2) and ((c - nc) == 2):
                    if board.board[r+1][c-1] in "rR":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r+1][c-1] = " "
                        board.w_score += 1
                        if nr == 7:
                            board.board[nr][nc] = "W"
                        game_instance.switch_turn(game_instance.current_turn, game_instance.players)
                        return True, "Capture Complete"
            
            elif board.board[r][c] == "W":
                kp = king_piece()
                return kp.movements_extra(board, r, c, nr, nc, player, game_instance)
                
        return False, "Invalid move target coordinates choice."

class king_piece(piece):
    def movements_extra(self, board, r, c, nr, nc, player, game_instance):
        # King pieces movement logic safely handling structural updates
        if (((abs(r-nr) == 1) and (abs(c-nc) == 1))):
            board.board[nr][nc] = board.board[r][c]
            board.board[r][c] = " "
            game_instance.switch_turn(game_instance.current_turn, game_instance.players)
            return True, "King Move Complete"
        return False, "Invalid King placement setup target chosen."
