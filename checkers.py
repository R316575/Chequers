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
        # redundant
        pass

    def switch_turn(self, current_turn, players):
        if self.current_turn == "R":
            self.current_turn = "W"
        else:
            self.current_turn = "R"

    def check_winner(self, w_score, r_score):
        if board.w_score == 12:
            print()
            board.display_board()
            print("Game over. White wins.")
            game.game_over()
        elif board.r_score == 12:
            print()
            board.display_board()
            print("Game over. Red wins")
            game.game_over()
        else:
            pass

    def game_over(self):
        exit()

    def check_no_possible_moves_white(self, board):
        for col in range (2,6):
           for row in range (0,6):
                if board.board[row][col] in "Ww":
                    if board.board[row+1][col+1] in "Rr" and board.board[row+2][col+2] == " ":
                        return
                    if board.board[row+1][col-1] in "Rr" and board.board[row+2][col-2] == " ":
                        return
        for col in range (0,2):
            for row in range (0,6):
                if board.board[row][col] in "Ww":
                    if board.board[row+1][col+1] in "Rr" and board.board[row+2][col+2] == " ":
                        return
        for col in range (6,8):
            for row in range (0,6):
                if board.board[row][col] in "Ww":
                    if board.board[row+1][col-1] in "Rr" and board.board[row+2][col-2] == " ":
                        return
        for col in range (2,6):
            for row in range (2,8):
                if board.board[row][col] == "W":
                    if board.board[row-1][col+1] in "Rr" and board.board[row-2][col+2] == " ":
                        return
                    if board.board[row-1][col-1] in "Rr" and board.board[row-2][col-2] == " ":
                        return
        for col in range (0,2):
            for row in range (2,8):
                if board.board[row][col] == "W":
                    if board.board[row-1][col+1] in "Rr" and board.board[row-2][col+2] == " ":
                        return
        for col in range (6,8):
            for row in range (2,8):
                if board.board[row][col] == "W":
                    if board.board[row-1][col-1] in "Rr" and board.board[row-2][col-2] == " ":
                        return

        for col in range (1,7):
            for row in range (0,7):
                if board.board[row][col] in "Ww" and (board.board[row+1][col+1] == " " or board.board[row+1][col-1] == " "):
                    return
        for col in range (1,7):
            for row in range (1,8):
                if board.board[row][col] == "W" and (board.board[row-1][col+1] == " " or board.board[row-1][col-1] == " "):
                    return
        for row in range (0,7):
            if board.board[row][0] in "Ww" and board.board[row+1][1] == " ":
                return
            if board.board[row][7] in "Ww" and board.board[row+1][6] == " ":
                return
        for row in range (1,8):
            if board.board[row][0] == "W" and board.board[row-1][1] == " ":
                return
            if board.board[row][7] == "W" and board.board[row-1][6] == " ":
                return

        print()
        board.display_board()
        print("White can no longer make a move.")
        print("Game over!")
        game.game_over()

    def check_no_possible_moves_red(self, board):
        for col in range (2,6):
            for row in range (2,8):
                if board.board[row][col] in "Rr":
                    if board.board[row-1][col+1] in "Ww" and board.board[row-2][col+2] == " ":
                        return
                    if board.board[row-1][col-1] in "Ww" and board.board[row-2][col-2] == " ":
                        return
        for col in range (0,2):
            for row in range (2,8):
                if board.board[row][col] in "Rr":
                    if board.board[row-1][col+1] in "Ww" and board.board[row-2][col+2] == " ":
                        return
        for col in range (6,8):
            for row in range (2,8):
                if board.board[row][col] in "Rr":
                    if board.board[row-1][col-1] in "Ww" and board.board[row-2][col-2] == " ":
                        return
        for col in range (2,6):
            for row in range (0,6):
                if board.board[row][col] == "R":
                    if board.board[row+1][col+1] in "Ww" and board.board[row+2][col+2] == " ":
                        return
                    if board.board[row+1][col-1] in "Ww" and board.board[row+2][col-2] == " ":
                        return
        for col in range (0,2):
            for row in range (0,6):
                if board.board[row][col] == "R":
                    if board.board[row+1][col+1] in "Ww" and board.board[row+2][col+2] == " ":
                        return
        for col in range (6,8):
            for row in range (0,6):
                if board.board[row][col] == "R":
                    if board.board[row+1][col-1] in "Ww" and board.board[row+2][col-2] == " ":
                        return
                    
        for col in range (1,7):
            for row in range (1,8):
                if board.board[row][col] in "Rr" and (board.board[row-1][col+1] == " " or board.board[row-1][col-1] == " "):
                    return
        for col in range (1,7):
            for row in range (0,7):
                if board.board[row][col] == "R" and (board.board[row+1][col+1] == " " or board.board[row+1][col-1] == " "):
                    return
        for row in range (1,8):
            if board.board[row][0] in "Rr" and board.board[row-1][1] == " ":
                return
            if board.board[row][7] in "Rr" and board.board[row-1][6] == " ":
                return
        for row in range (0,7):
            if board.board[row][0] == "R" and board.board[row+1][1] == " ":
                return
            if board.board[row][7] == "R" and board.board[row+1][6] == " ":
                return
                
        print()
        board.display_board()
        print("Red can no longer make a move.")
        print("Game over!")
        game.game_over()

