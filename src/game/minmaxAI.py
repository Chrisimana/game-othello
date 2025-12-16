import random
import time
from game.base_ai import BaseAI

class MinimaxAI(BaseAI):
    def __init__(self, depth=3, time_limit=None):
        self.depth = depth
        self.time_limit = time_limit
        self.start_time = 0
        self.node_count = 0 
        self.last_stats = {'depth': 0, 'time': 0}

    def _order_moves(self, board, valid_moves):
        # Move ordering sederhana: Prioritaskan pojok
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
        
        # Jika hanya ada 1 langkah, langsung ambil (hemat waktu)
        if len(valid_moves) == 1:
            self.last_stats = {'depth': 0, 'time': time.time() - self.start_time}
            return valid_moves[0]

        best_move_final = valid_moves[0]
        completed_depth = 0
        
        # --- LOGIKA ITERATIVE DEEPENING (GENAP) ---
        # Jika pakai time_limit, kita mulai dari depth 2 dan lompat 2 (2, 4, 6...)
        # Agar evaluasi selalu berakhir di giliran Bot (Genap)
        if self.time_limit:
            start_depth = 2
            step = 2
            max_depth_to_search = 64 # Angka besar karena dibatasi waktu
        else:
            # Jika fixed depth, gunakan settingan user
            start_depth = self.depth
            step = 1 
            max_depth_to_search = self.depth

        try:
            for d in range(start_depth, max_depth_to_search + 1, step):
                best_score = float('-inf')
                best_moves = []
                
                # Urutkan langkah agar kemungkinan menemukan yang terbaik lebih cepat (meski Minimax tetap cek semua)
                ordered_moves = self._order_moves(board, valid_moves)

                for move in ordered_moves:
                    # Cek waktu setiap 1000 node
                    self.node_count += 1
                    if self.time_limit and (self.node_count % 1000 == 0):
                        if time.time() - self.start_time >= self.time_limit:
                            raise TimeoutError("Time Limit Exceeded")

                    test_board = self._copy_board(board)
                    if test_board.make_move(move[0], move[1], player):
                        # Panggil rekursi Minimax
                        score = self._minimax(test_board, d - 1, False, player)
                        
                        if score > best_score:
                            best_score = score
                            best_moves = [move]
                        elif score == best_score:
                            best_moves.append(move)

                # UPDATE SAFE: Hanya update best_move_final jika loop kedalaman ini SELESAI
                if best_moves:
                    best_move_final = random.choice(best_moves)
                    completed_depth = d

        except TimeoutError:
            pass # Waktu habis, abaikan hasil depth ini, pakai hasil depth sebelumnya
        
        elapsed_time = time.time() - self.start_time
        self.last_stats = {'depth': completed_depth, 'time': elapsed_time}

        return best_move_final

    def _minimax(self, board, depth, is_maximizing, player):
        # Cek waktu di dalam rekursi juga
        self.node_count += 1
        if self.time_limit and (self.node_count % 1000 == 0):
            if time.time() - self.start_time >= self.time_limit:
                raise TimeoutError("Time Limit")

        if depth == 0 or board.is_game_over():
            return self._evaluate_board_advanced(board, player)

        opponent = 'W' if player == 'B' else 'B'
        current_player = player if is_maximizing else opponent
        valid_moves = board.get_valid_moves(current_player)

        # Jika tidak ada langkah, pass giliran (depth dikurangi tapi maximizing di-flip)
        if not valid_moves:
            return self._minimax(board, depth - 1, not is_maximizing, player)

        ordered_moves = self._order_moves(board, valid_moves)

        if is_maximizing:
            best_score = float('-inf')
            for move in ordered_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move[0], move[1], current_player)
                score = self._minimax(test_board, depth - 1, False, player)
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = float('inf')
            for move in ordered_moves:
                test_board = self._copy_board(board)
                test_board.make_move(move[0], move[1], current_player)
                score = self._minimax(test_board, depth - 1, True, player)
                best_score = min(best_score, score)
            return best_score