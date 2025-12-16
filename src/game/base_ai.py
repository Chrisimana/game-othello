from game.board import Board
from utils.constants import BOARD_WEIGHTS

class BaseAI:
    
    def _copy_board(self, board):
        # Optimasi copy board
        new_board = Board.__new__(Board)
        new_board.board = [row[:] for row in board.board]
        new_board.current_player = board.current_player
        return new_board

    def _get_game_phase(self, board):
        total_pieces = sum(1 for row in board.board for cell in row if cell is not None)
        if total_pieces < 20: return 'early'
        elif total_pieces < 45: return 'mid'
        else: return 'late'

    def _count_stable_pieces(self, board, player):
        stable = 0
        corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        for r, c in corners:
            if board.board[r][c] == player:
                stable += 1
                dx = 1 if c == 0 else -1
                for i in range(1, 7):
                    if 0 <= c + i*dx < 8 and board.board[r][c + i*dx] == player: stable += 1
                    else: break 
                dy = 1 if r == 0 else -1
                for i in range(1, 7):
                    if 0 <= r + i*dy < 8 and board.board[r + i*dy][c] == player: stable += 1
                    else: break
        return stable

    def _evaluate_board_advanced(self, board, player):
        # 1. CEK GAME OVER (Sudah Benar)
        if board.is_game_over():
            winner = board.get_winner()
            black_score, white_score = board.get_score()
            diff = abs(black_score - white_score)
            
            if winner == player:
                return 1000000 + diff 
            elif winner == 'D':
                return 0 
            else:
                return -1000000 - diff

        # 2. Heuristik Normal
        black_len, white_len = board.get_score()
        game_phase = self._get_game_phase(board) 
        
        # --- [TWEAK 1] POSITION SCORE (Tetap) ---
        position_score = 0
        for r in range(8):
            for c in range(8):
                if board.board[r][c] == player:
                    position_score += BOARD_WEIGHTS[r][c]
                elif board.board[r][c] is not None:
                    position_score -= BOARD_WEIGHTS[r][c]

        # --- [TWEAK 2] MOBILITY (Dinamis) ---
        my_moves = len(board.get_valid_moves(player))
        opponent = 'W' if player == 'B' else 'B'
        op_moves = len(board.get_valid_moves(opponent))
        
        # PERUBAHAN: Di Late Game, jangan terlalu peduli mobilitas
        if game_phase == 'late':
            mobility_weight = 2
        else:
            mobility_weight = 5 # Atau 10 untuk early/mid
            
        mobility_score = (my_moves - op_moves) * mobility_weight 

        # --- [TWEAK 3] COIN PARITY (Dinamis & Agresif) ---
        diff_coin = (black_len - white_len) if player == 'B' else (white_len - black_len)
        
        if game_phase == 'late':
            # PERUBAHAN BESAR: Naikkan multiplier dari 2 menjadi 50 atau 100
            # Agar bot mengejar jumlah koin terbanyak saat permainan mau habis
            coin_score = diff_coin * 50 
        elif game_phase == 'early':
            coin_score = -diff_coin # Evaporation strategy
        else:
            coin_score = 0 

        # --- [TWEAK 4] STABILITY (Tetap Tinggi) ---
        stable_count = self._count_stable_pieces(board, player)
        op_stable_count = self._count_stable_pieces(board, opponent)
        stability_score = (stable_count - op_stable_count) * 200

        return position_score + mobility_score + coin_score + stability_score