##class player:
##    def __init__(self):
##        self.player_id = "player id" # is this actually needed
##        self.username = "username"
##        self.colour = "colour" # is this actually needed
##
##    def take_turn(self, game, board):
##        turn_complete = False
##        while not turn_complete:
##            x=0
##            position = input(f"{game.current_turn}, which counter do you want to move? ").upper()
##            new_position = input("Where do you want to move it to? ").upper()

##            if position == "Q" or new_position == "Q":
##                print("Game over!")
##                game.game_over()

##            if len(position) != 2 or len(new_position) != 2:
##                print("Invalid input. Please use the format 'A1'. Or enter values in the right range.")
##                x += 1

##            if position[1] not in "12345678" or new_position[1] not in "12345678":
##                print("Invalid input. Please only use row numbers 1 through 8.")
##                x += 1

##            if position[0] not in "ABCDEFGH" or new_position[0] not in "ABCDEFGH":
##                print("Invalid input. Please only use column letters A through H.")
##                x += 1
##            c = "ABCDEFGH".find(position[0])
##            r = 8 - int(position[1])
##            nc = "ABCDEFGH".find(new_position[0])
##            nr = 8 - int(new_position[1])

##            if c == -1 or nc == -1 or r < 0 or r > 7 or nr < 0 or nr > 7:
##                print("Invalid move. Please ensure the positions are valid.")
##                x += 1

##            if nc==c and r==nr:
##                print("Invalid, please move a piece.")
##                x += 1

##            if x != 0:
##                continue
##            else:
##                turn_complete = board.move_piece(r, c, nr, nc, game.current_turn)

##    def request_extra_time(self):
##        pass

class board:
    def __init__(self):
        self.board = []
        self.w_score = 0  # White score
        self.r_score = 0  # Red score

    def initialise_board(self):
        self.board = [[" " for _ in range(8)] for _ in range(8)]
        for x in range(8):
            if (x % 2) == 0:  # For even rows
                if x < 3:  # Player 1 pieces
                    self.board[x][1] = "w"
                    self.board[x][3] = "w"
                    self.board[x][5] = "w"
                    self.board[x][7] = "w"
                elif x > 4:  # Player 2 pieces
                    self.board[x][1] = "r"
                    self.board[x][3] = "r"
                    self.board[x][5] = "r"
                    self.board[x][7] = "r"
            else:  # For odd rows
                if x < 3:  # Player 1 pieces
                    self.board[x][0] = "w"
                    self.board[x][2] = "w"
                    self.board[x][4] = "w"
                    self.board[x][6] = "w"
                elif x > 4:  # Player 2 pieces
                    self.board[x][0] = "r"
                    self.board[x][2] = "r"
                    self.board[x][4] = "r"
                    self.board[x][6] = "r"
        self.display_board()

    def display_board(self):
        print(self.w_score * "R")
        print("  A B C D E F G H")  # Column labels
        for i in range(8):
            number = str(8-i) + " "
            print(number, end=" ")  # Row numbers
            for j in range(8):
                print(self.board[i][j], end=" ")
            print()  # Newline for the next row
        print(self.r_score * "W")

    def move_piece(self, r, c, nr, nc, player):
        if self.board[r][c] == " ":
            return False, "There is no piece here."
        elif self.board[r][c] not in "Rr" and player == "R":
            return False, "That is not your piece."
        elif self.board[r][c] not in "Ww" and player == "W":
            return False, "That is not your piece."


        return piece.movements(self, r, c, nr, nc, player)

    def get_piece_at(self, position):
        # redundant
        pass

    def remove_piece(self, position):
        # redundant
        pass

