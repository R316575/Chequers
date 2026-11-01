class CheckersEngine:
    def __init__(self):
        self.board = [[" " for _ in range(8)] for _ in range(8)]
        self.w_score = 0
        self.r_score = 0
        self.current_turn = "R"
        self.game_status = "active"
        self.initialise_board()

    def initialise_board(self):
        for x in range(8):
            for y in range(8):
                if (x + y) % 2 == 1:
                    if x < 3:
                        self.board[x][y] = "w"
                    elif x > 4:
                        self.board[x][y] = "r"

    def get_valid_moves(self, player_color):
        """Calculates legal moves to support the frontend Hints Toggle Feature."""
        valid_moves = {}
        forced_capture_exists = self.check_forced_capture_global(player_color)
        
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if (player_color == "R" and piece in ["r", "R"]) or (player_color == "W" and piece in ["w", "W"]):
                    moves_for_piece = self.get_piece_moves(r, c, forced_capture_exists)
                    if moves_for_piece:
                        valid_moves[f"{r},{c}"] = moves_for_piece
        return valid_moves

    def check_forced_capture_global(self, player):
        # Loops board to check if any piece has an immediate jump setup
        # Re-engineered from your base movements logic to scan ahead cleanly
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if (player == "R" and piece in ["r", "R"]) or (player == "W" and piece in ["w", "W"]):
                    if self.get_piece_jumps(r, c):
                        return True
        return False

    def get_piece_moves(self, r, c, forced_only):
        jumps = self.get_piece_jumps(r, c)
        if jumps:
            return jumps
        if forced_only:
            return []
        
        steps = []
        piece = self.board[r][c]
        dirs = []
        if piece == "r": dirs = [(-1, -1), (-1, 1)]
        elif piece == "w": dirs = [(1, -1), (1, 1)]
        elif piece in ["R", "W"]: dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and self.board[nr][nc] == " ":
                steps.append({"nr": nr, "nc": nc, "is_capture": False})
        return steps

    def get_piece_jumps(self, r, c):
        jumps = []
        piece = self.board[r][c]
        dirs = []
        opponents = ["w", "W"] if piece in ["r", "R"] else ["r", "R"]
        
        if piece == "r": dirs = [(-1, -1), (-1, 1)]
        elif piece == "w": dirs = [(1, -1), (1, 1)]
        elif piece in ["R", "W"]: dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in dirs:
            target_r, target_c = r + dr, c + dc
            landing_r, landing_c = r + (dr * 2), c + (dc * 2)
            if 0 <= landing_r < 8 and 0 <= landing_c < 8:
                if self.board[target_r][target_c] in opponents and self.board[landing_r][landing_c] == " ":
                    jumps.append({"nr": landing_r, "nc": landing_c, "is_capture": True, "cap_r": target_r, "cap_c": target_c})
        return jumps

    def execute_move(self, r, c, nr, nc, player):
        if self.current_turn != player:
            return False, "Not your turn."
        
        forced = self.check_forced_capture_global(player)
        allowed_moves = self.get_piece_moves(r, c, forced)
        
        matched_move = next((m for m in allowed_moves if m["nr"] == nr and m["nc"] == nc), None)
        if not matched_move:
            return False, "Forced single captures apply! Move invalid." if forced else False, "Illegal trajectory path."

        # Process movement
        moving_piece = self.board[r][c]
        self.board[r][c] = " "
        
        if matched_move["is_capture"]:
            self.board[matched_move["cap_r"]][matched_move["cap_c"]] = " "
            if player == "R": self.r_score += 1
            else: self.w_score += 1

        # Check for Promotion to King
        if player == "R" and nr == 0: moving_piece = "R"
        elif player == "W" and nr == 7: moving_piece = "W"

        self.board[nr][nc] = moving_piece

        # State check routines
        next_player = "W" if player == "R" else "R"
        if self.r_score == 12 or self.w_score == 12:
            self.game_status = "finished"
        elif not self.get_valid_moves(next_player):
            self.game_status = "finished"
        else:
            self.current_turn = next_player

        return True, "Success"
