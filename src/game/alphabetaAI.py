import random
import time
from game.base_ai import BaseAI

class AlphaBetaAI(BaseAI):
    def __init__(self, depth=3, time_limit=None):
        self.depth = depth
        self.time_limit = time_limit
        self.start_time = 0
        self.node_count = 0 
        self.last_stats = {'depth': 0, 'time': 0}

    # --- MOVE ORDERING (Tidak Berubah) ---
    def _order_moves(self, board, valid_moves):
        corners = {(0,0), (0,7), (7,0), (7,7)}
        def score_move_ordering(move):
            r, c = move
            if (r, c) in corners: return 1000
            if r == 0 or r == 7 or c == 0 or c == 7: return 10
            return 0
        return sorted(valid_moves, key=score_move_ordering, reverse=True)

    def get_move(self, board, player):
        valid_moves = board.get_valid_moves(player)
        if not valid_moves:
            return None
            
        self.start_time = time.time()
        self.node_count = 0 

        if len(valid_moves) == 1:
            self.last_stats = {'depth': 0, 'time': time.time() - self.start_time}
            return valid_moves[0]

        best_move_final = valid_moves[0]
        completed_depth = 0
        
        # --- [UPDATE 1] LOGIKA PAKSA GENAP ---
        # Jika pakai time_limit, mulai dari depth 2 dan lompat 2 (2, 4, 6, ...)
        # Jika fixed depth, gunakan depth yang diminta user.
        if self.time_limit:
            start_depth = 2 
            step = 2
        else:
            start_depth = self.depth
            step = 1 # Tidak looping jika fixed, atau loop normal

        max_depth_to_search = self.depth if not self.time_limit else 64 # Max board size

        try:
            # Loop dengan step (bisa 1 atau 2)
            for d in range(start_depth, max_depth_to_search + 1, step):
                best_score = float('-inf')
                best_moves = []
                alpha = float('-inf')
                beta = float('inf')

                ordered_moves = self._order_moves(board, valid_moves)

                for move in ordered_moves:
                    self.node_count += 1
                    if self.time_limit and (self.node_count % 1000 == 0):
                        if time.time() - self.start_time >= self.time_limit:
                            raise TimeoutError("Time Limit Exceeded")

                    test_board = self._copy_board(board)
                    if test_board.make_move(move[0], move[1], player):
                        # Panggil alphabeta
                        score = self._alphabeta(test_board, d - 1, alpha, beta, False, player)
                        
                        if score > best_score:
                            best_score = score
                            best_moves = [move]
                        elif score == best_score:
                            best_moves.append(move)
                        
                        alpha = max(alpha, best_score)

                if best_moves:
                    best_move_final = random.choice(best_moves)
                    completed_depth = d 

        except TimeoutError:
            pass # Kembalikan hasil dari depth genap terakhir yang selesai

        elapsed_time = time.time() - self.start_time
        self.last_stats = {'depth': completed_depth, 'time': elapsed_time}

        return best_move_final

    # ... (Method _alphabeta TIDAK PERLU DIUBAH, biarkan sama seperti file asli) ...
    def _alphabeta(self, board, depth, alpha, beta, is_maximizing, player):
        # Gunakan kode _alphabeta yang sama persis dari file Anda sebelumnya
        self.node_count += 1
        if self.time_limit and (self.node_count % 1000 == 0):
            if time.time() - self.start_time >= self.time_limit:
                raise TimeoutError("Time Limit")

        if depth == 0 or board.is_game_over():
            return self._evaluate_board_advanced(board, player)

        opponent = 'W' if player == 'B' else 'B'
        current_player = player if is_maximizing else opponent
        valid_moves = board.get_valid_moves(current_player)

        if not valid_moves:
            return self._alphabeta(board, depth - 1, alpha, beta, not is_maximizing, player)

        ordered_moves = self._order_moves(board, valid_moves)

        if is_maximizing:
            value = float('-inf')
            for move in ordered_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move[0], move[1], current_player)
                score = self._alphabeta(test_board, depth - 1, alpha, beta, False, player)
                value = max(value, score)
                alpha = max(alpha, value)
                if beta <= alpha: break 
            return value
        else:
            value = float('inf')
            for move in ordered_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move[0], move[1], current_player)
                score = self._alphabeta(test_board, depth - 1, alpha, beta, True, player)
                value = min(value, score)
                beta = min(beta, value)
                if beta <= alpha: break 
            return value