class piece:
    def __init__(self):
        self.colour = "colour" # do i need thses
        self.position = "position" # do i need these

    def get_captured(self):
        # redundant
        pass

    def movements(self, board, r, c, nr, nc, player):
        if player == "R":
            forced_capture = False
            for col in range (2,6):
                for row in range (2,8):
                    if board.board[row][col] in "Rr": #any piece
                        if board.board[row-1][col+1] in "Ww" and board.board[row-2][col+2] == " ":
                            forced_capture = True
                        if board.board[row-1][col-1] in "Ww" and board.board[row-2][col-2] == " ":
                            forced_capture = True
            for col in range (0,2):
                for row in range (2,8):
                    if board.board[row][col] in "Rr": # any piece
                        if board.board[row-1][col+1] in "Ww" and board.board[row-2][col+2] == " ":
                            forced_capture = True
            for col in range (6,8):
                for row in range (2,8):
                    if board.board[row][col] in "Rr": # any piece
                        if board.board[row-1][col-1] in "Ww" and board.board[row-2][col-2] == " ":
                            forced_capture = True

            if board.board[r][c] == "r": # red not king
                if ((r -nr)==1) and ((((nc-c)==1) or ((c-nc)==1))) and forced_capture == False: #forward one move
                    board.board[nr][nc] = board.board[r][c]
                    board.board[r][c] = " "
                    if nr == 0:
                        board.board[nr][nc] = "R"
                    else:
                        pass
                    game.check_winner(board.w_score, board.r_score)
                    game.check_no_possible_moves_white(board)
                    board.display_board()
                    game.switch_turn(game.current_turn, game.players)
                    return True
                elif ((r-nr)==2) and ((nc-c)==2): #capture foward right
                    if board.board[r-1][nc-1] == "w" or board.board[r-1][nc-1] == "W":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "                        
                        board.board[r-1][nc-1] = " "
                        board.r_score += 1
                        if nr == 0:
                            board.board[nr][nc] = "R"
                        else:
                            pass
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_white(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                elif ((r-nr)==2) and ((c-nc)==2): #capture foward left
                    if board.board[r-1][c-1] == "w" or board.board[r-1][c-1] == "W":                        
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r-1][c-1] = " "
                        board.r_score += 1
                        if nr == 0:
                            board.board[nr][nc] = "R"
                        else:
                            pass
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_white(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                else:
                    if forced_capture == True:
                        print("Need to make a capture")
                    else:
                        print("Invalid move, White cannot move there.")
                    return False
            elif board.board[r][c] == "R":
                king_piece.movements_extra(board, r,c, nr, nc, player)
        else:
            forced_capture = False
            for col in range (2,6):
                for row in range (0,6):
                    if board.board[row][col] in "Ww":
                        if board.board[row+1][col+1] in "Rr" and board.board[row+2][col+2] == " ":
                            forced_capture = True
                        if board.board[row+1][col-1] in "Rr" and board.board[row+2][col-2] == " ":
                            forced_capture = True
            for col in range (0,2):
                for row in range (0,6):
                    if board.board[row][col] in "Ww":
                        if board.board[row+1][col+1] in "Rr" and board.board[row+2][col+2] == " ":
                            forced_capture = True
            for col in range (6,8):
                for row in range (0,6):
                    if board.board[row][col] in "Ww":
                        if board.board[row+1][col-1] in "Rr" and board.board[row+2][col-2] == " ":
                            forced_capture = True

            if board.board[r][c] == "w": # white not king:
                if ((nr-r)==1) and ((((nc-c)==1) or ((c-nc)==1))) and forced_capture == False: #forward one move
                    board.board[nr][nc] = board.board[r][c]
                    board.board[r][c] = " "
                    if nr == 7:
                        board.board[nr][nc] = "W"
                    else:
                        pass
                    game.check_winner(board.w_score, board.r_score)
                    game.check_no_possible_moves_red(board)
                    board.display_board()
                    game.switch_turn(game.current_turn, game.players)
                elif ((nr-r)==2) and ((nc-c)==2): #forward right capture
                    if board.board[nr-1][nc-1] == "r" or board.board[nr-1][nc-1] == "R":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[nr-1][nc-1] = " "
                        board.w_score += 1
                        if nr == 7:
                            board.board[nr][nc] = "W"
                        else:
                            pass
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_red(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                elif ((nr-r)==2) and ((c-nc)==2):
                    if board.board[r+1][c-1] == "r" or board.board[r+1][c-1] == "R":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r+1][c-1] = " "
                        board.w_score += 1
                        if nr == 7:
                            board.board[nr][nc] = "W"
                        else:
                            pass
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_red(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                else:
                    if forced_capture == True:
                        print("Need to make a capture")
                    else:
                        print("Invalid move, White cannot move there.")
                    return False
            elif board.board[r][c] == "W":
                            king_piece.movements_extra(board, r,c, nr, nc, player)
                        

    
class normal_piece (piece): # might be able to get rid of this all together
    def __init__(self):
        super().__init__()

    def become_king(self):
        # redundant
        pass


class king_piece (piece):
    def __init__(self):
        super().__init__()

    def movements_extra(self, board, r,c, nr, nc, player):
        if player == "R":
            for col in range (2,6):
                for row in range (0,6):
                    if board.board[row][col] == "R": # king only
                        if board.board[row+1][col+1] in "Ww" and board.board[row+2][col+2] == " ":
                            forced_capture = True
                        if board.board[row+1][col-1] in "Ww" and board.board[row+2][col-2] == " ":
                            forced_capture = True
            for col in range (0,2):
                for row in range (0,6):
                    if board.board[row][col] == "R": # king only
                        if board.board[row+1][col+1] in "Ww" and board.board[row+2][col+2] == " ":
                            forced_capture = True
            for col in range (6,8):
                for row in range (0,6):
                    if board.board[row][col] == "R": # king only
                        if board.board[row+1][col-1] in "Ww" and board.board[row+2][col-2] == " ":
                            forced_capture = True

            if board.board[r][c] == "R": # red king
                if (((r-nr)==1) and ((((nc-c)==1) or ((c-nc)==1))) or (((nr-r==1) and (((c-nc)==1) or (nc-c)==1)))) and forced_capture == False:
                    board.board[nr][nc] = board.board[r][c]
                    board.board[r][c] = " "
                    game.check_winner(board.w_score, board.r_score)
                    game.check_no_possible_moves_white(board)
                    board.display_board()
                    game.switch_turn(game.current_turn, game.players)
                    return True
                elif ((r-nr)==2) and ((c-nc)==2): #capture foward left
                    if board.board[r-1][c-1] == "w" or board.board[r-1][c-1] == "W":                        
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r-1][c-1] = " "
                        board.r_score += 1
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_white(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                elif ((nr-r)==2) and ((nc-c)==2): #capture forward right
                    if board.board[nr-1][nc-1] == "w" or board.board[nr-1][nc-1] == "W":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[nr-1][nc-1] = " "
                        board.r_score += 1
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_white(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                elif ((nr-r)==2) and ((c-nc)==2): # capture backward left
                    if board.board[r+1][c-1] == "w" or board.board[r+1][c-1] == "W":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r+1][c-1] = " "
                        board.r_score += 1
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_white(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                elif ((nr-r)==2) and ((nc-c)==2): # capture backward right
                    if board.board[r+1][c+1] == "w" or board.board[r+1][c+1] == "W":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r+1][c+1] = " "
                        board.r_score += 1
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_white(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False 
                else:
                    if forced_capture == True:
                        print("Need to make a capture")
                    else:
                        print("Invalid move, White cannot move there.")
                    return False
        else:
            for col in range (2,6):
                for row in range (2,8):
                    if board.board[row][col] == "W":
                        if board.board[row-1][col+1] in "Rr" and board.board[row-2][col+2] == " ":
                            forced_capture = True
                        if board.board[row-1][col-1] in "Rr" and board.board[row-2][col-2] == " ":
                            forced_capture = True
            for col in range (0,2):
                for row in range (2,8):
                    if board.board[row][col] == "W":
                        if board.board[row-1][col+1] in "Rr" and board.board[row-2][col+2] == " ":
                            forced_capture = True
            for col in range (6,8):
                for row in range (2,8):
                    if board.board[row][col] == "W":                            
                        if board.board[row-1][col-1] in "Rr" and board.board[row-2][col-2] == " ":
                            forced_capture = True
            if board.board[r][c] == "W": #white king
                if (((r-nr)==1) and ((((nc-c)==1) or ((c-nc)==1))) or (((nr-r)==1) and (((c-nc)==1) or (nc-c)==1))) and forced_capture == False:
                    board.board[nr][nc] = board.board[r][c]
                    board.board[r][c] = " "
                    game.check_winner(board.w_score, board.r_score)
                    game.check_no_possible_moves_red(board)
                    board.display_board()
                    game.switch_turn(game.current_turn, game.players)
                elif ((r-nr)==2) and ((c-nc)==2): #capture foward left
                    if board.board[r-1][c-1] == "r" or board.board[r-1][c-1] == "R":                        
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r-1][c-1] = " "
                        board.r_score += 1
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_red(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                elif ((nr-r)==2) and ((nc-c)==2): #capture forward right
                    if board.board[nr-1][nc-1] == "r" or board.board[nr-1][nc-1] == "R":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[nr-1][nc-1] = " "
                        board.r_score += 1
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_red(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                elif ((nr-r)==2) and ((c-nc)==2): # capture backward left
                    if board.board[r+1][c-1] == "r" or board.board[r+1][c-1] == "R":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r+1][c-1] = " "
                        board.r_score += 1
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_red(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False
                elif ((nr-r)==2) and ((nc-c)==2): # capture backward right
                    if board.board[r+1][c+1] == "r" or board.board[r+1][c+1] == "R":
                        board.board[nr][nc] = board.board[r][c]
                        board.board[r][c] = " "
                        board.board[r+1][c+1] = " "
                        board.r_score += 1
                        game.check_winner(board.w_score, board.r_score)
                        game.check_no_possible_moves_red(board)
                        board.display_board()
                        game.switch_turn(game.current_turn, game.players)
                        return True
                    else:
                        print("Invalid move, capture cannot be made.")
                        return False 
                else:
                    if forced_capture == True:
                        print("Need to make a capture")
                    else:
                        print("Invalid move, White cannot move there.")
                    return False

#main program:
print("CHEQUERS")
multiplayer = multiplayer()
game = game()
##player = player()
board = board()
piece = piece()
normal_piece = normal_piece()
king_piece = king_piece()

moves = True
game.start_game()
##while moves == True:
##    player.take_turn(game, game.board)

# TO DO LIST: 
# multiplayer aspect: usernames, game code, two players in one game
# web page UI
# extra time request
# calculate valid moves: could recycle checks for logic use
# hints toggle
# client disconnections